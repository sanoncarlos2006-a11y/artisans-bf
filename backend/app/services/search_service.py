from sqlalchemy.orm import Session

from app.models.business import Business
from app.utils.distance import calculate_distance_km
from app.utils.open_status import get_open_status_label
from app.utils.text_normalizer import normalize_category, normalize_text
from app.utils.hours_display import build_hours_label, opening_days_to_labels
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
        "average_rating": round(float(business.average_rating or 0), 2),
        "reviews_count": int(business.reviews_count or 0),
        "distance_km": distance_km,
        "open_status": get_open_status_label(
            business.opening_days,
            business.open_time,
            business.close_time,
            bool(business.is_temporarily_closed),
        ),
        "opening_days": business.opening_days,
        "open_time": business.open_time,
        "close_time": business.close_time,
        "is_temporarily_closed": bool(business.is_temporarily_closed),
        "opening_days_labels": opening_days_to_labels(business.opening_days),
        "hours_label": build_hours_label(business.opening_days, business.open_time, business.close_time),
        "google_maps_url": build_google_maps_place_url(business.latitude, business.longitude, business.name),
        "google_navigation_url": google_navigation_url,
        "openstreetmap_url": build_openstreetmap_url(business.latitude, business.longitude),
        "photo_url": business.photo_url,
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
