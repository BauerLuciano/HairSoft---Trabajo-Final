import math, requests
from decimal import Decimal
from .models import ConfiguracionLocal


def haversine(lat1, lon1, lat2, lon2):
    """Calcula la distancia en km entre dos puntos geográficos usando la fórmula de Haversine."""
    R = 6371
    d_lat = math.radians(lat2 - lat1)
    d_lon = math.radians(lon2 - lon1)
    a = (math.sin(d_lat / 2) ** 2 +
         math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) *
         math.sin(d_lon / 2) ** 2)
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return round(R * c, 2)


def distancia_por_ruta(lat_origen, lng_origen, lat_destino, lng_destino):
    """Calcula la distancia en km usando OSRM (rutas reales por calles).
    Retorna (distancia_km, ruta_coords, duracion_segundos).
    Si falla, distancia = Haversine, ruta_coords = [], duracion_segundos = 0."""
    try:
        url = (
            f"https://router.project-osrm.org/route/v1/driving/"
            f"{lng_origen},{lat_origen};{lng_destino},{lat_destino}"
            f"?overview=full&geometries=geojson"
        )
        resp = requests.get(url, timeout=5)
        data = resp.json()
        if data.get('code') == 'Ok' and data.get('routes'):
            ruta = data['routes'][0]
            distancia_metros = ruta['distance']
            duracion_segundos = ruta['duration']
            coords = ruta['geometry']['coordinates']
            ruta_coords = [[c[1], c[0]] for c in coords]
            km = round(distancia_metros / 1000, 2)
            return km, ruta_coords, round(duracion_segundos)
    except Exception:
        pass
    km = haversine(lat_origen, lng_origen, lat_destino, lng_destino)
    return km, [], 0


def calcular_costo_envio(lat_destino, lng_destino):
    """Calcula el costo de envío basado en la distancia real por calles y la configuración local.
    Retorna (costo, distancia_km, dentro_cobertura, ruta_coords, tiempo_estimado_minutos)."""
    config = ConfiguracionLocal.get_solo()
    distancia, ruta_coords, duracion_segundos = distancia_por_ruta(
        float(config.latitud_local),
        float(config.longitud_local),
        lat_destino,
        lng_destino
    )
    radio = float(config.radio_cobertura_km or 0)
    dentro_cobertura = distancia <= radio if radio > 0 else True
    costo = float(config.tarifa_base_envio) + (distancia * float(config.precio_por_km))
    tiempo_estimado_minutos = round(duracion_segundos / 60) if duracion_segundos > 0 else 0
    return round(costo, 2), distancia, dentro_cobertura, ruta_coords, tiempo_estimado_minutos
