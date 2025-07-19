import traceback
import streamlit as st
import requests

from config import GCF_UPLOAD_CV_URL

st.set_page_config(
    page_title="Subida de Documentos a GCP",
    page_icon="📤",
    layout="wide"
)

st.title("📤 Subida de Documentos a Google Cloud Storage")
st.markdown("Sube tus documentos y se almacenarán en el bucket de GCP que indiques.")

# --- Formulario de subida ---
with st.form("upload_form"):
    uploaded_file = st.file_uploader("Selecciona un archivo PDF para subir", type=["pdf"])
    language_options = ["Catalan", "Spanish", "English", "French", "German", "Italian", "Portuguese", "Other"]
    selected_languages = st.multiselect("Idiomas", language_options)
    languages = ", ".join(selected_languages)
    available_hours_per_semester = st.number_input("Horas disponibles por semestre", min_value=0, max_value=50, step=1)
    submit_button = st.form_submit_button("Subir archivo")

if submit_button:
    if not uploaded_file:
        st.warning("Por favor, selecciona un archivo para subir.")
    elif not uploaded_file.name.lower().endswith('.pdf'):
        st.warning("El archivo debe ser un PDF (.pdf).")
    else:
        try:
            files = {"file": (uploaded_file.name, uploaded_file, uploaded_file.type)}
            data = {
                "languages": languages,
                "available_hours_per_semester": int(available_hours_per_semester)
            }
            response = requests.post(GCF_UPLOAD_CV_URL, files=files, data=data)
            if response.status_code == 200 and response.json().get("success"):
                employee_id = response.json().get("employee_id")
                st.success(f"Archivo '{uploaded_file.name}' subido correctamente y datos guardados en BigQuery.")
                if employee_id:
                    st.info(f"ID de empleado asignado: {employee_id}")
            else:
                st.error(f"Error: {response.text}")
        except Exception as e:
            st.error(f"Error al subir el archivo: {e}\n\n{traceback.format_exc()}")