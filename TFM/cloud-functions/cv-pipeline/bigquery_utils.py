from google.cloud import bigquery
from config import PROJECT_ID, BQ_DATASET
import logging
from time import sleep

bq_client = bigquery.Client(project=PROJECT_ID)

def insert_row_to_bq(row: dict, table_name: str, identifier: int) -> bool:
    """
    Inserta una fila con los datos proporcionados en BigQuery.
    Si se proporciona un identificador (ID) y ya existe una fila con ese ID, actualiza las columnas fijas.
    Si no existe, inserta una nueva fila.
    Args:
        row (dict): Diccionario con los datos a insertar. Debe contener las claves: descripcion_semantica, embedding, experience_level, processed_at.
        table_name (str): Nombre de la tabla de BigQuery donde insertar los datos.
        identifier (int, optional): Valor del campo ID para identificar la fila.
    Returns:
        bool: True si la operación fue exitosa, False en caso contrario.
    """
    try:
        table_id = f"{PROJECT_ID}.{BQ_DATASET}.{table_name}"
        logging.info(f"[{identifier}] Intentando insertar/actualizar registro con ID {identifier if identifier is not None else 'N/A'} en {table_id}")

        # Buscar si ya existe una fila con ese ID
        query = f"""
            SELECT COUNT(*) as count
            FROM `{table_id}`
            WHERE ID = @id
        """
        job_config = bigquery.QueryJobConfig(query_parameters=[
            bigquery.ScalarQueryParameter("id", "INT64", identifier)
        ])
        query_job = bq_client.query(query, job_config=job_config)
        result = list(query_job.result())
        exists = result[0].count > 0 if result else False

        if exists:
            # Sistema de reintentos para el UPDATE
            max_retries = 5
            base_wait_time = 30  # 30 segundos inicial
            
            for attempt in range(max_retries):
                try:
                    if attempt > 0:
                        wait_time = base_wait_time * (2 ** attempt)  # 30, 60, 120, 240, 480 segundos
                        logging.info(f"[{identifier}] Reintento {attempt + 1}/{max_retries}. Esperando {wait_time} segundos...")
                        sleep(wait_time)
                    
                    # Actualizar las columnas fijas
                    update_query = f"""
                        UPDATE `{table_id}`
                        SET descripcion_semantica = @descripcion_semantica,
                            embedding = @embedding,
                            experience_level = @experience_level,
                            processed_at = @processed_at
                        WHERE ID = @id
                    """
                    params = [
                        bigquery.ScalarQueryParameter("descripcion_semantica", "STRING", row["descripcion_semantica"]),
                        bigquery.ArrayQueryParameter("embedding", "FLOAT64", row["embedding"]),
                        bigquery.ScalarQueryParameter("experience_level", "INT64", row["experience_level"]),
                        bigquery.ScalarQueryParameter("processed_at", "STRING", row["processed_at"]),
                        bigquery.ScalarQueryParameter("id", "INT64", identifier)
                    ]
                    update_job_config = bigquery.QueryJobConfig(query_parameters=params)
                    update_job = bq_client.query(update_query, job_config=update_job_config)
                    update_job.result()
                    logging.info(f"[{identifier}] Registro con ID {identifier} actualizado correctamente en BigQuery.")
                    return True
                    
                except Exception as update_error:
                    error_msg = str(update_error)
                    if "streaming buffer" in error_msg.lower():
                        if attempt < max_retries - 1:
                            logging.warning(f"[{identifier}] Error de streaming buffer en intento {attempt + 1}. Reintentando...")
                            continue
                        else:
                            logging.error(f"[{identifier}] Error de streaming buffer después de {max_retries} intentos. No se pudo actualizar.")
                            return False
                    else:
                        # Si es otro tipo de error, no reintentar
                        logging.error(f"[{identifier}] Error no relacionado con streaming buffer: {error_msg}")
                        raise update_error
        else:
            logging.error(f"[{identifier}] No se encontró registro con ID {identifier}, insertando nueva fila.")
            return False

    except Exception as e:
        logging.error(f"[{identifier}] Excepción durante el guardado del registro con ID {identifier if identifier is not None else 'N/A'}: {e}")
        return False 