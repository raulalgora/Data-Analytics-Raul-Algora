import json
import logging

def infer_course_difficulty_range(course_info: dict, extraction_model=None) -> tuple[int | None, int | None]:
    """
    Usa un LLM para inferir el rango de dificultad (mínimo y máximo) de un curso,
    utilizando tanto el título como la descripción.

    Returns:
        tuple: (level_min, level_max) o (None, None) si falla.
    """
    semantic_description = course_info.get("descripcion_semantica", "")
    course_title = course_info.get("Training Title", "N/A")

    prompt = f"""
    You are an expert curriculum analyst. Your task is to determine the experience level range a course is designed for, based on its title and summary.

    The difficulty level must be on a scale from 0 to 10, where:
    - 0-1: Foundational / Introductory
    - 2-3: Beginner
    - 4-6: Intermediate
    - 7-8: Advanced
    - 9-10: Expert

    Analyze the following course information. Pay close attention to keywords in BOTH the title and the summary, such as "introduction", "for beginners", "advanced", "complete guide", "masterclass", "from scratch", etc.

    ---
    Course Title: {course_title}

    Course Summary:
    {semantic_description}
    ---

    **Output Format:**
    You MUST respond with a single, valid JSON object with two keys: "level_min" and "level_max".
    - Both values MUST be integers between 0 and 10.
    - `level_min` MUST be less than or equal to `level_max`.
    """
    try:
        generation_config = {"response_mime_type": "application/json"}
        if extraction_model is None:
            raise ValueError("extraction_model debe ser proporcionado")
        response = extraction_model.generate_content([prompt], generation_config=generation_config)

        response_data = json.loads(response.text)
        level_min = response_data.get("level_min")
        level_max = response_data.get("level_max")

        if (isinstance(level_min, int) and isinstance(level_max, int) and
            0 <= level_min <= 10 and 0 <= level_max <= 10 and
            level_min <= level_max):
            return level_min, level_max
        else:
            logging.warning(f"{course_info.get('Training Object ID', 'N/A')} El modelo devolvió un rango de nivel inválido: min={level_min}, max={level_max}")
            return None, None

    except (json.JSONDecodeError, KeyError, Exception) as e:
        logging.error(f"Error en la llamada a la API o parseo (ID: {course_info.get('Training Object ID', 'N/A')}): {e}")
        return None, None 