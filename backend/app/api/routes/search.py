from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.business import Business
from app.schemas.search import BusinessSearchItem
from app.services.search_service import business_to_search_item, search_businesses
from app.utils.distance import calculate_distance_km
from app.utils.navigation_links import build_google_maps_navigation_url, build_openstreetmap_url

router = APIRouter(tags=["Recherche géolocalisée"])


@router.get("/search", response_model=list[BusinessSearchItem])
def search_route(
    q: str | None = Query(default=None, description="Recherche libre : nom ou domaine, ex: mécanicien"),
    name: str | None = Query(default=None, description="Nom du commerce"),
    category: str | None = Query(default=None, description="Domaine/catégorie : mecanicien, couturier..."),
    min_rating: float | None = Query(default=None, ge=0, le=5),
    lat: float | None = Query(default=None),
    lng: float | None = Query(default=None),
    radius_km: float | None = Query(default=10.0, gt=0),
    db: Session = Depends(get_db),
):
    return search_businesses(
        db=db,
        q=q,
        name=name,
        category=category,
        min_rating=min_rating,
        lat=lat,
        lng=lng,
        radius_km=radius_km,
    )


@router.get("/businesses/{business_id}", response_model=BusinessSearchItem)
def get_business_route(
    business_id: int,
    lat: float | None = Query(default=None),
    lng: float | None = Query(default=None),
    db: Session = Depends(get_db),
):
    business = db.query(Business).filter(Business.id == business_id).first()
    if not business:
        raise HTTPException(status_code=404, detail="Commerce introuvable.")

    distance_km = None
    if lat is not None and lng is not None:
        distance_km = calculate_distance_km(lat, lng, business.latitude, business.longitude)

    return business_to_search_item(business, distance_km=distance_km, user_lat=lat, user_lng=lng)


@router.get("/businesses/{business_id}/navigation")
def get_business_navigation_route(
    business_id: int,
    lat: float | None = Query(default=None, description="Latitude actuelle de l'utilisateur"),
    lng: float | None = Query(default=None, description="Longitude actuelle de l'utilisateur"),
    mode: str = Query(default="walking", description="walking, driving, bicycling ou transit"),
    db: Session = Depends(get_db),
):
    """
    Fournit les liens d'itinéraire à ouvrir côté frontend.

    Cette route ne recrée pas Google Maps dans le backend : elle donne au frontend
    les URLs prêtes à ouvrir pour guider l'utilisateur vers le commerce.
    """
    business = db.query(Business).filter(Business.id == business_id).first()
    if not business:
        raise HTTPException(status_code=404, detail="Commerce introuvable.")

    distance_km = None
    if lat is not None and lng is not None:
        distance_km = calculate_distance_km(lat, lng, business.latitude, business.longitude)

    return {
        "business_id": business.id,
        "name": business.name,
        "category": business.category,
        "destination": {
            "latitude": business.latitude,
            "longitude": business.longitude,
            "address_description": business.address_description,
        },
        "origin": {"latitude": lat, "longitude": lng} if lat is not None and lng is not None else None,
        "distance_km": distance_km,
        "google_navigation_url": build_google_maps_navigation_url(
            destination_lat=business.latitude,
            destination_lng=business.longitude,
            origin_lat=lat,
            origin_lng=lng,
            travel_mode=mode,
        ),
        "openstreetmap_url": build_openstreetmap_url(business.latitude, business.longitude),
        "note_frontend": "Pour le suivi en direct, le frontend doit utiliser navigator.geolocation.watchPosition() et ouvrir google_navigation_url pour l'itinéraire guidé.",
    }
