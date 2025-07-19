import streamlit as st
import requests

# --- Configuración de la Página ---
st.set_page_config(
    page_title="Búsqueda de Cursos",
    page_icon="🔎",
    layout="wide"
)

# --- Constantes y Función de API ---
# Esta URL debe apuntar a tu nuevo endpoint
API_URL = "https://recomendacion-semantica-999832391351.europe-west1.run.app"

@st.cache_data(ttl=600)
def get_text_search_recommendations(employee_id: str, query_text: str):
    """Llama a la API de búsqueda por texto."""
    if not employee_id or not query_text:
        return None
    
    payload = {"employee_id": employee_id, "query_text": query_text}
    try:
        response = requests.post(API_URL, json=payload, headers={"Content-Type": "application/json"}, timeout=90)
        if response.status_code == 200:
            return response.json()
        else:
            st.error(f"Error en la respuesta de la API ({response.status_code}):")
            st.json(response.json())
            return None
    except requests.exceptions.RequestException as e:
        st.error(f"Error al conectar con la API: {e}")
        return None

# --- Interfaz de Usuario ---

st.title("🔎 Búsqueda de Cursos por Tema o Habilidad")
st.markdown("Describe lo que te gustaría aprender y el sistema encontrará los cursos más relevantes para ti, ajustados a tu nivel de experiencia.")

# --- Entradas del Usuario ---
col1, col2 = st.columns(2)
with col1:
    employee_id_input = st.text_input(
        "Tu ID de Empleado (para filtrar por nivel)",
        placeholder="Ej: 2850972"
    )
with col2:
    # Este espacio queda libre por si quieres añadir más filtros en el futuro
    pass

query_text_input = st.text_area(
    "¿Qué quieres aprender?",
    placeholder="Ej: 'Modelos para detectar fraude con machine learning', 'habilidades de comunicación para líderes', 'introducción a SQL'...",
    height=120
)

if st.button("Buscar Cursos", type="primary", use_container_width=True):
    if not employee_id_input or not query_text_input:
        st.warning("Por favor, introduce tu ID y describe lo que quieres aprender.")
    else:
        with st.spinner(f"Buscando cursos sobre '{query_text_input[:40]}...'"):
            # Guardamos la respuesta en el estado de la sesión
            st.session_state.text_search_response = get_text_search_recommendations(employee_id_input, query_text_input)

# --- Visualización de Resultados ---
if 'text_search_response' in st.session_state and st.session_state.text_search_response:
    response_data = st.session_state.text_search_response
    st.markdown("---")

    employee_level = response_data.get('employee_level')
    st.header(f"Resultados para tu búsqueda")
    st.caption(f"Mostrando cursos con un nivel de dificultad adecuado para tu nivel de experiencia calculado: **{employee_level} / 10**")

    recommended_courses = response_data.get("recommended_courses", [])
    
    if recommended_courses:
        for i, course in enumerate(recommended_courses):
            st.subheader(f"{i+1}. {course['course_title']}")
            
            col_metric, col_details = st.columns([1, 4])
            with col_metric:
                st.metric(label="Relevancia con tu Búsqueda", value=f"{course['similarity']:.1%}")

            with col_details:
                st.markdown(f"**ID del Curso:** `{course['course_id']}`")
                level_min = course.get('course_level_min')
                level_max = course.get('course_level_max')
                if level_min is not None:
                    st.markdown(f"**📊 Nivel del Curso:** `{level_min} - {level_max}`")

                with st.expander("Ver descripción del curso"):
                    st.write(course['course_description'])
            st.divider()
    else:
        st.info("No se encontraron cursos que coincidan con tu búsqueda y tu nivel de experiencia.")