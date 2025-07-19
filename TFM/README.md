# TFM_Caixa

Este repositorio contiene el proyecto de TFM para CaixaBank, una solución integral que abarca la ingesta, procesamiento, análisis y visualización de datos, utilizando tecnologías modernas de orquestación, cloud, pipelines de datos y aplicaciones web.

## Tabla de Contenidos

- [Descripción General](#descripción-general)
- [Estructura del Proyecto](#estructura-del-proyecto)
- [Componentes Principales](#componentes-principales)
  - [Airflow (Orquestación de Pipelines)](#airflow-orquestación-de-pipelines)
  - [API](#api)
  - [Cloud Functions](#cloud-functions)
  - [Dataflow](#dataflow)
  - [Frontend](#frontend)
  - [Terraform (Infraestructura como Código)](#terraform-infraestructura-como-código)
- [Requisitos](#requisitos)
- [Cómo Ejecutar](#cómo-ejecutar)
- [Autores](#autores)
- [Licencia](#licencia)

---

## Descripción General

El objetivo de este proyecto es crear una arquitectura robusta y escalable para la gestión de datos y recomendaciones personalizadas, integrando diferentes tecnologías de procesamiento, almacenamiento y visualización, tanto en local como en la nube.

---

## Estructura del Proyecto

```
TFM_Caixabank/
│
├── airflow-docker/           # Orquestación de pipelines con Apache Airflow en Docker
├── API/                     # API REST para interacción y procesamiento de datos
├── cloud-functions/         # Funciones serverless para procesamiento específico en GCP
├── dataflow_courses/        # Pipelines de procesamiento de datos con Apache Beam/Dataflow
├── front/                   # Aplicación web para visualización y carga de datos (Streamlit)
├── terraform/               # Infraestructura como código (IaC) para GCP
├── cloudbuild.yaml          # Configuración de CI/CD en Google Cloud Build
├── README.md                # Este archivo
└── requirements.txt         # Requisitos globales del proyecto
```

---

## Componentes Principales

### Airflow (Orquestación de Pipelines)

- **Ubicación:** `airflow-docker/`
- **Descripción:** Contiene la configuración y los DAGs de Apache Airflow para orquestar los flujos de trabajo de ingesta, transformación y carga de datos.
- **Archivos clave:**
  - `docker-compose.yaml`: Despliegue de Airflow en contenedores.
  - `dags/`: Scripts de los DAGs, incluyendo scraping, procesamiento y carga de datos.

### API

- **Ubicación:** `API/`
- **Descripción:** API REST desarrollada en Python para exponer servicios de procesamiento y consulta de datos.
- **Archivos clave:**
  - `api_server.py`: Servidor principal de la API.
  - `add_loadtime_column.py`, `inspect_columns.py`: Scripts de utilidades para manipulación de datos.
  - `Dockerfile`: Contenedor para despliegue de la API.

### Cloud Functions

- **Ubicación:** `cloud-functions/`
- **Descripción:** Conjunto de funciones serverless desplegadas en Google Cloud Functions para tareas específicas como extracción, embedding, recomendación y procesamiento de CVs.
- **Subcarpetas:**
  - `course-pipeline-job/`
  - `cv-pipeline/`
  - `cv-uploader/`
  - `find-similar-courses/`
  - `recomendacion-gap-rol/`
  - `recomendacion-semantica/`
  - `recomendar-gap-rol/`
- **Cada subcarpeta** contiene su propio `main.py`, dependencias y lógica específica.

### Dataflow

- **Ubicación:** `dataflow_courses/`
- **Descripción:** Pipelines de procesamiento de datos usando Apache Beam, ejecutables en Google Dataflow.
- **Archivos clave:**
  - `courses_pipeline_fixed.py`: Pipeline principal de procesamiento de cursos.
  - `Dockerfile`: Imagen para ejecutar el pipeline en Dataflow.

### Frontend

- **Ubicación:** `front/`
- **Descripción:** Aplicación web desarrollada con Streamlit para visualización de dashboards, búsqueda temática y carga de CVs.
- **Archivos clave:**
  - `app.py`: Entrada principal de la app.
  - `pages/`: Páginas de la aplicación (dashboard, búsqueda, upload de CV).
  - `Dockerfile`: Contenedor para despliegue del frontend.

### Terraform (Infraestructura como Código)

- **Ubicación:** `terraform/`
- **Descripción:** Scripts de Terraform para desplegar y gestionar la infraestructura en Google Cloud Platform (GCP), incluyendo BigQuery, Cloud Run y Composer.
- **Estructura modular:** Cada recurso tiene su propio módulo reutilizable.

---

## Requisitos

- Docker y Docker Compose
- Python 3.8+
- Google Cloud SDK
- Terraform
- (Opcional) Entorno virtual para Python

Consulta los archivos `requirements.txt` de cada componente para dependencias específicas.

---

## Cómo Ejecutar

1. **Clonar el repositorio**
   ```bash
   git clone https://github.com/tu_usuario/TFM_Caixabank.git
   cd TFM_Caixabank
   ```

2. **Levantar Airflow en local**
   ```bash
   cd airflow-docker
   docker-compose up
   ```

3. **Desplegar la API**
   ```bash
   cd ../API
   docker build -t tfm_api .
   docker run -p 8000:8000 tfm_api
   ```

4. **Ejecutar el Frontend**
   ```bash
   cd ../front
   streamlit run app.py
   ```

5. **Desplegar infraestructura en GCP**
   ```bash
   cd ../terraform
   terraform init
   terraform apply
   ```

6. **Desplegar Cloud Functions y Dataflow**
   - Sigue las instrucciones específicas en cada subcarpeta.

---

## Licencia

Este proyecto está bajo la Licencia MIT. Consulta el archivo LICENSE para más detalles.