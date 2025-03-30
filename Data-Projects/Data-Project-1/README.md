# SQLAZO: Plataforma Interactiva de Análisis Inmobiliario

<div align="center">
  <img src="https://raw.githubusercontent.com/devicons/devicon/master/icons/python/python-original.svg" height="40" alt="python" />
  <img width="12" />
  <img src="https://raw.githubusercontent.com/devicons/devicon/master/icons/postgresql/postgresql-original.svg" height="40" alt="postgresql" />
  <img width="12" />
  <img src="https://raw.githubusercontent.com/devicons/devicon/master/icons/docker/docker-original.svg" height="40" alt="docker" />
</div>

## 📌 Descripción del Proyecto

SQLAZO es una plataforma interactiva con mapas dinámicos que integra datos clave sobre los distritos de Valencia para ayudar a tomar decisiones informadas sobre vivienda. Desarrollado tras las recientes inundaciones en Valencia, permite analizar cómo estos eventos podrían impactar el mercado inmobiliario.

## 🎯 Problema y Solución

Tras los recientes incidentes en Valencia, se prevé una redistribución de la demanda y una subida del precio de la vivienda. SQLAZO responde a preguntas como:
- ¿Dónde van a subir más los precios?
- ¿Qué zonas ofrecen mejor relación calidad-precio?
- ¿Qué áreas tienen mejores servicios esenciales?

Nuestra plataforma permite:
- Filtrar por ingresos y preferencias
- Visualizar distritos con códigos de color
- Ver distribución de zonas verdes
- Obtener datos detallados de cada distrito
- Comparar indicadores entre zonas

## 🛠️ Arquitectura Técnica

El proyecto está estructurado en cuatro componentes principales:

### 1. Ingestión de Datos
- **Fuentes**: Ayuntamiento de Valencia (API), INE (XLSX), Idealista (HTML)
- **Datos recopilados**: Colegios, hospitales, metro, zonas verdes, precios de alquiler y variaciones

### 2. Tratamiento del Dato
- Python para procesamiento y transformación
- PostgreSQL para almacenamiento
- Shapely para análisis geoespacial
- Tabla de equivalencias para unificar nomenclaturas de distritos

### 3. Visualización
- Interfaz web con Streamlit y Folium
- Mapas interactivos con selección de distritos
- Filtrado por ingresos mensuales
- Capas activables (distritos, zonas verdes)

### 4. Dockerización y Automatización
- Contenedores Docker para cada componente
- Luigi para orquestación de tareas
- Automatización del pipeline de datos

## 📊 Valor de Negocio

El proyecto tiene dos enfoques comerciales:

**B2B**: Suscripción para inmobiliarias y profesionales con análisis detallados.

**B2C**: Modelo freemium para usuarios particulares con comparador de zonas.

## 🚀 Próximos Pasos

Para futuras versiones consideramos incorporar:
- Datos de criminalidad
- Información de supermercados y centros comerciales
- Datos de transporte público (EMT, Valenbisi)
- Predicciones de precios futuros