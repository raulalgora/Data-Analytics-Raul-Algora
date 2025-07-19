# Usa una imagen base oficial de Python. 'slim' es una versión ligera.
FROM python:3.11-slim

# Establece el directorio de trabajo dentro del contenedor.
WORKDIR /app

# Copia primero el archivo de requerimientos.
# Esto es una optimización: si no cambias los requerimientos, Docker reutilizará
# esta capa en futuras compilaciones, haciéndolas mucho más rápidas.
COPY requirements.txt ./

# Instala las dependencias. '--no-cache-dir' mantiene la imagen pequeña.
RUN pip install --no-cache-dir -r requirements.txt

# Ahora copia el resto del código de tu aplicación al contenedor.
COPY . .

# Expone el puerto que usará Streamlit. Cloud Run le pasará el puerto 8080 por defecto.
EXPOSE 8080

# El comando para ejecutar la aplicación.
# Usa la variable de entorno $PORT que Cloud Run proporciona automáticamente.
# Las flags adicionales son importantes para que Streamlit funcione correctamente detrás del proxy de Cloud Run.
CMD ["streamlit", "run", "app.py", "--server.port", "8080", "--server.enableCORS", "false", "--server.enableXsrfProtection", "false"]