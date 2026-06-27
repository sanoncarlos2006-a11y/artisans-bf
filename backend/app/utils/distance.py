from math import atan2, cos, radians, sin, sqrt


def calculate_distance_km(user_lat: float, user_lng: float, business_lat: float, business_lng: float) -> float:
    """Calcule la distance en kilomètres avec la formule de Haversine."""
    earth_radius_km = 6371.0

    lat1 = radians(user_lat)
    lon1 = radians(user_lng)
    lat2 = radians(business_lat)
    lon2 = radians(business_lng)

    dlat = lat2 - lat1
    dlon = lon2 - lon1

    a = sin(dlat / 2) ** 2 + cos(lat1) * cos(lat2) * sin(dlon / 2) ** 2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))
    return round(earth_radius_km * c, 2)
