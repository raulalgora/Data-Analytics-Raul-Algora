# Usar la imagen oficial de Python
FROM python:3.11-slim

# Establecer el directorio de trabajo
WORKDIR /app

# Copiar los archivos de requirements primero para aprovechar el cache de Docker
COPY requirements.txt .

# Instalar las dependencias
RUN pip install --no-cache-dir -r requirements.txt

# Copiar el código de la aplicación
COPY . .

# Exponer el puerto (aunque Cloud Run lo maneja automáticamente)
EXPOSE 8080

# Comando para ejecutar la aplicación
CMD ["python", "main.py"] 