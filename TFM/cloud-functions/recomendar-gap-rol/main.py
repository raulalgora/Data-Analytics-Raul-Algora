import functions_framework
from google.cloud import bigquery
import json
import numpy as np

# Inicializar el cliente de BigQuery. 
client = bigquery.Client(location="europe-southwest1") 

# --- Función auxiliar para obtener un embedding ---
def get_embedding_from_bq(table_name: str, id_column: str, id_value, id_type: str):
    """Obtiene un único vector de embedding de una tabla."""
    query = f"""
        SELECT embedding FROM `{table_name}`
        WHERE `{id_column}` = @id_value
        LIMIT 1
    """
    job_config = bigquery.QueryJobConfig(
        query_parameters=[bigquery.ScalarQueryParameter("id_value", id_type, id_value)]
    )
    # No envolvemos esto en try/except para que los errores de BQ se propaguen y se capturen en la función principal.
    query_job = client.query(query, job_config=job_config)
    results = list(query_job.result())
    if results:
        return np.array(results[0].embedding)
    return None

@functions_framework.http
def recommend_skill_gap_courses(request):
    """
    Endpoint HTTP que recomienda cursos para cerrar la brecha entre un empleado
    y un rol objetivo.
    """
    try:
        # 1. Validación de la entrada
        request_json = request.get_json(silent=True)
        if not request_json:
            return (json.dumps({"error": "Invalid JSON request body"}), 400, {'Content-Type': 'application/json'})

        employee_id_str = request_json.get('employee_id')
        target_role = request_json.get('target_role')

        if not employee_id_str or not target_role:
            return (json.dumps({"error": "Missing 'employee_id' or 'target_role' in request body"}), 400, {'Content-Type': 'application/json'})

        try:
            employee_id = int(employee_id_str)
        except (ValueError, TypeError):
            return (json.dumps({"error": "employee_id must be a valid integer"}), 400, {'Content-Type': 'application/json'})

        # 2. Obtener los vectores en Python
        employee_vector = get_embedding_from_bq(
            "tfm-caixabank.recomendation_system.empleados_procesados", 
            "ID", employee_id, "INT64"
        )
        target_role_vector = get_embedding_from_bq(
            "tfm-caixabank.recomendation_system.roles_procesados", 
            "Nombre", target_role, "STRING"
        )

        if employee_vector is None or target_role_vector is None:
            msg = "Could not find embedding for the specified employee or target role."
            return (json.dumps({"error": msg, "details": f"Employee found: {employee_vector is not None}, Role found: {target_role_vector is not None}"}), 404, {'Content-Type': 'application/json'})

        # 3. Calcular el vector de brecha en Python
        skill_gap_vector = target_role_vector - employee_vector

        # 4. Ejecutar una consulta VECTOR_SEARCH simple con el vector resultante
        sql_query = """
            SELECT
                base.`Training Title` AS course_title,
                base.`Training Object ID` AS course_id,
                base.descripcion_semantica AS course_description,
                1 - distance AS similarity
            FROM
                VECTOR_SEARCH(
                    TABLE `tfm-caixabank.recomendation_system.cursos_procesados`,
                    'embedding',
                    (SELECT @skill_gap_vector AS embedding),
                    query_column_to_search => 'embedding',
                    top_k => 10,
                    distance_type => 'COSINE'
                )
            ORDER BY similarity DESC
        """
        
        job_config = bigquery.QueryJobConfig(
            query_parameters=[
                bigquery.ArrayQueryParameter("skill_gap_vector", "FLOAT64", skill_gap_vector.tolist())
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
            output["message"] = "No courses found for the calculated skill gap."
        else:
            for row in recommendations:
                output["recommended_courses_for_skill_gap"].append({
                    "course_title": row.course_title,
                    "course_id": row.course_id,
                    "course_description": row.course_description,
                    "similarity_to_gap": round(row.similarity, 4)
                })
        
        return (json.dumps(output), 200, {'Content-Type': 'application/json'})

    except Exception as e:
        # Captura cualquier otro error durante el proceso y devuelve un error 500
        # Es útil loguear el error para depuración
        print(f"Internal Server Error: {e}") # Esto aparecerá en los logs de Cloud Run
        error_response = json.dumps({"error": "An internal server error occurred."})
        return (error_response, 500, {'Content-Type': 'application/json'})