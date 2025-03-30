import pandas as pd
import requests
import openpyxl
import json
import psycopg2
from io import BytesIO

conn_target = psycopg2.connect(
    dbname="DISTRITOS",
    user="postgres",
    password="Welcome01",
    host="postgres",
    port="5432" 
)

cursor = conn_target.cursor()

table_alquiler = """
CREATE TABLE IF NOT EXISTS alquiler (
    distrito_id INTEGER,
    name VARCHAR(255),
    ALQTBID12_M_VC_22 FLOAT,
    ALQTBID12_M_VU_22 FLOAT,
    CONSTRAINT unique_distrito_name UNIQUE (distrito_id, name)
)
"""
cursor.execute(table_alquiler)
conn_target.commit()

# URL del archivo Excel
excel_url = "https://cdn.mivau.gob.es/portal-web-mivau/vivienda/serpavi/2024-05-07_bd_sistema-indices-alquiler-vivienda_2011-2022.xlsx"

# Descargar el archivo Excel directamente en memoria
response = requests.get(excel_url)
excel_file = BytesIO(response.content)  # Usamos BytesIO para cargarlo en memoria

# Leer las hojas del Excel directamente desde el archivo en memoria
df_header = pd.read_excel(excel_file, 
                          sheet_name="Distritos",
                          usecols="D, E, HZ, IC",
                          nrows=1,
                          header=0)

df_data = pd.read_excel(excel_file, 
                   sheet_name="Distritos", 
                   usecols="D, E, HZ, IC",
                   skiprows=8992,
                   nrows=19,
                   header=0
                   )

df_data.columns = df_header.columns

cudis_name = {
    4625001: {'name': 'CIUTAT VELLA', 'distrito_id': 1},
    4625002: {'name': "L'EIXAMPLE", 'distrito_id': 2},
    4625003: {'name': 'EXTRAMURS', 'distrito_id': 3},
    4625004: {'name': 'CAMPANAR', 'distrito_id': 4},
    4625005: {'name': 'LA SAIDIA', 'distrito_id': 5},
    4625006: {'name': 'EL PLA DEL REAL', 'distrito_id': 6},
    4625007: {'name': "L'OLIVERETA", 'distrito_id': 7},
    4625008: {'name': 'PATRAIX', 'distrito_id': 8},
    4625009: {'name': 'JESUS', 'distrito_id': 9},
    4625010: {'name': 'QUATRE CARRERES', 'distrito_id': 10},
    4625011: {'name': 'POBLATS MARITIMS', 'distrito_id': 11},
    4625012: {'name': 'CAMINS AL GRAU', 'distrito_id': 12},
    4625013: {'name': 'ALGIROS', 'distrito_id': 13},
    4625014: {'name': 'BENIMACLET', 'distrito_id': 14},
    4625015: {'name': 'RASCANYA', 'distrito_id': 15},
    4625016: {'name': 'BENICALAP', 'distrito_id': 16},
    4625017: {'name': 'POBLES DEL NORD', 'distrito_id': 17},
    4625018: {'name': "POBLES DE L'OEST", 'distrito_id': 18},
    4625019: {'name': 'POBLES DEL SUD', 'distrito_id': 19}
}

df_data['CUDIS'] = df_data['CUDIS'].map(cudis_name).fillna(df_data['CUDIS'])

grouped_data = df_data[['LITMUN', 'CUDIS', 'ALQTBID12_M_VC_22', 'ALQTBID12_M_VU_22']].groupby('LITMUN').apply(
    lambda group: group[['CUDIS', 'ALQTBID12_M_VC_22', 'ALQTBID12_M_VU_22']].to_dict(orient='records')
).reset_index(name='cudis_data')

for municipality in grouped_data['cudis_data']:
    for data in municipality:
        cursor.execute(
            """
            INSERT INTO alquiler (distrito_id, name, ALQTBID12_M_VC_22, ALQTBID12_M_VU_22)
            VALUES (%s, %s, %s, %s)
            ON CONFLICT (distrito_id, name) DO NOTHING
            """,
            (data['CUDIS']['distrito_id'], data['CUDIS']['name'], data['ALQTBID12_M_VC_22'], data['ALQTBID12_M_VU_22'])
        )
        conn_target.commit()

cursor.close()
conn_target.close()

