import functions_framework
from google.cloud import bigquery
import os
import json
import numpy as np

# Variables de entorno
PROJECT_ID = os.environ.get("PROJECT_ID", "tfm-caixabank")
BQ_DATASET = os.environ.get("BQ_DATASET", "recomendation_system")

# Inicializar el cliente de BigQuery.
# Se recomienda usar la ubicación del dataset para optimizar el rendimiento.
client = bigquery.Client(location="europe-southwest1")

# --- Función auxiliar para obtener un embedding ---
def get_employee_embedding(employee_id):
    query = """
        SELECT embedding, languages, experience_level FROM `tfm-caixabank.recomendation_system.empleados_procesados`
        WHERE ID = @id_value
        LIMIT 1
    """
    job_config = bigquery.QueryJobConfig(
        query_parameters=[bigquery.ScalarQueryParameter("id_value", "INT64", employee_id)]
    )
    query_job = client.query(query, job_config=job_config)
    results = list(query_job.result())
    if results:
        return {
            "embedding": np.array(results[0].embedding),
            "languages": results[0].languages,
            "experience_level": results[0].experience_level
        }
    return None

def get_role_embedding(role_name):
    query = """
        SELECT embedding, experience_level FROM `tfm-caixabank.recomendation_system.roles_procesados`
        WHERE Nombre = @id_value
        LIMIT 1
    """
    job_config = bigquery.QueryJobConfig(
        query_parameters=[bigquery.ScalarQueryParameter("id_value", "STRING", role_name)]
    )
    query_job = client.query(query, job_config=job_config)
    results = list(query_job.result())
    if results:
        return {
            "embedding": np.array(results[0].embedding),
            "experience_level": results[0].experience_level
        }
    return None

# --- Función auxiliar para la similitud coseno (si se necesita en Python) ---
def cosine_similarity(vec1, vec2):
    """Calcula la similitud coseno entre dos vectores."""
    dot_product = np.dot(vec1, vec2)
    norm_a = np.linalg.norm(vec1)
    norm_b = np.linalg.norm(vec2)
    if norm_a == 0 or norm_b == 0:
        return 0.0
    return dot_product / (norm_a * norm_b)


