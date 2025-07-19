from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.models import Variable
from google.cloud import storage
from datetime import datetime
import json, logging

GCS_BUCKET = Variable.get("GCS_LANDING_BUCKET")         # donde está el JSON
CONFIG_PATH = "configs/airflow_variables.json"

def load_vars():
    client = storage.Client()
    bucket = client.bucket(GCS_BUCKET)
    blob = bucket.blob(CONFIG_PATH)
    content = blob.download_as_text()
    variables = json.loads(content)

    for key, value in variables.items():
        Variable.set(key, value)
        logging.info(f"✅ Variable {key} creada")

with DAG(
    dag_id="bootstrap_variables_from_json",
    start_date=datetime(2025, 7, 1),
    schedule_interval=None,
    catchup=False,
    tags=["bootstrap"]
) as dag:
    PythonOperator(
        task_id="load_airflow_variables",
        python_callable=load_vars
    )