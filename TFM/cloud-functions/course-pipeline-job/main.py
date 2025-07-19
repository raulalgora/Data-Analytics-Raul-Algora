import logging
import vertexai
from vertexai.generative_models import GenerativeModel
from vertexai.language_models import TextEmbeddingModel
from google.cloud import bigquery
from config import BQ_DATASET, BQ_TABLE_PREPROCESADOS, BQ_TABLE_PROCESADOS, TEXT_MODEL, EMBEDDING_MODEL, PROJECT_ID, LOCATION
from extraction import extract_semantic_description_from_course
from embedding import generate_embedding_from_text_vertex
from difficulty import infer_course_difficulty_range
from logging_config import setup_json_logging
import datetime

# Configurar logging para stdio con JSON estructurado
setup_json_logging()

def course_pipeline():
    """
    Triggered by a change to a Cloud Storage bucket or HTTP request.
    Args:
         event (dict): Event payload.
         context (google.cloud.functions.Context): Metadata for the event.
    """

    # Iniciamos modelos
    logging.info("Inicializando modelos de Vertex AI")
    vertexai.init(project=PROJECT_ID, location=LOCATION)
    text_model = GenerativeModel(TEXT_MODEL)
    embedding_model = TextEmbeddingModel.from_pretrained(EMBEDDING_MODEL)

    # Ejecutar query en BigQuery para obtener cursos
    bq_client = bigquery.Client(project=PROJECT_ID)
    current_date = datetime.datetime.now().strftime('%Y-%m-%d')
    query = f"""
    SELECT *
    FROM `{PROJECT_ID}.{BQ_DATASET}.{BQ_TABLE_PREPROCESADOS}`
    WHERE load_date = '{current_date}'
    """
    
    logging.info("Ejecutando query en BigQuery para obtener cursos")
    query_job = bq_client.query(query)
    results = list(query_job.result())
    
    if not results:
        logging.warning("No se encontraron cursos para procesar")
        return
    
    logging.info(f"Se encontraron {len(results)} cursos para procesar")
    
    # Procesar cursos en batch de 50
    batch_size = 50
    processed_batches = 0
    total_processed = 0
    
    for i in range(0, len(results), batch_size):
        batch = results[i:i + batch_size]
        batch_number = processed_batches + 1
        logging.info(f"Procesando batch {batch_number} con {len(batch)} cursos")
        
        batch_data = []
        
        for row in batch:
            course_id = row.get('training_object_id', 'unknown')
            course_data = {
                'Training Title': row.get('training_title', ''),
                'Training Provider': row.get('training_provider', ''),
                'Training Type': row.get('training_type', ''),
                'Training Active': row.get('training_active', ''),
                'Training Description': row.get('training_description', ''),
                'Training Hours': row.get('training_hours', ''),
                'Area de formación': row.get('area_formacion', ''),
                'Subarea de formación': row.get('subarea_formacion', ''),
                'Keyword': row.get('keyword', ''),
                'Language': row.get('language', ''),
                'Tipo de formación': row.get('tipo_formacion', ''),
                'Training Subject': row.get('training_subject', ''),
                # Los siguientes campos no aparecen en la tabla pero estaban en el dict original
                'Loadtime': row.get('loadtime', ''),
                'Load Date': row.get('load_date', ''),
                'Date Processed': row.get('date_processed', ''),
                'Processing Timestamp': row.get('processing_timestamp', '')
            }
            
            logging.info(f"[{course_id}] Procesando curso: {course_data.get('title', 'Sin título')}")
            
            try:
                # Extraer descripción semántica
                logging.info(f"[{course_id}] Extrayendo descripción semántica del curso...")
                semantic_description = extract_semantic_description_from_course(course_data, model=text_model, course_id=course_id)
                if not semantic_description:
                    logging.error(f"[{course_id}] Extracción de descripción semántica fallida")
                    continue
                logging.info(f"[{course_id}] Extracción de descripción semántica completada")
                logging.debug(f"[{course_id}] Semantic description: {semantic_description}")
                
                # Inferir nivel de dificultad
                logging.info(f"[{course_id}] Infiriendo nivel de dificultad...")
                difficulty_level_min, difficulty_level_max = infer_course_difficulty_range(semantic_description, model=text_model, course_id=course_id)
                if difficulty_level_min is None or difficulty_level_max in None:
                    logging.error(f"[{course_id}] Inferencia de nivel de dificultad fallida")
                    continue
                logging.info(f"[{course_id}] Nivel de dificultad inferido: {difficulty_level_min}-{difficulty_level_max}")
                
                # Generar embedding
                logging.info(f"[{course_id}] Generando embedding...")
                embedding_vector = generate_embedding_from_text_vertex(semantic_description, embedding_model=embedding_model, course_id=course_id)
                if not embedding_vector:
                    logging.error(f"[{course_id}] Generación de embedding fallida")
                    continue
                logging.info(f"[{course_id}] Generación de embedding completada")
                logging.debug(f"[{course_id}] Embedding vector length: {len(embedding_vector)}")
                
                # Preparar datos para el batch
                row_data = {
                    "descripcion_semantica": semantic_description,
                    "embedding": embedding_vector,
                    "level_min": int(difficulty_level_min),
                    "level_max": int(difficulty_level_max),
                    "subprocessed_at": datetime.datetime.utcnow().isoformat()
                }
                batch_data.append(row_data)
                total_processed += 1
                
                logging.info(f"[{course_id}] Curso procesado exitosamente")
                
            except Exception as e:
                logging.error(f"[{course_id}] Error inesperado en pipeline: {str(e)}")
                continue
        
        # Insertar batch en BigQuery
        if batch_data:
            try:
                logging.info(f"Insertando batch {batch_number} con {len(batch_data)} registros en BigQuery")
                errors = bq_client.insert_rows_json(f"{PROJECT_ID}.{BQ_DATASET}.{BQ_TABLE_PROCESADOS}", batch_data)
                if errors:
                    logging.error(f"Errores al insertar batch {batch_number}: {errors}")
                else:
                    logging.info(f"Batch {batch_number} insertado exitosamente en BigQuery")
            except Exception as e:
                logging.error(f"Error al insertar batch {batch_number} en BigQuery: {str(e)}")
        
        processed_batches += 1
    
    logging.info(f"Procesamiento completado. Total de cursos procesados: {total_processed} en {processed_batches} batches")

if __name__ == "__main__":
    course_pipeline()