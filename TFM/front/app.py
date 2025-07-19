import streamlit as st
import requests

# --- CONFIGURACIÓN DE LA PÁGINA ---
st.set_page_config(
    page_title="Recomendador de Cursos",
    page_icon="🎓",
    layout="wide"
)

# --- DATOS Y CONSTANTES ---
API_URLS = {
    "similar_courses": "https://europe-southwest1-tfm-caixabank.cloudfunctions.net/find-similar-courses", 
    "skill_gap": "https://recomendar-gap-rol-999832391351.europe-southwest1.run.app"
}

ROLE_LIST = [
    "Data Engineer", "Data Modeler", "Machine Learning Engineer(MLE)", "Data Scientist",
    "Controller & Reporting - Cloud Finance", "Assistant", "HR Business Partner", "SSGG",
    "Tech Delivery Lead", "Infraestructura", "UX / UI", "Software Engineer",
    "Technical Solution", "Quality Assurance", "SRE", "Arquitecto", "Solution Engineer",
    "Scrum Master", "Innovación", "OperationsSpecialist", "T & T", "Service Owner", "Product Owner"
]

# --- FUNCIÓN GENERAL PARA LLAMAR A LAS APIs ---
@st.cache_data(ttl=600)
def get_recommendations(rec_type: str, payload: dict):
    api_url = API_URLS.get(rec_type)
    try:
        response = requests.post(api_url, json=payload, headers={"Content-Type": "application/json"}, timeout=90)
        if response.status_code == 200:
            return response.json()
        else:
            st.error(f"Error en la respuesta de la API ({response.status_code}): {response.text}")
            return None 
    except requests.exceptions.RequestException as e:
        st.error(f"Error al conectar con la API: {e}")
        return None

# --- INTERFAZ DE USUARIO ---

st.title("🎓 Sistema de Recomendación de Cursos Inteligente")

# 1. Selector de tipo de recomendación
st.subheader("1. Elige tu objetivo")
rec_type_option = st.radio(
    "¿Qué tipo de recomendación buscas?",
    ("Cursos para mi Perfil Actual", "Plan de Carrera (hacia un Rol)"),
    key="rec_type",
    horizontal=True,
    label_visibility="collapsed"
)

# 2. Entradas del usuario
st.subheader("2. Introduce tus datos y preferencias")

if st.session_state.rec_type == "Cursos para mi Perfil Actual":
    col1, col2 = st.columns(2)
    with col1:
        employee_id_input = st.text_input("Tu ID de Empleado", placeholder="Ej: 2850972")
    with col2:
        lambda_param = st.slider(
            "Nivel de Exploración (Diversidad)",
            min_value=0.0,
            max_value=1.0,
            value=0.1,
            step=0.1,
            help="0.0 = Máxima Relevancia. 1.0 = Máxima Diversidad."
        )
    target_role_input = None
else:
    col1, col2 = st.columns(2)
    with col1:
        employee_id_input = st.text_input("Tu ID de Empleado", placeholder="Ej: 2850972")
    with col2:
        target_role_input = st.selectbox("Rol al que aspiras", options=ROLE_LIST, index=None, placeholder="Selecciona un rol...")
    lambda_param = 0.0

# 3. Botón para ejecutar la búsqueda
st.subheader("3. Obtén tus recomendaciones")
if st.button("Generar Recomendaciones", type="primary", use_container_width=True):
    if not employee_id_input:
        st.warning("Por favor, introduce tu ID de empleado.")
    elif st.session_state.rec_type == "Plan de Carrera (hacia un Rol)" and not target_role_input:
        st.warning("Por favor, selecciona el rol al que aspiras.")
    else:
        st.session_state.api_response = {}

        if st.session_state.rec_type == "Cursos para mi Perfil Actual":
            payload = {"employee_id": employee_id_input, "lambda": lambda_param}
            with st.spinner("Analizando tu perfil y buscando cursos..."):
                st.session_state.api_response = get_recommendations("similar_courses", payload)
        else:
            payload = {"employee_id": employee_id_input, "target_role": target_role_input}
            with st.spinner(f"Calculando la brecha de habilidades hacia '{target_role_input}'..."):
                st.session_state.api_response = get_recommendations("skill_gap", payload)

