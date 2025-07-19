import functions_framework
from google.cloud import bigquery
import json
import numpy as np
import pandas as pd
from scipy.spatial.distance import cosine
import traceback

# Initialize BigQuery client
client = bigquery.Client(location="europe-southwest1") 

@functions_framework.http
def find_similar_courses(request):
    """
    Endpoint que recomienda cursos. Acepta un parámetro opcional 'lambda'
    para controlar la exploración (diversidad) vs. explotación (relevancia).
    """
    try:
        # 1. Validación de la entrada
        request_json = request.get_json(silent=True)
        if not request_json or 'employee_id' not in request_json:
            return (json.dumps({"error": "Missing employee_id"}), 400, {'Content-Type': 'application/json'})

        employee_id = int(request_json['employee_id'])
        lambda_param = float(request_json.get('lambda', 0.0))
        if not (0.0 <= lambda_param <= 1.0):
            raise ValueError("lambda must be between 0.0 and 1.0")

        # 2. Construcción y Ejecución de la Consulta Única
        top_k_initial = 200 # Pedimos un pool grande para compensar los filtros

        sql_query = f"""
            WITH 
            EmployeeProfile AS (
                -- Primero, obtenemos el perfil completo del empleado en una CTE
                SELECT
                    e.ID,
                    e.embedding,
                    e.experience_level,
                    e.descripcion_semantica,
                    l.employee_langs
                FROM `tfm-caixabank.recomendation_system.empleados_procesados` AS e
                LEFT JOIN `tfm-caixabank.recomendation_system.empleados_idiomas` AS l ON e.ID = l.ID
                WHERE e.ID = @employee_id
            )
            -- Consulta principal
            SELECT
                -- Seleccionamos la información del empleado desde la CTE para tenerla en cada fila
                (SELECT ID FROM EmployeeProfile) AS employee_id,
                (SELECT descripcion_semantica FROM EmployeeProfile) AS employee_description,
                (SELECT experience_level FROM EmployeeProfile) AS employee_level,
                (SELECT employee_langs FROM EmployeeProfile) AS employee_languages,
                
                -- Seleccionamos la información de los cursos
                base.`Training Title` AS course_title,
                base.`Training Object ID` AS course_id,
                base.descripcion_semantica AS course_description,
                base.level_min AS course_level_min,
                base.level_max AS course_level_max,
                course_langs.course_langs AS course_languages,
                -- Añadimos la columna de embedding condicionalmente para el re-ranking
                {'base.embedding AS course_embedding,' if lambda_param > 0 else ''}
                1 - distance AS similarity
            FROM
                VECTOR_SEARCH(
                    -- Pre-filtramos los cursos por nivel, usando el nivel de la CTE
                    (
                        SELECT * FROM `tfm-caixabank.recomendation_system.cursos_procesados`
                        WHERE (SELECT experience_level FROM EmployeeProfile) BETWEEN level_min AND level_max
                        AND level_min IS NOT NULL
                    ),
                    'embedding',
                    -- La tabla de consulta es la propia CTE del empleado
                    TABLE EmployeeProfile,
                    query_column_to_search => 'embedding',
                    top_k => @top_k,
                    distance_type => 'COSINE'
                )
            -- Unimos con los idiomas del curso para obtenerlos y para filtrar
            JOIN `tfm-caixabank.recomendation_system.cursos_idiomas` AS course_langs
                ON base.`Training Object ID` = course_langs.`Training Object ID`
            -- Filtramos por idioma
            WHERE
                -- Si el empleado no tiene idiomas, se aceptan todos los cursos
                ARRAY_LENGTH((SELECT employee_langs FROM EmployeeProfile)) = 0 OR
                -- Si tiene, se busca coincidencia
                (SELECT COUNT(1) FROM UNNEST(course_langs.course_langs) AS lang 
                 WHERE lang IN UNNEST((SELECT employee_langs FROM EmployeeProfile))) > 0
            ORDER BY similarity DESC;
        """

        # El único parámetro que la consulta SQL necesita ahora es el ID del empleado y el top_k
        query_config = bigquery.QueryJobConfig(
            query_parameters=[
                bigquery.ScalarQueryParameter("employee_id", "INT64", employee_id),
                bigquery.ScalarQueryParameter("top_k", "INT64", top_k_initial)
            ]
        )
        
        query_job = client.query(sql_query, job_config=query_config)
        results_df = pd.DataFrame([dict(row) for row in query_job.result()])

        # 3. Procesamiento y Formateo de Resultados
        if results_df.empty:
            # No podemos obtener el perfil si no hay resultados, así que lo buscamos si es necesario
            profile_query = "SELECT descripcion_semantica, experience_level, employee_langs FROM EmployeeProfile"
            # (En una implementación real, se podría manejar esto de forma más elegante)
            return (json.dumps({
                "employee_id": employee_id,
                "message": "No suitable courses found for the employee's level and language.",
                "recommended_courses": []
            }), 200, {'Content-Type': 'application/json'})

        FINAL_RECOMMENDATION_COUNT = 10

        if lambda_param > 0:
            final_courses = re_rank_with_mmr(results_df, lambda_param, top_k=FINAL_RECOMMENDATION_COUNT)
        else: # lambda = 0.0
            final_courses = []
            for _, row in results_df.head(FINAL_RECOMMENDATION_COUNT).iterrows():
                final_courses.append({
                    "course_title": row['course_title'],
                    "course_id": row['course_id'],
                    "course_description": row['course_description'],
                    "course_languages": row['course_languages'],
                    "course_level_min": row['course_level_min'],
                    "course_level_max": row['course_level_max'],
                    "similarity": round(row['similarity'], 4)
                })

        # 4. Construcción de la Salida Final
        first_row = results_df.iloc[0]
        output = {
            "employee_id": int(first_row.employee_id),
            "employee_description": str(first_row.employee_description),
            "employee_level": int(first_row.employee_level),
            "employee_languages": first_row.employee_languages,
            "lambda_parameter_used": float(lambda_param),
            "recommended_courses": final_courses
        }

        return (json.dumps(output, default=str), 200, {'Content-Type': 'application/json'})

    except Exception as e:
        print(f"Internal Server Error Traceback: {e}")
        traceback.print_exc()
        error_response = json.dumps({"error": "An internal server error occurred."})
        return (error_response, 500, {'Content-Type': 'application/json'})


