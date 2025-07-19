import traceback
import logging

def extract_semantic_description_from_course(course_data: dict, model=None, course_id="None") -> str | None:
    """Usa un LLM para extraer una descripción narrativa de un curso a partir de sus datos."""
    prompt = f"""
    You are an expert at analyzing course information and synthesizing comprehensive, insightful narrative summaries of a course's content, learning outcomes, and practical applications. Your goal is to create a rich, descriptive summary that captures the essence of the course for advanced semantic analysis and embedding.

    Read the following course information carefully and directly generate a detailed, structured narrative.

    Organize the narrative into the following sections, ensuring no introductory phrases or meta-commentary precede the content of each section or the overall output:

    **Course Overview:** A concise summary of what the course is about, its primary objective, and its overall focus.
    **Key Learning Outcomes & Skills Developed:** A descriptive paragraph detailing the core skills, competencies (both soft and technical), and knowledge areas that participants will acquire or enhance upon completing the course. Emphasize the practical application and depth of knowledge gained.
    **Technical Tools & Technologies Covered:** A narrative section explaining any specific software, platforms, programming languages, or technologies that are taught or utilized within the course. Describe how these tools are used in the context of the course content.
    **Target Audience & Applications:** A description of who the course is designed for and the real-world scenarios or professional contexts where the acquired skills can be applied.

    Consider the following course information for your summary:
    - Training Title: {course_data.get("Training Title", "N/A")}
    - Training Description: {course_data.get("Training Description", "N/A")}
    - Area de formación: {course_data.get("Area de formación", "N/A")}
    - Subarea de formación: {course_data.get("Subarea de formación", "N/A")}
    - Training Subject: {course_data.get("Training Subject", "N/A")}
    - Language: {course_data.get("Language", "N/A")}
    - Training Type: {course_data.get("Training Type", "N/A")}

    Focus on creating a fluid, grammatically correct narrative. Do not use bullet points or lists within the main sections. The output should be a coherent plain text document, ready for direct embedding, without any introductory sentences or phrases before the summary or any of the sections.
    """
    
    try:
        logging.info(f"{course_id} Procesando información del curso")
        
        logging.info(f"{course_id} Enviando información del curso al modelo de extracción (Gemini)...")
        if model is None:
            raise ValueError("model debe ser proporcionado")
        
        response = model.generate_content([prompt])
        logging.info(f"{course_id} Respuesta recibida del modelo.")
        
        return response.text
    
    except Exception as e:
        logging.error(f"{course_id} Error durante la extracción: {e}\n{traceback.format_exc()}")
        return None 