# --- VISUALIZACIÓN DE RESULTADOS ---
if st.session_state.get('api_response'):
    response_data = st.session_state.api_response
    st.markdown("---")

    # PLAN DE CARRERA
    if "recommended_courses_for_skill_gap" in response_data:
        employee_id = response_data.get("employee_id")
        target_role = response_data.get("target_role")
        employee_language = response_data.get("employee_language", "Desconocido")
        recommended_courses = response_data.get("recommended_courses_for_skill_gap", [])
        
        st.header(f"Plan de Carrera para el Empleado {employee_id}")
        st.caption(f"🌐 Idioma del empleado: `{employee_language}`")
        st.subheader(f"🚀 Cursos para alcanzar el rol de: **{target_role}**")

        if recommended_courses:
            for i, course in enumerate(recommended_courses):
                similarity_value = course.get("similarity_to_gap", 0)
                card_title = f"{i+1}. {course['course_title']}"
                course_language = course.get("course_languages", "Desconocido")

                st.subheader(card_title)
                col_metric, col_details = st.columns([1, 4])
                with col_metric:
                    st.metric(label="Relevancia para la Brecha", value=f"{similarity_value:.1%}")
                with col_details:
                    st.markdown(f"**ID del Curso:** `{course['course_id']}`")
                    st.markdown(f"**🌍 Idioma del Curso:** `{course_language}`")
                    with st.expander("Ver descripción del curso"):
                        st.write(course['course_description'])
                st.divider()
        else:
            st.info("No se encontraron cursos para esta selección.")

    # CURSOS PARA PERFIL ACTUAL
    else:
        employee_id = response_data.get("employee_id")
        employee_description = response_data.get("employee_description")
        employee_level = response_data.get("employee_level") 
        employee_languages = response_data.get("employee_languages", "Desconocido")
        recommended_courses = response_data.get("recommended_courses", [])
        lambda_used = response_data.get("lambda_parameter_used")


        st.header(f"Recomendaciones para el Empleado: {employee_id}")
        st.caption(f"🌐 Idioma del empleado: `{employee_languages}`")

        col_level, col_lang, col_lambda = st.columns(3)
        if employee_level is not None:
            col_level.metric("Tu Nivel de Experiencia", f"{employee_level} / 10", help="Nivel de experiencia calculado para tu perfil, usado para filtrar cursos.")
        if employee_languages:
            col_lang.metric("Tus Idiomas", ", ".join(employee_languages))
        if lambda_used is not None:
            col_lambda.metric("Parámetro de Exploración", f"{lambda_used:.1f}", help="0.0 = Máxima Relevancia, 1.0 = Máxima Diversidad.")

        with st.expander("Ver el Resumen Completo del Perfil Utilizado"):
            st.write(employee_description)

        st.subheader("✨ Cursos sugeridos basados en tu perfil actual:")

        if recommended_courses:
            for i, course in enumerate(recommended_courses):
                # Obtener todos los datos del curso
                is_reranked = course.get("reranked", False)
                similarity_value = course.get("original_similarity", course.get("similarity", 0))
                course_languages = course.get("course_languages", [])
                level_min = course.get("course_level_min")
                level_max = course.get("course_level_max")

                # Título dinámico
                card_title = f"{i+1}. {course['course_title']}"
                if is_reranked and lambda_used > 0.1:
                    card_title += "  *(Sugerido por Diversidad)*"

                st.subheader(card_title)
                
                # Columnas para métrica y detalles
                col_metric, col_details = st.columns([1, 4])
                
                with col_metric:
                    st.metric(
                        label="Relevancia Original",
                        value=f"{similarity_value:.1%}",
                        help="Similitud directa del curso con tu perfil, antes de aplicar el filtro de diversidad."
                    )
                
                with col_details:
                    st.markdown(f"**ID del Curso:** `{course['course_id']}`")
                    
                    # --- ¡CAMBIO CLAVE AQUÍ! ---
                    # Mostrar el rango de nivel del curso de forma clara
                    if level_min is not None and level_max is not None:
                        if level_min == level_max:
                            st.markdown(f"**📊 Nivel del Curso:** `{level_min}` (Tu nivel es **{employee_level}**)")
                        else:
                            st.markdown(f"**📊 Nivel del Curso:** `{level_min} - {level_max}` (Tu nivel es **{employee_level}**)")
                    
                    st.markdown(f"**🌍 Idioma(s) del Curso:** `{', '.join(course_languages)}`")

                    with st.expander("Ver descripción completa del curso"):
                        st.write(course['course_description'])
                
                st.divider() # Separador visual entre cursos
        else:
            st.info("No se encontraron cursos que coincidan con tus filtros. Intenta con otros parámetros.")
