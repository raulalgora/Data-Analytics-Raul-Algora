import traceback
from google.cloud import storage
from vertexai.generative_models import Part
import logging

# Inicialización de clientes
storage_client = storage.Client()

def extract_semantic_description_from_cv(gcs_uri: str, model=None, employee_id="None") -> str | None:
    """Usa un LLM para extraer una descripción narrativa de un CV en GCS."""
    prompt = """
    You are an expert at analyzing CVs to synthesize comprehensive and insightful narrative summaries of a candidate's professional profile.
    Read the CV carefully and directly generate a detailed, structured narrative that highlights the candidate's core competencies, key experiences, and overall professional capabilities. The goal is to create a rich, descriptive summary that captures the essence of their profile for advanced semantic analysis.
    Organize the narrative into the following sections, ensuring no introductory phrases or meta-commentary precede the content of each section or the overall output:
    Professional Summary: A concise overview of the candidate's professional background, main accomplishments, and career focus.
    Technical Proficiencies: A descriptive paragraph detailing programming languages, tools, platforms, and technologies the candidate has experience with, emphasizing their application and depth of knowledge.
    Key Soft Skills & Leadership Qualities: A narrative section explaining the candidate's interpersonal and leadership qualities, illustrated by examples from their experience (e.g., problem-solving methodologies, communication styles, team collaboration, strategic thinking, adaptability).
    Language Capabilities: A clear statement of the candidate's language proficiencies, specifying the language and level (e.g., "Fluent in English, conversational in French").
    Domain & Functional Expertise: A comprehensive description of the candidate's industry-specific knowledge, functional areas of expertise (e.g., product management, cybersecurity, financial analysis), and the types of problems they are accustomed to solving within those domains.
    Focus on creating a fluid, grammatically correct narrative. Do not use bullet points or lists within the main sections. The output should be a coherent text document, ready for direct embedding, without any introductory sentences or phrases before the summary or any ofını.
    """
    try:
        logging.info(f"{employee_id} Procesando archivo: {gcs_uri}")
        bucket_name, blob_name = gcs_uri.replace("gs://", "").split("/", 1)
        bucket = storage_client.bucket(bucket_name)
        blob = bucket.blob(blob_name)

        logging.info(f"{employee_id} Descargando archivo desde GCS...")
        file_bytes = blob.download_as_bytes()
        logging.info(f"{employee_id} Archivo descargado correctamente.")

        mime_type = 'application/pdf' if blob_name.lower().endswith('.pdf') else 'text/plain'
        pdf_part = Part.from_data(data=file_bytes, mime_type=mime_type)

        logging.info(f"{employee_id} Enviando contenido al modelo de extracción (Gemini)...")
        if model is None:
            raise ValueError("model debe ser proporcionado")
        response = model.generate_content([prompt, pdf_part])
        logging.info(f"{employee_id} Respuesta recibida del modelo.")

        return response.text
    
    except Exception as e:
        logging.error(f"{employee_id} Error durante la extracción: {e}\n{traceback.format_exc()}")
        return None 