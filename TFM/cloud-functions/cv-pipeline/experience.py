import json
import logging

def infer_experience_level_from_description(semantic_description: str, model=None, employee_id="None") -> int | None:
    """
    Usa un LLM para inferir el nivel de experiencia de un empleado a partir de su
    descripción semántica.
    Returns:
        int: Un nivel de experiencia de 0 a 10, o None si falla.
    """
    prompt = f"""
    You are an expert HR analyst specializing in evaluating professional experience from text summaries. Your task is to assign an experience level to a candidate based on their professional profile summary.

    The experience level must be on a scale from 0 to 10, where:
    - 0-1: Intern / Trainee (No real-world experience, primarily academic).
    - 2-3: Junior / Entry-Level (0-2 years of experience, needs guidance).
    - 4-6: Mid-Level / Intermediate (2-5 years of experience, mostly autonomous).
    - 7-8: Senior (5-10 years of experience, leads projects, mentors others).
    - 9-10: Principal / Expert (10+ years of deep, specialized experience, industry-recognized).

    Analyze the following professional summary:
    ---
    {semantic_description}
    ---

    **Output Format:**
    You MUST respond with a single, valid JSON object. The JSON object must have a single key, "experience_level", and its value MUST be an integer between 0 and 10. Do not add any text before or after the JSON object.

    Example of a valid response:
    {{
      "experience_level": 7
    }}
    """
    try:
        # Forzar la salida JSON
        generation_config = {"response_mime_type": "application/json"}
        if model is None:
            raise ValueError("model debe ser proporcionado")
        response = model.generate_content([prompt], generation_config=generation_config)
        response_data = json.loads(response.text)
        level = response_data.get("experience_level")
        if isinstance(level, int) and 0 <= level <= 10:
            return level
        else:
            logging.warning(f"{employee_id} El modelo devolvió un nivel inválido: {level}")
            return None
    except (json.JSONDecodeError, KeyError, Exception) as e:
        logging.error(f"{employee_id} Error durante la inferencia de nivel: {e}")
        return None 