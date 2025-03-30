import streamlit as st
import folium
from streamlit_folium import folium_static
import requests
import psycopg2

## Conexión a pgadmin4 (BD = DISTRITOS)
conn_target = psycopg2.connect(
    dbname="DISTRITOS",
    user="postgres",
    password="Welcome01",
    host="postgres",
    port="5432"
)

st.set_page_config(layout="wide")

## Requests a las capas del mapa
geojson_url_1 = "https://valencia.opendatasoft.com/api/v2/catalog/datasets/districtes-distritos/exports/geojson"
response_1 = requests.get(geojson_url_1)

geojson_url_2 = "https://valencia.opendatasoft.com/api/explore/v2.1/catalog/datasets/zonas-verdes/exports/geojson?lang=es&timezone=Europe%2FMadrid"
response_2 = requests.get(geojson_url_2)

## Funciones para colorear los distritos
def get_color(distrito):
    colores_distritos = {
        "EL PLA DEL REAL": "##FF0000",
        "EXTRAMURS": "#00CED1",
        "L'EIXAMPLE": "#FF6347",
        "ALGIROS": "#9400D3",
        "RASCANYA": "#2E8B57",
        "POBLATS DE L'OEST": "#DC143C",
        "L'OLIVERETA": "#556B2F",
        "POBLATS DEL NORD": "#00FF00",
        "BENICALAP": "#FF69B4",
        "LA SAIDIA": "#FFD700",
        "CAMINS AL GRAU": "#FF00FF",
        "BENIMACLET": "#00FFFF",
        "CAMPANAR": "#FFA500",
        "POBLATS MARITIMS": "#008080",
        "CIUTAT VELLA": "#800000",  
        "JESUS": "8A2BE2", 
        "QUATRE CARRERES": "#808000", 
        "POBLATS DEL SUD": "#0000FF",
        "PATRAIX": "#D2691E" 
    }
    if distrito in distritos_aptos:
        return colores_distritos.get(distrito, "#D3D3D3")
    return "#D3D3D3"

def style_function(feature, context=None):
    return {
        'fillColor': get_color(feature['properties']['nombre']), 
        'color': 'black',
        'weight': 1,
        'fillOpacity': 0.5
    }

def highlight_function(feature):
    return {
        'fillColor': get_color(feature['properties']['nombre']), 
        'color': 'white',
        'weight': 2,
        'fillOpacity': 0.7
    }


## Función para la capa de zonas verdes
def green_stripes_style(feature):
    return {
        'fillColor': 'green',
        'color': 'green',
        'weight': 2, 
        'fillOpacity': 0.2,
        'dashArray': '5,5'
    }

## Función para filtrar los ingresos mensuales netos
def obtener_distritos_aptos(ingreso_maximo):
    distritos_aptos = []
    cursor = conn_target.cursor()
    cursor.execute(
    """
    SELECT distrito_id, name, alqtbid12_m_vc_22
    FROM resumen_2
    where alqtbid12_m_vc_22 <= %s
    """, (0.4 * ingreso_maximo,))
    distritos_data = cursor.fetchall()
    for distrito_id, name, alquiler_mensual in distritos_data:
        distritos_aptos.append(name)
    cursor.close()
    return distritos_aptos

## Función para obtener los datos informativos para la caja
def datos_distritos():
    cursor = conn_target.cursor()
    cursor.execute("""
        SELECT distrito_id, name, alqtbid12_m_vc_22, variacion_anual, total_hospitales, tipos_financiacion, total_metro, total_colegios_publicos, total_colegios_privados, total_colegios_concertados
        FROM resumen_2
    """)
    distritos_data = cursor.fetchall()
    cursor.close()
    return distritos_data

## Montaje de la visualización en streamlit
if response_1.status_code == 200 and response_2.status_code == 200:
    geojson_data_1 = response_1.json()
    geojson_data_2 = response_2.json()

    col1, col2 = st.columns([1, 3])

    ## "Columna" de filtros (col1) = la parte izquierda de la app
    with col1:
        st.header("Filtros")
        selected_ingresos = st.slider("Selecciona tus ingresos mensuales netos", 0, 10000, 3000)

        st.header("Control de capas")
        show_districts = st.checkbox("Mostrar Distritos", value=True)
        show_green_zones = st.checkbox("Mostrar Zonas Verdes", value=True)

    ## "Columna" donde está el mapa        
    with col2:
        distritos_aptos = obtener_distritos_aptos(selected_ingresos)
        m = folium.Map(location=[39.4699, -0.3763], zoom_start=12)

        district_group = folium.FeatureGroup(name="Distritos")
        green_zone_group = folium.FeatureGroup(name="Zonas Verdes")

        # Caja de información del GeoJSON de distritos
        tooltip_1 = folium.features.GeoJsonTooltip(
            fields=['nombre'],
            aliases=['Distrito'],
            localize=True,
            sticky=False
        )
        folium.GeoJson(
            geojson_data_1,
            style_function=lambda feature: style_function(feature, distritos_aptos),
            highlight_function=highlight_function,
            tooltip=tooltip_1
        ).add_to(district_group)

        # Caja de información del GeoJSON de zonas verdes, te indica el tipo de zona
        tooltip_2 = folium.features.GeoJsonTooltip(
            fields=['nivel3'],
            aliases=['Zona Verde'],
            localize=True,
            sticky=False
        )
        folium.GeoJson(
            geojson_data_2,
            style_function=green_stripes_style,
            tooltip=tooltip_2
        ).add_to(green_zone_group)

        if show_districts:
            district_group.add_to(m)
        if show_green_zones:
            green_zone_group.add_to(m)

        folium_static(m, width=1200, height=800)

else:
    st.error("No se pudieron descargar los archivos GeoJSON.")


## Formato de márgenes
st.markdown(
    """
    <style>
    .main {
        max-width: 100%;
        padding: 0px;
    }
    .block-container {
        padding-top: 50px;
        padding-bottom: 0px;
    }
    </style>
    """,
    unsafe_allow_html=True
)


