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
    reviews_count: int
    distance_km: float | None
    open_status: str
    opening_days: str | None
    open_time: str | None
    close_time: str | None
    is_temporarily_closed: bool
    opening_days_labels: list[str]
    hours_label: str
    google_maps_url: str
    google_navigation_url: str | None
    openstreetmap_url: str
    photo_url: str | None
    description: str | None
