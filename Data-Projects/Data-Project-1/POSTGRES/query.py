import psycopg2



# Credenciales para conectarte a tu base de datos PostgreSQL
DB_HOST = "postgres"
DB_NAME = "DISTRITOS"
DB_USER = "postgres"
DB_PASSWORD = "Welcome01"
DB_PORT = "5432"  # Cambia este valor si usas un puerto diferente

# Consulta SQL que deseas ejecutar
QUERY = """
CREATE TABLE sqlazo_table AS (
	SELECT 
        cp.distrito_id, 
        a.name, 
        a.alqtbid12_m_vc_22, 
        v.variacion_anual, 
        h.total_hospitales,
        h.tipos_financiacion,
        bm.total_metro,
        COUNT(CASE WHEN c.regimen = 'PÚBLICO' THEN 1 END) AS total_colegios_publicos,
        COUNT(CASE WHEN c.regimen = 'PRIVADO' THEN 1 END) AS total_colegios_privados,
        COUNT(CASE WHEN c.regimen = 'CONCERTADO' THEN 1 END) AS total_colegios_concertados
	FROM codigos_postales cp
	LEFT JOIN colegios c ON cp.codigo_postal = c.codigo_postal
	LEFT JOIN alquiler a ON cp.distrito_id = a.distrito_id
	LEFT JOIN variacion_precio v ON a.name = v.name
	LEFT JOIN distritos_id d ON cp.distrito_id = d.distrito_id
	LEFT JOIN hospitales h ON d.distrito_id = h.distrito_id
	LEFT JOIN (
	    SELECT 
	        d.distrito_id, 
	        COUNT(bm.denominacion) AS total_metro
	    FROM distritos_id d
	    LEFT JOIN bocas_metro bm ON d.name = bm.distrito
	    GROUP BY d.distrito_id
	) bm ON d.distrito_id = bm.distrito_id
	GROUP BY 
	    cp.distrito_id, 
	    a.name, 
	    a.alqtbid12_m_vc_22, 
	    v.variacion_anual, 
	    d.name, 
	    h.total_hospitales, 
	    h.tipos_financiacion,
	    bm.total_metro
	ORDER BY cp.distrito_id ASC
);
"""

def execute_query():
    """
    Conecta a la base de datos PostgreSQL y ejecuta la consulta SQL.
    """
    try:
        # Conexión a la base de datos
        connection = psycopg2.connect(
            host=DB_HOST,
            database=DB_NAME,
            user=DB_USER,
            password=DB_PASSWORD,
            port=DB_PORT
        )
        cursor = connection.cursor()
        print("Conexión a la base de datos establecida.")

        # Ejecutar la consulta
        print("Ejecutando consulta SQL...")
        cursor.execute(QUERY)
        connection.commit()
        print("Consulta ejecutada con éxito. La tabla 'resumen_2' ha sido creada.")

    except Exception as e:
        print(f"Error al ejecutar la consulta: {e}")

    finally:
        # Cerrar la conexión
        if connection:
            cursor.close()
            connection.close()
            print("Conexión a la base de datos cerrada.")

if __name__ == "__main__":
    execute_query()
