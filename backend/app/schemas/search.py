from pydantic import BaseModel


class BusinessSearchItem(BaseModel):
    id: int
    owner_id: int | None
    name: str
    category: str
    phone: str
    address_description: str
    latitude: float
    longitude: float
    status: str
    average_rating: float
    ratings_count: int
    rating_average: float
    rating_count: int
    reviews_count: int
    distance_km: float | None
    opening_hours: str
    hours_label: str
    google_maps_url: str
    google_navigation_url: str | None
    openstreetmap_url: str
    photos: list[str]
    photo_url: str | None
    description: str | None
