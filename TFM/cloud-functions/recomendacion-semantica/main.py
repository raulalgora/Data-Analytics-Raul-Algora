import functions_framework
from google.cloud import bigquery
from vertexai.language_models import TextEmbeddingModel
import json
import numpy as np
import traceback

# --- INICIALIZACIÓN (se ejecuta una sola vez por instancia) ---
# Inicializar el cliente de BigQuery
client = bigquery.Client(location="europe-southwest1") # Reemplaza con tu región

# Cargar el modelo de embedding
try:
    embedding_model = TextEmbeddingModel.from_pretrained("text-embedding-004")
    print("Modelo de embedding cargado correctamente.")
except Exception as e:
    embedding_model = None
    print(f"ERROR FATAL: No se pudo cargar el modelo de embedding: {e}")

@functions_framework.http
def recommend_by_text(request):
    """
    Recomienda cursos basados en un texto y filtra por el nivel del empleado.
    """
    try:
        # 1. Validación de la entrada
        if embedding_model is None:
            raise RuntimeError("El modelo de embedding no está disponible.")

        request_json = request.get_json(silent=True)
        if not request_json or 'employee_id' not in request_json or 'query_text' not in request_json:
            return (json.dumps({"error": "Missing 'employee_id' or 'query_text'"}), 400, {'Content-Type': 'application/json'})

        employee_id = int(request_json['employee_id'])
        query_text = str(request_json['query_text'])

        if not query_text.strip():
            return (json.dumps({"error": "'query_text' cannot be empty"}), 400, {'Content-Type': 'application/json'})

        # 2. Obtener el perfil del empleado (nivel y descripción para el output)
        profile_query = """
            SELECT experience_level, descripcion_semantica
            FROM `tfm-caixabank.recomendation_system.empleados_procesados`
            WHERE ID = @employee_id LIMIT 1
        """
        profile_config = bigquery.QueryJobConfig(
            query_parameters=[bigquery.ScalarQueryParameter("employee_id", "INT64", employee_id)]
        )
        profile_results = list(client.query(profile_query, job_config=profile_config).result())

        if not profile_results or profile_results[0].experience_level is None:
            return (json.dumps({"error": "Employee not found or experience level is not set"}), 404, {'Content-Type': 'application/json'})
        
        employee_profile = profile_results[0]

        # 3. Generar embedding para el texto de consulta del usuario
        response = embedding_model.get_embeddings([query_text])
        query_embedding = response[0].values

        # 4. Ejecutar la búsqueda vectorial pre-filtrada en BigQuery
        search_query = """
            SELECT
                base.`Training Title` AS course_title,
                base.`Training Object ID` AS course_id,
                base.descripcion_semantica AS course_description,
                base.level_min AS course_level_min,
                base.level_max AS course_level_max,
                1 - distance AS similarity
            FROM
                VECTOR_SEARCH(
                    (
                        SELECT * FROM `tfm-caixabank.recomendation_system.cursos_procesados`
                        WHERE @employee_level BETWEEN level_min AND level_max
                        AND level_min IS NOT NULL
                    ),
                    'embedding',
                    (SELECT @query_embedding AS embedding),
                    query_column_to_search => 'embedding',
                    top_k => 10,
                    distance_type => 'COSINE'
                )
            ORDER BY similarity DESC
        """
        
        search_config = bigquery.QueryJobConfig(
            query_parameters=[
                bigquery.ScalarQueryParameter("employee_level", "INT64", employee_profile.experience_level),
                bigquery.ArrayQueryParameter("query_embedding", "FLOAT64", query_embedding)
            ]
        )
        
        search_results = list(client.query(search_query, job_config=search_config).result())

        # 5. Formatear y devolver la respuesta
        recommended_courses = [dict(row) for row in search_results]

        output = {
            "employee_id": employee_id,
            "employee_level": employee_profile.experience_level,
            "employee_description": employee_profile.descripcion_semantica,
            "query_text": query_text,
            "recommended_courses": recommended_courses
        }

        return (json.dumps(output, default=str), 200, {'Content-Type': 'application/json'})

    except Exception as e:
        print(f"Internal Server Error Traceback: {e}")
        traceback.print_exc()
        return (json.dumps({"error": "An internal server error occurred."}), 500, {'Content-Type': 'application/json'})