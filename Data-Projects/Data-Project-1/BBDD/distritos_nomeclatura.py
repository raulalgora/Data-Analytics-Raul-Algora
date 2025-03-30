import psycopg2

conn_target = psycopg2.connect(
    dbname="DISTRITOS",
    user="postgres",
    password="Welcome01",
    host="postgres",
    port="5432" 
)
cursor = conn_target.cursor()

table_distritos = """
CREATE TABLE IF NOT EXISTS distritos_id (
    distrito_id INTEGER PRIMARY KEY,
    name VARCHAR(255),
    CUDIS INTEGER
)
"""
cursor.execute(table_distritos)
conn_target.commit()

table_codigos_postales = """
CREATE TABLE IF NOT EXISTS codigos_postales (
    codigo_postal VARCHAR(10),
    distrito_id INTEGER,
    PRIMARY KEY (codigo_postal, distrito_id),
    FOREIGN KEY (distrito_id) REFERENCES distritos_id (distrito_id)
)
"""
cursor.execute(table_codigos_postales)
conn_target.commit()

distritos = [
    {
        'distrito_id': 1,
        'name': 'CIUTAT VELLA',
        'CUDIS': 4625001,
        'codigos_postales': ['46001', '46002', '46003']
    },
    {
        'distrito_id': 2,
        'name': "L'EIXAMPLE",
        'CUDIS': 4625002,
        'codigos_postales': ['46006', '46004', '46005']
    },
    {
        'distrito_id': 3,
        'name': 'EXTRAMURS',
        'CUDIS': 4625003,
        'codigos_postales': ['46007', '46008']
    },
    {
        'distrito_id': 4,
        'name': 'CAMPANAR',
        'CUDIS': 4625004,
        'codigos_postales': ['46015', '46009']
    },
    {
        'distrito_id': 5,
        'name': 'LA SAIDIA',
        'CUDIS': 4625005,
        'codigos_postales': ['46009', '46010', '46019']
    },
    {
        'distrito_id': 6,
        'name': 'EL PLA DEL REAL',
        'CUDIS': 4625006,
        'codigos_postales': ['46010', '46021']
    },
    {
        'distrito_id': 7,
        'name': "L'OLIVERETA",
        'CUDIS': 4625007,
        'codigos_postales': ['46014', '46018']
    },
    {
        'distrito_id': 8,
        'name': 'PATRAIX',
        'CUDIS': 4625008,
        'codigos_postales': ['46018', '46017', '46015']
    },
    {
        'distrito_id': 9,
        'name': 'JESUS',
        'CUDIS': 4625009,
        'codigos_postales': ['46007', '46017', '46006']
    },
    {
        'distrito_id': 10,
        'name': 'QUATRE CARRERES',
        'CUDIS': 4625010,
        'codigos_postales': ['46006', '46026', '46013']
    },
    {
        'distrito_id': 11,
        'name': 'POBLATS MARITIMS',
        'CUDIS': 4625011,
        'codigos_postales': ['46024', '46011']
    },
    {
        'distrito_id': 12,
        'name': 'CAMINS AL GRAU',
        'CUDIS': 4625012,
        'codigos_postales': ['46022', '46023']
    },
    {
        'distrito_id': 13,
        'name': 'ALGIROS',
        'CUDIS': 4625013,
        'codigos_postales': ['46021', '46022']
    },
    {
        'distrito_id': 14,
        'name': 'BENIMACLET',
        'CUDIS': 4625014,
        'codigos_postales': ['46020', '46022']
    },
    {
        'distrito_id': 15,
        'name': 'RASCANYA',
        'CUDIS': 4625015,
        'codigos_postales': ['46019', '46025']
    },
    {
        'distrito_id': 16,
        'name': 'BENICALAP',
        'CUDIS': 4625016,
        'codigos_postales': ['46015', '46035']
    },
    {
        'distrito_id': 17,
        'name': 'POBLES DEL NORD',
        'CUDIS': 4625017,
        'codigos_postales': ['46016']
    },
    {
        'distrito_id': 18,
        'name': "POBLES DE L'OEST",
        'CUDIS': 4625018,
        'codigos_postales': ['46035']
    },
    {
        'distrito_id': 19,
        'name': 'POBLES DEL SUD',
        'CUDIS': 4625019,
        'codigos_postales': ['46012']
    }
]


# Insertar los datos en la tabla distritos
for distrito in distritos:
    cursor.execute(
        """
        INSERT INTO distritos_id(distrito_id, name, CUDIS)
        VALUES (%s, %s, %s)
        ON CONFLICT (distrito_id) DO NOTHING
        """,
        (distrito['distrito_id'], distrito['name'], distrito['CUDIS'])
    )

# Insertar los datos en la tabla codigos_postales
for distrito in distritos:
    for codigo_postal in distrito['codigos_postales']:
        cursor.execute(
            """
            INSERT INTO codigos_postales (codigo_postal, distrito_id)
            VALUES (%s, %s)
            ON CONFLICT (codigo_postal, distrito_id) DO NOTHING
            """,
            (codigo_postal, distrito['distrito_id'])
        )


conn_target.commit()

cursor.close()
conn_target.close()
