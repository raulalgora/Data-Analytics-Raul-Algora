import streamlit as st
import pandas as pd

# --- Configuración de la Página ---
st.set_page_config(
    page_title="Dashboard de Evaluación",
    page_icon="📈",
    layout="wide"
)

st.title("📈 Dashboard de Evaluación de Modelos de Recomendación")
st.markdown("Análisis comparativo de las métricas de calidad para los diferentes sistemas de recomendación desarrollados.")
st.info("Resultados pre-calculados offline sobre un conjunto de prueba de **100 empleados**, recomendando **10 cursos** para cada uno.")

# ===================================================================
# DATOS PRE-CALCULADOS
# Aquí pegamos los resultados que obtuviste.
# ===================================================================

evaluation_data = [
    {
        "model_name": "Modelo Base (Similitud de Coseno)",
        "description": "Este modelo recomienda los 10 cursos cuyos embeddings son más cercanos al embedding del perfil del empleado. Prioriza la relevancia semántica directa, resultando en una alta personalización pero con menor diversidad y cobertura.",
        "metrics": {
            "coverage": 0.03707,
            "diversity": 0.2015,
            "personalization": 0.9924,
            "avg_intra_list_similarity": 0.7984
        },
        "sample_recommendations": {
            "Ejemplo Empleado A": ["ID_Curso_1", "ID_Curso_2", "..."],
            "Ejemplo Empleado B": ["ID_Curso_3", "ID_Curso_4", "..."]
        }
    },
    {
        "model_name": "Modelo 2 (Futuro: con Mejora de Diversidad)",
        "description": "Un futuro modelo podría implementar técnicas como el re-ranking con penalización por similitud (Maximal Marginal Relevance) para aumentar la diversidad y la cobertura, manteniendo una alta personalización.",
        "metrics": {
            # Valores hipotéticos de un modelo mejorado
            "coverage": 0.12, # <-- Esperaríamos que suba
            "diversity": 0.65, # <-- Esperaríamos que suba significativamente
            "personalization": 0.98, # <-- Podría bajar un poco, pero seguiría siendo alta
            "avg_intra_list_similarity": 0.35
        },
        "sample_recommendations": {
            "Ejemplo Empleado A": ["ID_Curso_1", "ID_Curso_X", "..."],
            "Ejemplo Empleado B": ["ID_Curso_3", "ID_Curso_Y", "..."]
        }
    }
]


# --- FUNCIÓN PARA MOSTRAR LOS RESULTADOS DE UN MODELO ---
def display_model_results(model_data):
    st.header(model_data["model_name"])
    st.markdown(f"*{model_data['description']}*")

    metrics = model_data["metrics"]
    coverage = metrics.get("coverage", 0)
    diversity = metrics.get("diversity", 0)
    personalization = metrics.get("personalization", 0)
    avg_ils = metrics.get("avg_intra_list_similarity", 0)

    # Mostrar métricas en columnas
    col1, col2, col3 = st.columns(3)
    col1.metric("📊 Cobertura", f"{coverage:.2%}", help="Porcentaje del catálogo total de cursos que se recomienda al menos una vez. Más alto es mejor.")
    col2.metric("🎨 Diversidad", f"{diversity:.4f}", help=f"1 - Similitud Intra-Lista (Más alto es mejor). La similitud promedio fue {avg_ils:.4f}.")
    col3.metric("👤 Personalización", f"{personalization:.4f}", help="Disimilitud promedio entre las listas de los usuarios (Más alto es mejor).")

    # Mostrar ejemplos de recomendaciones (puedes llenar esto más tarde)
    with st.expander("Ver ejemplos de recomendaciones (placeholder)"):
        st.table(pd.DataFrame(model_data["sample_recommendations"]))
    
    st.markdown("---")


# --- Bucle para mostrar todos los modelos evaluados ---
for model in evaluation_data:
    display_model_results(model)