import requests
import geopandas as gpd
from shapely.geometry import Point, shape

# URLs de las APIs
URL_DISTRITOS = "https://valencia.opendatasoft.com/api/explore/v2.1/catalog/datasets/districtes-distritos/records?limit=20"  # Reemplaza con la URL real de distritos
URL_BOCAS = "https://valencia.opendatasoft.com/api/explore/v2.1/catalog/datasets/fgv-bocas/records?limit=20"  # Reemplaza con la URL real de bocas de metro

# Función para obtener datos de la API
def fetch_data_from_api(api_url):
    """
    Descarga datos desde una API y los devuelve como un diccionario.
    """
    try:
        response = requests.get(api_url)
        response.raise_for_status()  # Verifica errores HTTP
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error al conectar con la API: {e}")
        return {}

# Obtener datos de las APIs
distritos_data = fetch_data_from_api(URL_DISTRITOS)
bocas_data = fetch_data_from_api(URL_BOCAS)

# Verificar que los datos tienen el formato esperado
if "results" not in distritos_data or "results" not in bocas_data:
    raise ValueError("Las APIs no devolvieron el formato esperado (campo 'results' no encontrado).")

# Crear un GeoDataFrame a partir de los distritos
distritos_geometries = [
    {
        "geometry": shape(distrito["geo_shape"]["geometry"]),
        "nombre": distrito["nombre"]  # Asegúrate de que "nombre" corresponde al campo correcto en la API
    }
    for distrito in distritos_data["results"]
    if "geo_shape" in distrito and "geometry" in distrito["geo_shape"]
]
distritos = gpd.GeoDataFrame(distritos_geometries)
distritos.set_crs(epsg=4326, inplace=True)  # Asegurar sistema de coordenadas WGS84

# Crear un GeoDataFrame a partir de las bocas de metro
bocas_geometries = [
    {
        "geometry": Point(boca["geo_point_2d"]["lon"], boca["geo_point_2d"]["lat"]),
        "denominacion": boca["denominacion"]
    }
    for boca in bocas_data["results"]
    if "geo_point_2d" in boca
]
bocas = gpd.GeoDataFrame(bocas_geometries)
bocas.set_crs(epsg=4326, inplace=True)  # Asegurar sistema de coordenadas WGS84

# Función para encontrar el distrito de una boca de metro
def encontrar_distrito(boca, distritos):
    """
    Determina en qué distrito se encuentra una boca de metro.
    """
    for _, distrito in distritos.iterrows():
        if distrito["geometry"].contains(boca["geometry"]):
            return distrito["nombre"]  # Cambia "nombre" si el campo es diferente
    return "Sin distrito"

# Asignar distritos a las bocas de metro
bocas["distrito"] = bocas.apply(lambda boca: encontrar_distrito(boca, distritos), axis=1)

# Exportar los datos enriquecidos a un JSON
output_file = "bocas_con_distritos.json"
bocas.to_file(output_file, driver="GeoJSON")
print(f"Datos exportados a {output_file}")
