import os

PROJECT_ID = os.environ.get("PROJECT_ID", "tfm-caixabank")
BUCKET_NAME = os.environ.get("BUCKET_NAME", "cvs-empleados")
BQ_DATASET = os.environ.get("BQ_DATASET", "recomendation_system")
BQ_EMPLEADOS_TABLE = os.environ.get("BQ_EMPLEADOS_TABLE", 'empleados_procesados')
BQ_IDIOMAS_TABLE = os.environ.get("BQ_IDIOMAS_TABLE", 'empleados_idiomas')