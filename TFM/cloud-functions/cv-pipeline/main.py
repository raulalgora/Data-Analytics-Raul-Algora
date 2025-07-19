import logging
import json
import vertexai
from vertexai.generative_models import GenerativeModel
from vertexai.language_models import TextEmbeddingModel
from config import BQ_TABLE, TEXT_MODEL, EMBEDDING_MODEL, PROJECT_ID, LOCATION

from extraction import extract_semantic_description_from_cv
from embedding import generate_embedding_from_text_vertex
from experience import infer_experience_level_from_description
from bigquery_utils import insert_row_to_bq
import datetime

# Configurar logging para stdio con JSON estructurado
class JsonFormatter(logging.Formatter):
    def format(self, record):
        log_entry = {
            'timestamp': self.formatTime(record),
            'severity': record.levelname,
            'message': record.getMessage(),
            'logger': record.name
        }
        if hasattr(record, 'funcName'):
            log_entry['function'] = record.funcName
        if hasattr(record, 'lineno'):
            log_entry['line'] = record.lineno
        return json.dumps(log_entry)

# Configurar el logger raíz
logger = logging.getLogger()
logger.setLevel(logging.DEBUG)

# Eliminar handlers existentes
for handler in logger.handlers[:]:
    logger.removeHandler(handler)

# Añadir handler para stdio con JSON formatter
handler = logging.StreamHandler()
handler.setFormatter(JsonFormatter())
logger.addHandler(handler)

def cv_pipeline(event, context):
    """
    Triggered by a change to a Cloud Storage bucket.
    Args:
         event (dict): Event payload.
         context (google.cloud.functions.Context): Metadata for the event.
    """

    logging.info(f"Inicializando modelos")
    vertexai.init(project=PROJECT_ID, location=LOCATION)
    text_model = GenerativeModel(TEXT_MODEL)
    embedding_model = TextEmbeddingModel.from_pretrained(EMBEDDING_MODEL)

    logging.info(f"Evento recibido: {event}")
    bucket = event['bucket']
    file_name = event['name']
    
    gcs_path = f"gs://{bucket}/{file_name}"
    logging.info(f"GCS path: {gcs_path}")

    employee_id = file_name.split('.')[0]

    if not file_name.lower().endswith('.pdf'):
        logging.error(f"[{employee_id}] El archivo {gcs_path} no es un PDF. Solo se permiten archivos PDF.")
        return

    try:
        # Extraer descripción semántica
        logging.info(f"[{employee_id}] Extrayendo descripción semántica del CV...")
        semantic_description = extract_semantic_description_from_cv(gcs_path, model=text_model, employee_id=employee_id)
        if not semantic_description:
            logging.error(f"[{employee_id}] Extracción de texto fallida")
            return
        logging.info(f"[{employee_id}] Extracción de texto completada")
        logging.debug(f"[{employee_id}] Semantic description: {semantic_description}")
        
        # Inferir nivel de experiencia
        logging.info(f"[{employee_id}] Infiriendo nivel de experiencia...")
        experience_level = infer_experience_level_from_description(semantic_description, model=text_model, employee_id=employee_id)
        logging.info(f"[{employee_id}] Nivel de experiencia inferido: {experience_level}")
        
        # Generar embedding
        logging.info(f"[{employee_id}] Generando embedding...")
        embedding_vector = generate_embedding_from_text_vertex(semantic_description, embedding_model=embedding_model, employee_id=employee_id)
        if not embedding_vector:
            logging.error(f"[{employee_id}] Generación de embedding fallida")
            return
        logging.info(f"[{employee_id}] Generación de embedding completada")
        logging.debug(f"[{employee_id}] Embedding vector: {embedding_vector}")
        
        # Guardar en BigQuery
        logging.info(f"[{employee_id}] Preparando y guardando en BigQuery...")
        row = {
            "descripcion_semantica": semantic_description,
            "embedding": embedding_vector,
            "experience_level": int(experience_level),
            "processed_at": datetime.datetime.utcnow().isoformat()
        }
        save_success = insert_row_to_bq(row, BQ_TABLE, identifier=int(employee_id))
        if not save_success:
            logging.error(f"[{employee_id}] Guardado en BigQuery fallido")
            return
        
        logging.info(f"[{employee_id}] Pipeline completado con éxito")
    
    except Exception as e:
        logging.error(f"[{employee_id}] Error inesperado en pipeline: {str(e)}")