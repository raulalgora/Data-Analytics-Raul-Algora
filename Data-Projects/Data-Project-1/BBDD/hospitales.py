import requests
from collections import defaultdict
import psycopg2

def obtener_todos_hospitales(url):
    """
    Obtiene TODOS los registros de hospitales desde la API de Valencia.
    """
    hospitales_total = []
    try:
        parametros = {
            'limit': 100,
            'offset': 0
        }
        
        while True:
            respuesta = requests.get(url, params=parametros)
            respuesta.raise_for_status()
            
            datos = respuesta.json()
            
            hospitales_parcial = [
                {
                    'nombre': hospital['nombre'], 
                    'distrito': hospital['coddistrit'],
                    'financiacion': hospital.get('financiaci', 'No especificado')
                } 
                for hospital in datos['results'] 
                if hospital.get('tipo') == 'Hospital'
            ]
            
            hospitales_total.extend(hospitales_parcial)
            
            if len(datos['results']) < parametros['limit']:
                break
            
            parametros['offset'] += parametros['limit']
        
        return hospitales_total
    
    except requests.RequestException as e:
        print(f"Error al obtener datos de la API: {e}")
        return []

def agrupar_hospitales_por_distrito(hospitales):
    """
    Agrupa los hospitales por distrito y estructura los datos.
    """
    distritos = defaultdict(lambda: {
        'distrito_id': None,
        'total_hospitales': 0,
        'nombres_hospitales': '',
        'tipos_financiacion': ''
    })
    
    for hospital in hospitales:
        distrito = hospital['distrito']
        
        distritos[distrito]['distrito_id'] = distrito
        distritos[distrito]['total_hospitales'] += 1
        
        # Concatenar los nombres de los hospitales
        if distritos[distrito]['nombres_hospitales']:
            distritos[distrito]['nombres_hospitales'] += ', '  # Separar con coma
        distritos[distrito]['nombres_hospitales'] += hospital['nombre']
        
        # Concatenar los tipos de financiación en un string
        financiacion = hospital['financiacion']
        if financiacion not in distritos[distrito]['tipos_financiacion']:
            if distritos[distrito]['tipos_financiacion']:
                distritos[distrito]['tipos_financiacion'] += ', '  # Separar con coma
            distritos[distrito]['tipos_financiacion'] += financiacion
    
    return dict(distritos)

def enviar_a_postgres(data, db_config):
    """
    Envía los datos procesados a PostgreSQL, creando la tabla si no existe.
    """
    conn = None
    try:
        conn = psycopg2.connect(**db_config)
        cursor = conn.cursor()

        # Crear la tabla con la columna tipos_financiacion como TEXT
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS hospitales (
            distrito_id INTEGER PRIMARY KEY,
            total_hospitales INTEGER,
            nombres_hospitales TEXT,
            tipos_financiacion TEXT  -- Almacenamos como string simple
        );
        """)

        # Insertar los datos
        for distrito, datos in data.items():
            cursor.execute("""
            INSERT INTO hospitales (distrito_id, total_hospitales, nombres_hospitales, tipos_financiacion)
            VALUES (%s, %s, %s, %s)
            ON CONFLICT (distrito_id) DO UPDATE
            SET total_hospitales = EXCLUDED.total_hospitales,
                nombres_hospitales = EXCLUDED.nombres_hospitales,
                tipos_financiacion = EXCLUDED.tipos_financiacion;
            """, (
                datos['distrito_id'],
                datos['total_hospitales'],
                datos['nombres_hospitales'],  # Ya es un string
                datos['tipos_financiacion']   # Ya es un string
            ))
        
        conn.commit()
        print("Datos enviados correctamente a PostgreSQL.")
    except psycopg2.OperationalError as e:
        print(f"Error de conexión con PostgreSQL: {e}")
    except psycopg2.Error as e:
        print(f"Error al interactuar con la base de datos: {e}")
    finally:
        if conn:
            cursor.close()
            conn.close()

# URL del endpoint de la API de Valencia
url_api = 'https://valencia.opendatasoft.com/api/explore/v2.1/catalog/datasets/hospitales/records?'

# Configuración de la base de datos PostgreSQL
db_config = {
    'dbname': 'DISTRITOS',
    'user': 'postgres',
    'password': 'Welcome01',
    'host': 'postgres',
    'port': 5432
}

# Obtener la lista completa de hospitales
lista_hospitales = obtener_todos_hospitales(url_api)

# Agrupar hospitales por distrito
hospitales_por_distrito = agrupar_hospitales_por_distrito(lista_hospitales)

# Enviar los datos a PostgreSQL directamente sin guardar el JSON
enviar_a_postgres(hospitales_por_distrito, db_config)
