# Configuración centralizada para la cloud function course-pipeline
PROJECT_ID = "tfm-caixabank"
LOCATION = "europe-southwest1"

# BigQuery
BQ_DATASET = "courses_dataset"
BQ_TABLE_PREPROCESADOS = "daily_courses_fixed"
BQ_TABLE_PROCESADOS = "cursos_procesados"

# Vertex AI
TEXT_MODEL = "gemini-2.0-flash"
EMBEDDING_MODEL = "gemini-embedding-001"

# Otros parámetros globales
DEFAULT_LANGUAGE = "es" 