@functions_framework.http
def recommend_skill_gap_courses(request):
    """
    Endpoint HTTP que recomienda cursos para cerrar la brecha entre un empleado
    y un rol objetivo, utilizando el enfoque de "Gap Analysis".
    """
    try:
        # 1. Validación de la entrada
        request_json = request.get_json(silent=True)
        if not request_json:
            return (json.dumps({"error": "Invalid JSON request body"}), 400, {'Content-Type': 'application/json'})

        employee_id_str = request_json.get('employee_id')
        target_role = request_json.get('target_role')
        top_k = request_json.get('top_k', 10) # Número de recomendaciones, por defecto 10

        if not employee_id_str or not target_role:
            return (json.dumps({"error": "Missing 'employee_id' or 'target_role' in request body"}), 400, {'Content-Type': 'application/json'})

        try:
            employee_id = int(employee_id_str)
        except (ValueError, TypeError):
            return (json.dumps({"error": "employee_id must be a valid integer"}), 400, {'Content-Type': 'application/json'})
        
        if not isinstance(top_k, int) or top_k <= 0:
            return (json.dumps({"error": "top_k must be a positive integer"}), 400, {'Content-Type': 'application/json'})


        # 2. Obtener los vectores y atributos del empleado en Python
        employee_data = get_employee_embedding(employee_id)
        target_role_vector_data = get_role_embedding(target_role)

        if employee_data is None or target_role_vector_data is None:
            msg = "Could not find embedding for the specified employee or target role."
            return (json.dumps({"error": msg, "details": f"Employee found: {employee_data is not None}, Role found: {target_role_vector_data is not None}"}), 404, {'Content-Type': 'application/json'})

        employee_vector = employee_data["embedding"]
        employee_languages = employee_data["languages"]
        employee_exp_level = employee_data["experience_level"]
        target_role_vector = target_role_vector_data["embedding"]


        # 3. Calcular el vector de brecha en Python
        skill_gap_vector = target_role_vector - employee_vector


        # 4. Ejecutar una consulta VECTOR_SEARCH con el vector resultante y aplicar filtros
        # Usamos CTEs (Common Table Expressions) para aplicar filtros después de la búsqueda vectorial
        # y antes de la selección final para mantener el orden de distancia.
        sql_query = f"""
            SELECT
                course_title,
                course_id,
                course_description,
                language,
                level_min,
                level_max,
                similarity
            FROM
            (
                SELECT
                    base.`Training Title` AS course_title,
                    base.`Training Object ID` AS course_id,
                    base.descripcion_semantica AS course_description,
                    base.Language AS language,
                    base.level_min AS level_min,
                    base.level_max AS level_max,
                    1 - distance AS similarity
                FROM
                    VECTOR_SEARCH(
                        TABLE `tfm-caixabank.recomendation_system.cursos_procesados`,
                        'embedding',
                        (SELECT @skill_gap_vector AS embedding),
                        query_column_to_search => 'embedding',
                        top_k => {top_k * 5}, -- Buscar más para tener suficientes después del filtrado
                        distance_type => 'COSINE'
                    )
            ) AS recommended_raw
            WHERE
                -- Filtrado por idioma del empleado
                ARRAY_LENGTH(@employee_languages) = 0 OR recommended_raw.language IN UNNEST(@employee_languages)
                -- Filtrado por nivel de experiencia del curso vs empleado
                -- Permite cursos ligeramente superiores al nivel del empleado para desarrollo
                AND (
                    @employee_exp_level IS NULL OR
                    (recommended_raw.level_min IS NULL AND recommended_raw.level_max IS NULL) OR
                    (
                        recommended_raw.level_min IS NOT NULL AND recommended_raw.level_max IS NOT NULL AND
                        @employee_exp_level BETWEEN recommended_raw.level_min - 1 AND recommended_raw.level_max + 1
                        -- Ajusta el +/- 1 según cómo quieras de permisivo ser con el nivel
                    )
                    OR (
                        recommended_raw.level_min IS NOT NULL AND recommended_raw.level_max IS NULL AND
                        @employee_exp_level >= recommended_raw.level_min - 1
                    )
                    OR (
                        recommended_raw.level_min IS NULL AND recommended_raw.level_max IS NOT NULL AND
                        @employee_exp_level <= recommended_raw.level_max + 1
                    )
                )
            ORDER BY similarity DESC
            LIMIT {top_k}
        """

        job_config = bigquery.QueryJobConfig(
            query_parameters=[
                bigquery.ArrayQueryParameter("skill_gap_vector", "FLOAT64", skill_gap_vector.tolist()),
                bigquery.ArrayQueryParameter("employee_languages", "STRING", employee_languages),
                bigquery.ScalarQueryParameter("employee_exp_level", "INT64", employee_exp_level),
            ]
        )
        query_job = client.query(sql_query, job_config=job_config)
        results = query_job.result()

        # 5. Formatear y devolver la salida
        recommendations = list(results)

        output = {
            "employee_id": employee_id,
            "target_role": target_role,
            "recommended_courses_for_skill_gap": []
        }

        if not recommendations:
            output["message"] = "No courses found for the calculated skill gap after filtering."
        else:
            for row in recommendations:
                output["recommended_courses_for_skill_gap"].append({
                    "course_title": row.course_title,
                    "course_id": row.course_id,
                    "course_description": row.course_description,
                    "language": row.language,
                    "level_min": row.level_min,
                    "level_max": row.level_max,
                    "similarity_to_gap": round(row.similarity, 4)
                })

        return (json.dumps(output), 200, {'Content-Type': 'application/json'})

    except Exception as e:
        print(f"Internal Server Error: {e}")
        error_response = json.dumps({"error": f"An internal server error occurred: {str(e)}"})
        return (error_response, 500, {'Content-Type': 'application/json'})