def re_rank_with_mmr(candidates_df: pd.DataFrame, lambda_param: float, top_k: int):
    # (El código de esta función no necesita cambios, solo su formateo de salida)
    candidates_df = candidates_df.dropna(subset=['course_embedding', 'similarity'])
    if candidates_df.empty:
        return []
    
    try:
        embeddings = np.stack(candidates_df['course_embedding'].values)
    except ValueError as e:
        print(f"Error al apilar embeddings: {e}")
        return []

    original_similarities = candidates_df['similarity'].values
    original_indices = candidates_df.index.tolist()
    selected_indices = []
    
    if not original_indices:
        return []

    first_rec_iloc = np.argmax(original_similarities)
    first_rec_index = original_indices.pop(first_rec_iloc)
    selected_indices.append(first_rec_index)
    
    while len(selected_indices) < min(top_k, len(candidates_df)) and original_indices:
        best_candidate_index = -1
        max_mmr_score = -np.inf
        for cand_index in original_indices:
            cand_iloc = candidates_df.index.get_loc(cand_index)
            relevance_score = original_similarities[cand_iloc]
            
            selected_ilocs = [candidates_df.index.get_loc(idx) for idx in selected_indices]
            sim_values = [1 - cosine(embeddings[cand_iloc], embeddings[sel_iloc]) for sel_iloc in selected_ilocs]
            max_sim_with_selected = max(sim_values) if sim_values else 0
            
            mmr_score = (1 - lambda_param) * relevance_score - lambda_param * max_sim_with_selected
            
            if mmr_score > max_mmr_score:
                max_mmr_score = mmr_score
                best_candidate_index = cand_index
        
        if best_candidate_index != -1:
            selected_indices.append(best_candidate_index)
            original_indices.remove(best_candidate_index)
        else:
            break
            
    final_df = candidates_df.loc[selected_indices]
    output_list = []
    for _, row in final_df.iterrows():
        output_list.append({
            "course_title": row['course_title'],
            "course_id": row['course_id'],
            "course_description": row['course_description'],
            "course_languages": row['course_languages'],
            "course_level_min": row['course_level_min'],
            "course_level_max": row['course_level_max'],
            "original_similarity": round(row['similarity'], 4),
            "reranked": True
        })
    return output_list