import pandas as pd
from bs4 import BeautifulSoup
import json
from unidecode import unidecode
import psycopg2

conn_target = psycopg2.connect(
    dbname="DISTRITOS",
    user="postgres",
    password="Welcome01",
    host="postgres",
    port="5432" 
)

cursor = conn_target.cursor()
table_alquiler = """
CREATE TABLE IF NOT EXISTS variacion_precio (
    Precio_m2_nov_24 VARCHAR(255),
    Variacion_mes VARCHAR(255),
    Variacion_tri VARCHAR(255),
    Variacion_anual VARCHAR(255),
    Maximo_precio VARCHAR(255),
    Variacion_percentil VARCHAR(255),
    name VARCHAR(255)
    )
"""
cursor.execute(table_alquiler)
conn_target.commit()

html_content = """
<table class="js-scroll-header component-table table" data-fixed-first-row="1" data-striping="1"><thead class="fix-thead"><tr class="table__cell"><th class="table__header"> <span>Localización</span></th><th class="table__header"> <span>Precio m2 nov 2024</span></th><th class="table__header"> <span>Variación mensual</span></th><th class="table__header"> <span>Variación trimestral</span></th><th class="table__header"> <span>Variación anual</span></th><th class="table__header"> <span>Máximo histórico</span></th><th class="table__header"> <span>Variación máximo</span></th></tr></thead><tbody><tr class="table__row"><td data-sortable="València" class="table__cell">València</td><td data-sortable="14.6725" class="table__cell">14,7 €/m2</td><td data-sortable="1.58478" class="table__cell table__cell--green">+ 1,6 %</td><td data-sortable="3.05676" class="table__cell table__cell--green">+ 3,1 %</td><td data-sortable="12.0868" class="table__cell table__cell--green">+ 12,1 %</td><td data-sortable="14.6725" class="table__cell">14,7 €/m2 nov 2024</td><td data-sortable="0" class="table__cell">0,0 %</td></tr><tr class="table__row"><td data-sortable="Algirós" class="table__cell"><a href="https://www.idealista.com/sala-de-prensa/informes-precio-vivienda/alquiler/comunitat-valenciana/valencia-valencia/valencia/algiros/" class="icon-elbow" title="Algirós">Algirós</a></td><td data-sortable="13.4615" class="table__cell">13,5 €/m2</td><td data-sortable="0.961502" class="table__cell table__cell--green">+ 1,0 %</td><td data-sortable="0.941819" class="table__cell table__cell--green">+ 0,9 %</td><td data-sortable="13.0762" class="table__cell table__cell--green">+ 13,1 %</td><td data-sortable="13.4615" class="table__cell">13,5 €/m2 nov 2024</td><td data-sortable="0" class="table__cell">0,0 %</td></tr><tr class="table__row"><td data-sortable="Benicalap" class="table__cell"><a href="https://www.idealista.com/sala-de-prensa/informes-precio-vivienda/alquiler/comunitat-valenciana/valencia-valencia/valencia/benicalap/" class="icon-elbow" title="Benicalap">Benicalap</a></td><td data-sortable="12.0843" class="table__cell">12,1 €/m2</td><td data-sortable="-3.94344" class="table__cell table__cell--red">- 3,9 %</td><td data-sortable="-4.73401" class="table__cell table__cell--red">- 4,7 %</td><td data-sortable="7.18543" class="table__cell table__cell--green">+ 7,2 %</td><td data-sortable="12.7371" class="table__cell">12,7 €/m2 sep 2024</td><td data-sortable="-5.1251854817816" class="table__cell table__cell--red">- 5,1 %</td></tr><tr class="table__row"><td data-sortable="Benimaclet" class="table__cell"><a href="https://www.idealista.com/sala-de-prensa/informes-precio-vivienda/alquiler/comunitat-valenciana/valencia-valencia/valencia/benimaclet/" class="icon-elbow" title="Benimaclet">Benimaclet</a></td><td data-sortable="12.9656" class="table__cell">13,0 €/m2</td><td data-sortable="0.550618" class="table__cell table__cell--green">+ 0,6 %</td><td data-sortable="0.843892" class="table__cell table__cell--green">+ 0,8 %</td><td data-sortable="6.36259" class="table__cell table__cell--green">+ 6,4 %</td><td data-sortable="13.1125" class="table__cell">13,1 €/m2 mayo 2024</td><td data-sortable="-1.1203050524309" class="table__cell table__cell--red">- 1,1 %</td></tr><tr class="table__row"><td data-sortable="Camins al Grau" class="table__cell"><a href="https://www.idealista.com/sala-de-prensa/informes-precio-vivienda/alquiler/comunitat-valenciana/valencia-valencia/valencia/camins-al-grau/" class="icon-elbow" title="Camins al Grau">Camins al Grau</a></td><td data-sortable="14.9534" class="table__cell">15,0 €/m2</td><td data-sortable="1.8742" class="table__cell table__cell--green">+ 1,9 %</td><td data-sortable="6.50873" class="table__cell table__cell--green">+ 6,5 %</td><td data-sortable="13.5698" class="table__cell table__cell--green">+ 13,6 %</td><td data-sortable="14.9534" class="table__cell">15,0 €/m2 nov 2024</td><td data-sortable="0" class="table__cell">0,0 %</td></tr><tr class="table__row"><td data-sortable="Campanar" class="table__cell"><a href="https://www.idealista.com/sala-de-prensa/informes-precio-vivienda/alquiler/comunitat-valenciana/valencia-valencia/valencia/campanar/" class="icon-elbow" title="Campanar">Campanar</a></td><td data-sortable="14.8238" class="table__cell">14,8 €/m2</td><td data-sortable="2.50244" class="table__cell table__cell--green">+ 2,5 %</td><td data-sortable="9.26768" class="table__cell table__cell--green">+ 9,3 %</td><td data-sortable="11.8592" class="table__cell table__cell--green">+ 11,9 %</td><td data-sortable="15.0161" class="table__cell">15,0 €/m2 mayo 2024</td><td data-sortable="-1.2806254620041" class="table__cell table__cell--red">- 1,3 %</td></tr><tr class="table__row"><td data-sortable="Ciutat Vella" class="table__cell"><a href="https://www.idealista.com/sala-de-prensa/informes-precio-vivienda/alquiler/comunitat-valenciana/valencia-valencia/valencia/ciutat-vella/" class="icon-elbow" title="Ciutat Vella">Ciutat Vella</a></td><td data-sortable="18.2203" class="table__cell">18,2 €/m2</td><td data-sortable="1.05042" class="table__cell table__cell--green">+ 1,1 %</td><td data-sortable="-0.679208" class="table__cell table__cell--red">- 0,7 %</td><td data-sortable="9.32158" class="table__cell table__cell--green">+ 9,3 %</td><td data-sortable="18.3449" class="table__cell">18,3 €/m2 ago 2024</td><td data-sortable="-0.67920784523218" class="table__cell table__cell--red">- 0,7 %</td></tr><tr class="table__row"><td data-sortable="El Pla del Real" class="table__cell"><a href="https://www.idealista.com/sala-de-prensa/informes-precio-vivienda/alquiler/comunitat-valenciana/valencia-valencia/valencia/el-pla-del-real/" class="icon-elbow" title="El Pla del Real">El Pla del Real</a></td><td data-sortable="13.6054" class="table__cell">13,6 €/m2</td><td data-sortable="-1.69011" class="table__cell table__cell--red">- 1,7 %</td><td data-sortable="-0.680362" class="table__cell table__cell--red">- 0,7 %</td><td data-sortable="1.38908" class="table__cell table__cell--green">+ 1,4 %</td><td data-sortable="14.0625" class="table__cell">14,1 €/m2 sep 2024</td><td data-sortable="-3.2504888888889" class="table__cell table__cell--red">- 3,3 %</td></tr><tr class="table__row"><td data-sortable="Extramurs" class="table__cell"><a href="https://www.idealista.com/sala-de-prensa/informes-precio-vivienda/alquiler/comunitat-valenciana/valencia-valencia/valencia/extramurs/" class="icon-elbow" title="Extramurs">Extramurs</a></td><td data-sortable="15.0943" class="table__cell">15,1 €/m2</td><td data-sortable="0.628667" class="table__cell table__cell--green">+ 0,6 %</td><td data-sortable="4.45449" class="table__cell table__cell--green">+ 4,5 %</td><td data-sortable="16.7025" class="table__cell table__cell--green">+ 16,7 %</td><td data-sortable="15.0943" class="table__cell">15,1 €/m2 nov 2024</td><td data-sortable="0" class="table__cell">0,0 %</td></tr><tr class="table__row"><td data-sortable="Jesús" class="table__cell"><a href="https://www.idealista.com/sala-de-prensa/informes-precio-vivienda/alquiler/comunitat-valenciana/valencia-valencia/valencia/jesus/" class="icon-elbow" title="Jesús">Jesús</a></td><td data-sortable="12.7226" class="table__cell">12,7 €/m2</td><td data-sortable="3.18661" class="table__cell table__cell--green">+ 3,2 %</td><td data-sortable="4.56903" class="table__cell table__cell--green">+ 4,6 %</td><td data-sortable="23.1831" class="table__cell table__cell--green">+ 23,2 %</td><td data-sortable="12.7226" class="table__cell">12,7 €/m2 nov 2024</td><td data-sortable="0" class="table__cell">0,0 %</td></tr><tr class="table__row"><td data-sortable="L'Eixample" class="table__cell"><a href="https://www.idealista.com/sala-de-prensa/informes-precio-vivienda/alquiler/comunitat-valenciana/valencia-valencia/valencia/leixample/" class="icon-elbow" title="L'Eixample">L'Eixample</a></td><td data-sortable="16.6667" class="table__cell">16,7 €/m2</td><td data-sortable="0.0240057" class="table__cell">0,0 %</td><td data-sortable="-1.96059" class="table__cell table__cell--red">- 2,0 %</td><td data-sortable="13.3334" class="table__cell table__cell--green">+ 13,3 %</td><td data-sortable="17" class="table__cell">17,0 €/m2 ago 2024</td><td data-sortable="-1.9605882352941" class="table__cell table__cell--red">- 2,0 %</td></tr><tr class="table__row"><td data-sortable="L'Olivereta" class="table__cell"><a href="https://www.idealista.com/sala-de-prensa/informes-precio-vivienda/alquiler/comunitat-valenciana/valencia-valencia/valencia/lolivereta/" class="icon-elbow" title="L'Olivereta">L'Olivereta</a></td><td data-sortable="13.0586" class="table__cell">13,1 €/m2</td><td data-sortable="2.52251" class="table__cell table__cell--green">+ 2,5 %</td><td data-sortable="5.19422" class="table__cell table__cell--green">+ 5,2 %</td><td data-sortable="20.429" class="table__cell table__cell--green">+ 20,4 %</td><td data-sortable="13.0586" class="table__cell">13,1 €/m2 nov 2024</td><td data-sortable="0" class="table__cell">0,0 %</td></tr><tr class="table__row"><td data-sortable="La Saïdia" class="table__cell"><a href="https://www.idealista.com/sala-de-prensa/informes-precio-vivienda/alquiler/comunitat-valenciana/valencia-valencia/valencia/la-saidia/" class="icon-elbow" title="La Saïdia">La Saïdia</a></td><td data-sortable="13.3912" class="table__cell">13,4 €/m2</td><td data-sortable="2.90158" class="table__cell table__cell--green">+ 2,9 %</td><td data-sortable="1.49154" class="table__cell table__cell--green">+ 1,5 %</td><td data-sortable="11.4151" class="table__cell table__cell--green">+ 11,4 %</td><td data-sortable="13.3912" class="table__cell">13,4 €/m2 nov 2024</td><td data-sortable="0" class="table__cell">0,0 %</td></tr><tr class="table__row"><td data-sortable="Patraix" class="table__cell"><a href="https://www.idealista.com/sala-de-prensa/informes-precio-vivienda/alquiler/comunitat-valenciana/valencia-valencia/valencia/patraix/" class="icon-elbow" title="Patraix">Patraix</a></td><td data-sortable="12.3529" class="table__cell">12,4 €/m2</td><td data-sortable="0.241822" class="table__cell table__cell--green">+ 0,2 %</td><td data-sortable="6.82481" class="table__cell table__cell--green">+ 6,8 %</td><td data-sortable="14.5973" class="table__cell table__cell--green">+ 14,6 %</td><td data-sortable="12.3529" class="table__cell">12,4 €/m2 nov 2024</td><td data-sortable="0" class="table__cell">0,0 %</td></tr><tr class="table__row"><td data-sortable="Poblats Marítims" class="table__cell"><a href="https://www.idealista.com/sala-de-prensa/informes-precio-vivienda/alquiler/comunitat-valenciana/valencia-valencia/valencia/poblats-maritims/" class="icon-elbow" title="Poblats Marítims">Poblats Marítims</a></td><td data-sortable="14.9868" class="table__cell">15,0 €/m2</td><td data-sortable="1.63781" class="table__cell table__cell--green">+ 1,6 %</td><td data-sortable="3.20635" class="table__cell table__cell--green">+ 3,2 %</td><td data-sortable="8.26266" class="table__cell table__cell--green">+ 8,3 %</td><td data-sortable="14.9868" class="table__cell">15,0 €/m2 nov 2024</td><td data-sortable="0" class="table__cell">0,0 %</td></tr><tr class="table__row"><td data-sortable="Quatre Carreres" class="table__cell"><a href="https://www.idealista.com/sala-de-prensa/informes-precio-vivienda/alquiler/comunitat-valenciana/valencia-valencia/valencia/quatre-carreres/" class="icon-elbow" title="Quatre Carreres">Quatre Carreres</a></td><td data-sortable="14.5051" class="table__cell">14,5 €/m2</td><td data-sortable="0.669739" class="table__cell table__cell--green">+ 0,7 %</td><td data-sortable="-1.43112" class="table__cell table__cell--red">- 1,4 %</td><td data-sortable="14.9165" class="table__cell table__cell--green">+ 14,9 %</td><td data-sortable="14.7157" class="table__cell">14,7 €/m2 ago 2024</td><td data-sortable="-1.4311245812296" class="table__cell table__cell--red">- 1,4 %</td></tr><tr class="table__row"><td data-sortable="Rascanya" class="table__cell"><a href="https://www.idealista.com/sala-de-prensa/informes-precio-vivienda/alquiler/comunitat-valenciana/valencia-valencia/valencia/rascanya/" class="icon-elbow" title="Rascanya">Rascanya</a></td><td data-sortable="13.2401" class="table__cell">13,2 €/m2</td><td data-sortable="1.16213" class="table__cell table__cell--green">+ 1,2 %</td><td data-sortable="5.9208" class="table__cell table__cell--green">+ 5,9 %</td><td data-sortable="22.3748" class="table__cell table__cell--green">+ 22,4 %</td><td data-sortable="13.2401" class="table__cell">13,2 €/m2 nov 2024</td><td data-sortable="0" class="table__cell">0,0 %</td></tr></tbody></table>
"""


