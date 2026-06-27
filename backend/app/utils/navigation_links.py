from urllib.parse import quote_plus


def build_google_maps_place_url(destination_lat: float, destination_lng: float, destination_name: str | None = None) -> str:
    """Lien Google Maps simple vers la position du commerce."""
    query = f"{destination_lat},{destination_lng}"
    if destination_name:
        query = f"{destination_name} {query}"
    return f"https://www.google.com/maps/search/?api=1&query={quote_plus(query)}"


def build_google_maps_navigation_url(
    destination_lat: float,
    destination_lng: float,
    origin_lat: float | None = None,
    origin_lng: float | None = None,
    travel_mode: str = "walking",
) -> str:
    """
    Lien Google Maps d'itinéraire.

    Aucun SDK ni clé API n'est nécessaire : le frontend ouvre simplement ce lien.
    Si origin_lat/origin_lng sont absents, Google Maps utilisera la position actuelle
    de l'utilisateur après autorisation dans l'application Google Maps/le navigateur.
    """
    allowed_modes = {"driving", "walking", "bicycling", "transit"}
    mode = travel_mode if travel_mode in allowed_modes else "walking"

    base = "https://www.google.com/maps/dir/?api=1"
    destination = f"{destination_lat},{destination_lng}"
    url = f"{base}&destination={quote_plus(destination)}&travelmode={mode}"

    if origin_lat is not None and origin_lng is not None:
        origin = f"{origin_lat},{origin_lng}"
        url += f"&origin={quote_plus(origin)}"

    return url


def build_openstreetmap_url(destination_lat: float, destination_lng: float, zoom: int = 18) -> str:
    """Lien OpenStreetMap centré sur le commerce."""
    return f"https://www.openstreetmap.org/?mlat={destination_lat}&mlon={destination_lng}#map={zoom}/{destination_lat}/{destination_lng}"
