from sqlalchemy.orm import Session

from app.models.business import Business
from app.utils.distance import calculate_distance_km
from app.utils.text_normalizer import normalize_category, normalize_text
from app.utils.navigation_links import (
    build_google_maps_navigation_url,
    build_google_maps_place_url,
    build_openstreetmap_url,
)


def business_to_search_item(
    business: Business,
    distance_km: float | None,
    user_lat: float | None = None,
    user_lng: float | None = None,
) -> dict:
    google_navigation_url = None
    if user_lat is not None and user_lng is not None:
        google_navigation_url = build_google_maps_navigation_url(
            destination_lat=business.latitude,
            destination_lng=business.longitude,
            origin_lat=user_lat,
            origin_lng=user_lng,
            travel_mode="walking",
        )

    photos = [photo.file_path for photo in sorted(business.photos, key=lambda item: (item.created_at, item.id))]
    rating = round(float(business.average_rating or 0), 2)
    rating_count = int(business.ratings_count or 0)

    return {
        "id": business.id,
        "owner_id": business.owner_id,
        "name": business.name,
        "category": business.category,
        "phone": business.phone,
        "address_description": business.address_description,
        "latitude": business.latitude,
        "longitude": business.longitude,
        "status": business.status,
        "average_rating": rating,
        "ratings_count": rating_count,
        "rating_average": rating,
        "rating_count": rating_count,
        "reviews_count": rating_count,
        "distance_km": distance_km,
        "opening_hours": business.opening_hours,
        "hours_label": business.opening_hours,
        "google_maps_url": build_google_maps_place_url(business.latitude, business.longitude, business.name),
        "google_navigation_url": google_navigation_url,
        "openstreetmap_url": build_openstreetmap_url(business.latitude, business.longitude),
        "photos": photos,
        "photo_url": photos[0] if photos else None,
        "description": business.description,
    }


def search_businesses(
    db: Session,
    q: str | None = None,
    name: str | None = None,
    category: str | None = None,
    min_rating: float | None = None,
    lat: float | None = None,
    lng: float | None = None,
    radius_km: float | None = 10.0,
) -> list[dict]:
    """
    Recherche publique :
    - uniquement les commerces published ;
    - filtre nom/catégorie/note ;
    - distance + tri du plus proche au plus éloigné si lat/lng fournis ;
    - état ouvert/fermé calculé selon les horaires.
    """
    query = db.query(Business).filter(Business.status == "published")

    text_query = normalize_text(q or name)
    if text_query:
        category_guess = normalize_category(text_query)
        query = query.filter(
            (Business.name.ilike(f"%{text_query}%"))
            | (Business.category.ilike(f"%{category_guess}%"))
        )

    if category:
        normalized_category = normalize_category(category)
        query = query.filter(Business.category.ilike(f"%{normalized_category}%"))

    if min_rating is not None:
        query = query.filter(Business.average_rating >= float(min_rating))

    businesses = query.all()
    results: list[dict] = []

    for business in businesses:
        distance_km = None
        if lat is not None and lng is not None:
            distance_km = calculate_distance_km(float(lat), float(lng), business.latitude, business.longitude)
            if radius_km is not None and distance_km > float(radius_km):
                continue

        results.append(business_to_search_item(business, distance_km, user_lat=lat, user_lng=lng))

    results.sort(key=lambda item: item["distance_km"] if item["distance_km"] is not None else 999999)
    return results
