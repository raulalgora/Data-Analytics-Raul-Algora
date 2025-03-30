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
    FROM sqlazo_table
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
        FROM sqlazo_table
    """)
    distritos_data = cursor.fetchall()
    cursor.close() 
    distritos_dict = {}
    for distrito in distritos_data:
        distritos_dict[distrito[1]] = distrito
    return distritos_dict

distritos_dict = datos_distritos()
print(distritos_dict)


## Montaje de la visualización en streamlit
st.set_page_config(layout="wide")
## Requests a las capas del mapa
geojson_url_1 = "https://valencia.opendatasoft.com/api/v2/catalog/datasets/districtes-distritos/exports/geojson"
response_1 = requests.get(geojson_url_1)
geojson_url_2 = "https://valencia.opendatasoft.com/api/explore/v2.1/catalog/datasets/zonas-verdes/exports/geojson?lang=es&timezone=Europe%2FMadrid"
response_2 = requests.get(geojson_url_2)

if response_1.status_code == 200 and response_2.status_code == 200:
    geojson_data_1 = response_1.json()
    geojson_data_2 = response_2.json()

    col1, col2 = st.columns([1, 3])

    ## "Columna" de filtros (col1) = la parte izquierda de la app
    with col1:
        st.markdown("<h2>Filtros</h2>", unsafe_allow_html=True)
        st.markdown(
        """
        <style>
        .tooltip {
            position: relative;
            display: inline-block;
            cursor: pointer;
            font-size: 13px;
            color: #0073e6;
        }
        .tooltip .tooltiptext {
            visibility: hidden;
            width: 500px;
            background-color: #555;
            color: #fff;
            text-align: center;
            border-radius: 5px;
            padding: 4px;
            position: absolute;
            z-index: 1;
            bottom: 125%;
            left: 50%;
            margin-left: -100px; /* Center the tooltip */
            opacity: 0;
            transition: opacity 0.3s;
        }
        .tooltip:hover .tooltiptext {
            visibility: visible;
            opacity: 1;
        }
        </style>
        <div class="tooltip">Seleccione tus ingresos mensuales netos
            <span class="tooltiptext">Este filtro asegura que el alquiler no supere el 40% de tus ingresos mensuales netos.</span>
        </div>
        """,
        unsafe_allow_html=True
    )
        selected_ingresos = st.slider("",0, 10000, 3000)
        
        st.markdown('<h3 style="font-size: 18px;">Control de capas</h3>', unsafe_allow_html=True)
        show_districts = st.checkbox("Mostrar Distritos", value=True)
        show_green_zones = st.checkbox("Mostrar Zonas Verdes", value=True)

        
    ## "Columna" donde está el mapa        
    with col2:
        distritos_aptos = obtener_distritos_aptos(selected_ingresos)
        m = folium.Map(location=[39.4699, -0.3763], zoom_start=12)

        district_group = folium.FeatureGroup(name="Distritos")
        green_zone_group = folium.FeatureGroup(name="Zonas Verdes")

        # Caja de información del GeoJSON de distritos
        for feature in geojson_data_1['features']:
            nombre_distrito = feature['properties']['nombre']
        
            # Encontrar el distrito correspondiente en los datos de la base de datos
            if nombre_distrito in distritos_dict:
                distrito = distritos_dict[nombre_distrito]
                
                # Modificar las propiedades del GeoJSON para incluir los datos del distrito
                feature['properties']['alquiler_mensual'] = distrito[2]
                feature['properties']['variacion_anual'] = distrito[3]
                feature['properties']['total_hospitales'] = distrito[4]
                feature['properties']['tipos_financiacion'] = distrito[5]
                feature['properties']['total_metro'] = distrito[6]
                feature['properties']['total_colegios_publicos'] = distrito[7]
                feature['properties']['total_colegios_privados'] = distrito[8]
                feature['properties']['total_colegios_concertados'] = distrito[9]

        # Ahora, puedes usar GeoJsonTooltip con los campos que has añadido en las propiedades
        tooltip_1 = folium.features.GeoJsonTooltip(
            fields=['nombre', 'alquiler_mensual', 'variacion_anual', 'total_colegios_publicos', 'total_colegios_privados', 'total_colegios_concertados', 'total_hospitales', 'tipos_financiacion', 
                        'total_metro'],
            aliases=['Distrito', 'Alquiler Mensual (2022)', 'Variación Anual (2024)', 'Colegios Públicos', 'Colegios Privados', 'Colegios Concertados', 'Hospitales', 'Tipos de hospitales', 
                        'Parada de metro'],
            localize=True,
            sticky=False
            )

        # Añadir el GeoJSON al mapa
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
    body, .main {
        margin: 0;
        padding: 0;
        overflow: hidden;
        height: 100vh;
    }
    .block-container {
        padding-top: 50px;
        padding-bottom: 0px;
    }
    .css-18e3th9 {
        height: 100%;
        overflow: hidden;
    }
    </style>
    """,
    unsafe_allow_html=True
)