soup = BeautifulSoup(html_content, 'html.parser')
table = soup.find('table')

if table:
    table_data = []
    headers = [header.text.strip() for header in table.find_all('th')]
    for row in table.find_all('tr'):
        cols = row.find_all(['th', 'td'])
        cols = [col.text.strip() for col in cols]
        
        if len(cols) > 1:
            row_data = dict(zip(headers, cols))
            table_data.append(row_data)

## Convertir en json
    json_data = json.dumps(table_data, indent=4, ensure_ascii=False)

## Guardar el JSON en un archivo
    # with open("variaciones_precios.json", "w", encoding="utf-8") as json_file:
    #     json_file.write(json_data)

#     print("JSON generado.")
# else:
#     print("No ha funcionado.")

# with open('variaciones_precios.json', 'r') as json_file:
#     variaciones_data = json.load(json_file)

    for item in table_data:
            # Renombrar 'Localización' a 'name'
            if 'Localización' in item:
                item['name'] = item.pop('Localización')

            # Convertir todos los valores a mayúsculas y quitar tildes
            for key, value in item.items():
                item[key] = unidecode(value.upper())
        
# with open('tabla_datos.json', 'w', encoding='utf-8') as f:
#         json.dump(table_data, f, ensure_ascii=False, indent=4)
# print("El archivo JSON se ha guardado como 'tabla_datos.json'.")

    for item in table_data:
        precio_m2 = item.get('Precio m2 nov 2024', None)
        variacion_mes = item.get('Variación mensual', None)
        variacion_tri = item.get('Variación trimestral', None)
        variacion_anual = item.get('Variación anual', None)
        maximo_precio = item.get('Máximo histórico', None)
        variacion_percentil = item.get('Variación máximo', None),
        name = item.get('name',None)


        insert_query = """
            INSERT INTO variacion_precio (Precio_m2_nov_24, Variacion_mes, Variacion_tri, Variacion_anual, Maximo_precio, Variacion_percentil,name)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            """
        cursor.execute(insert_query, (precio_m2, variacion_mes, variacion_tri, variacion_anual, maximo_precio, variacion_percentil, name))

    conn_target.commit()

cursor.close()
conn_target.close()

print("Los datos se han insertado correctamente en la base de datos.")

