import logging

def generate_embedding_from_text_vertex(text: str, embedding_model=None, employee_id="None") -> list[float] | None:
    """
    Genera un embedding para un texto dado usando Vertex AI.
    """
    try:
        logging.info(f"{employee_id} Generando embedding con Vertex AI...")
        if embedding_model is None:
            raise ValueError("model debe ser proporcionado")
        embeddings = embedding_model.get_embeddings([text])
        if embeddings:
            vector = embeddings[0].values
            logging.info(f"{employee_id} Embedding generado correctamente.")
            return vector
        else:
            logging.warning(f"{employee_id} La respuesta del modelo de embedding estaba vacía.")
            return None
    except Exception as e:
        logging.error(f"{employee_id} Error al generar embedding con Vertex AI: {e}")
        return None 