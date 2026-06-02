import math
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


def calcular_costo_envio(lat_destino, lng_destino):
    """Calcula el costo de envío basado en la distancia y la configuración local.
    Retorna (costo, distancia_km, dentro_cobertura)."""
    config = ConfiguracionLocal.get_solo()
    distancia = haversine(
        float(config.latitud_local),
        float(config.longitud_local),
        lat_destino,
        lng_destino
    )
    radio = float(config.radio_cobertura_km or 0)
    dentro_cobertura = distancia <= radio if radio > 0 else True
    costo = float(config.tarifa_base_envio) + (distancia * float(config.precio_por_km))
    return round(costo, 2), distancia, dentro_cobertura
