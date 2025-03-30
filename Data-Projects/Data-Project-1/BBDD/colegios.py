import requests
import pandas as pd
import psycopg2
import json

# Configuración
api_url = "https://valencia.opendatasoft.com/api/explore/v2.1/catalog/datasets/centros-educativos-en-valencia/exports/json?lang=es&timezone=Europe%2FBerlin"

# Conexión a PostgreSQL
conn = psycopg2.connect(
    dbname="DISTRITOS",  # Cambia al nombre de tu base de datos
    user="postgres",
    password="Welcome01",
    host="postgres",
    port="5432"
)
cursor = conn.cursor()

# Crear tabla para colegios
create_table_query = """
CREATE TABLE IF NOT EXISTS colegios (
    id SERIAL PRIMARY KEY,
    nombre VARCHAR(255),
    codigo_postal VARCHAR(10),
    regimen VARCHAR(50)
);
"""
cursor.execute(create_table_query)
conn.commit()

# Función para obtener y limpiar datos
def fetch_and_clean_data(api_url):
    """
    Obtiene y limpia los datos de la API, conservando el nombre, código postal y régimen.
    """
    try:
        response = requests.get(api_url)
        response.raise_for_status()
        data = response.json()

        # Filtrar los datos necesarios
        filtered_data = [
            {
                "nombre": item.get("dlibre"),
                "codigo_postal": item.get("codpos"),
                "regimen": item.get("regimen")
            }
            for item in data
            if item.get("dlibre") and item.get("codpos")
        ]
        return filtered_data

    except requests.exceptions.RequestException as e:
        print(f"Error al conectar con la API: {e}")
        return []

# Función para guardar datos en PostgreSQL
def save_to_postgres(data, cursor):
    """
    Inserta los datos en la tabla PostgreSQL.
    """
    for record in data:
        nombre = record["nombre"]
        codigo_postal = record["codigo_postal"]
        regimen = record["regimen"]

        cursor.execute("""
            INSERT INTO colegios (nombre, codigo_postal, regimen)
            VALUES (%s, %s, %s)
        """, (nombre, codigo_postal, regimen))

    conn.commit()
    print("Datos insertados en PostgreSQL.")

# Obtener los datos de la API
data_cleaned = fetch_and_clean_data(api_url)

# Insertar los datos en PostgreSQL
if data_cleaned:
    save_to_postgres(data_cleaned, cursor)
else:
    print("No se encontraron datos procesados.")

# Cerrar la conexión
cursor.close()
conn.close()
