import datetime
import uuid
import logging
import google.cloud.logging
from google.cloud.logging.handlers import CloudLoggingHandler
from google.cloud import storage, bigquery
from config import PROJECT_ID, BUCKET_NAME, BQ_DATASET, BQ_EMPLEADOS_TABLE, BQ_IDIOMAS_TABLE
import functions_framework
import json

client = google.cloud.logging.Client()
handler = CloudLoggingHandler(client)
logging.getLogger().setLevel(logging.INFO)
logging.getLogger().addHandler(handler)

@functions_framework.http
def upload_cv(request):
    try:
        if request.method != 'POST':
            return (json.dumps({"success": False, "error": "Only POST allowed"}), 405, {'Content-Type': 'application/json'})

        # --- Parsear datos del request ---
        # File
        if not request.files or 'file' not in request.files:
            return (json.dumps({"success": False, "error": "No file part in the request"}), 400, {'Content-Type': 'application/json'})
        file = request.files['file']
        if file.filename == '':
            return (json.dumps({"success": False, "error": "No selected file"}), 400, {'Content-Type': 'application/json'})
        
        # Languages
        languages = request.form.get('languages', '')
        
        # available_hours_per_semester
        available_hours_per_semester = request.form.get('available_hours_per_semester', None)
        if available_hours_per_semester is not None:
            try:
                available_hours_per_semester = int(available_hours_per_semester)
            except ValueError:
                return (json.dumps({"success": False, "error": "available_hours_per_semester must be an integer"}), 400, {'Content-Type': 'application/json'})
        else:
            available_hours_per_semester = 0

        # Generar un ID entero único basado en la marca de tiempo actual (milisegundos)
        employee_id = int(datetime.datetime.utcnow().timestamp() * 1000)

        # --- Subir archivo al bucket ---
        storage_client = storage.Client(project=PROJECT_ID)
        bucket = storage_client.bucket(BUCKET_NAME)
        blob = bucket.blob(f"{employee_id}.pdf")
        blob.upload_from_file(file, rewind=True)
        logging.info(f"Archivo '{employee_id}.pdf' subido correctamente al bucket '{BUCKET_NAME}'.")

        # --- Guardar metadatos en BigQuery ---
        bq_client = bigquery.Client(project=PROJECT_ID)
        empleados_table_id = f"{PROJECT_ID}.{BQ_DATASET}.{BQ_EMPLEADOS_TABLE}"
        
        empleados_insert_query = f"""
            INSERT INTO `{empleados_table_id}` (ID, file, languages, available_hours_per_semester, created_at)
            VALUES (@id, @file, @languages, @hours, @created_at)
        """
        
        job_config = bigquery.QueryJobConfig(query_parameters=[
            bigquery.ScalarQueryParameter("id", "INT64", employee_id),
            bigquery.ScalarQueryParameter("file", "STRING", file.filename),
            bigquery.ScalarQueryParameter("languages", "STRING", languages),
            bigquery.ScalarQueryParameter("hours", "INT64", available_hours_per_semester),
            bigquery.ScalarQueryParameter("created_at", "STRING", datetime.datetime.utcnow().isoformat())
        ])
        
        insert_job = bq_client.query(empleados_insert_query, job_config=job_config)
        insert_job.result()  # Esperar a que se complete la consulta
        if insert_job.errors:
            logging.error(f"Error al insertar en BigQuery: {insert_job.errors}")
            return (json.dumps({"success": False, "error": str(insert_job.errors)}), 500, {'Content-Type': 'application/json'})

        # --- Insertar en la tabla de idiomas ---
        # Parsear el string de idiomas a lista (asumiendo que viene como 'Catalan,Spanish,English')
        employee_langs = [lang.strip() for lang in languages.split(',') if lang.strip()]
        idiomas_table_id = f"{PROJECT_ID}.{BQ_DATASET}.{BQ_IDIOMAS_TABLE}"
        idiomas_insert_query = f"""
            INSERT INTO `{idiomas_table_id}` (ID, employee_langs)
            VALUES (@id, @employee_langs)
        """
        idiomas_job_config = bigquery.QueryJobConfig(query_parameters=[
            bigquery.ScalarQueryParameter("id", "INT64", employee_id),
            bigquery.ArrayQueryParameter("employee_langs", "STRING", employee_langs)
        ])
        idiomas_insert_job = bq_client.query(idiomas_insert_query, job_config=idiomas_job_config)
        idiomas_insert_job.result()
        if idiomas_insert_job.errors:
            logging.error(f"Error al insertar en empleados_idiomas: {idiomas_insert_job.errors}")
            return (json.dumps({"success": False, "error": str(idiomas_insert_job.errors)}), 500, {'Content-Type': 'application/json'})

        return (json.dumps({"success": True, "filename": file.filename, "employee_id": employee_id}), 200, {'Content-Type': 'application/json'})
    except Exception as e:
        logging.error(f"Error inesperado: {str(e)}")
        return (json.dumps({"success": False, "error": str(e)}), 500, {'Content-Type': 'application/json'}) 