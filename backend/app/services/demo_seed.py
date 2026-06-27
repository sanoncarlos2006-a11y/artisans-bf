from dataclasses import dataclass

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.security import hash_password
from app.models import Business, User


DEMO_OWNER = {
    "full_name": "Proprietaire Demo",
    "email": "demo.owner@example.test",
    "phone": "70000000",
    "password": "DemoPassword123",
}

DEMO_BUSINESSES = [
    {
        "name": "Atelier Couture Wend-Panga",
        "category": "Couturier",
        "phone": "70001001",
        "latitude": 12.3714,
        "longitude": -1.5197,
        "address_description": "Ouagadougou, quartier Gounghin, pres du marche.",
        "opening_hours": "Lundi-Samedi 08:00-18:00",
        "status": "published",
    },
    {
        "name": "Garage Moto Kadiogo",
        "category": "Mecanicien",
        "phone": "70001002",
        "latitude": 12.3972,
        "longitude": -1.4869,
        "address_description": "Ouagadougou, secteur 28, proche de la voie principale.",
        "opening_hours": "Lundi-Dimanche 07:30-19:00",
        "status": "published",
    },
    {
        "name": "Salon Coiffure Neerwaya",
        "category": "Coiffeur",
        "phone": "70001003",
        "latitude": 11.1771,
        "longitude": -4.2979,
        "address_description": "Bobo-Dioulasso, quartier Dioulassoba, rue commerciale.",
        "opening_hours": "Mardi-Dimanche 09:00-20:00",
        "status": "published",
    },
    {
        "name": "Menuiserie Faso Bois",
        "category": "Menuisier",
        "phone": "70001004",
        "latitude": 12.3296,
        "longitude": -1.5362,
        "address_description": "Ouagadougou, quartier Pissy, derriere la station.",
        "opening_hours": "Lundi-Samedi 08:00-17:30",
        "status": "draft",
    },
    {
        "name": "Electricite Lumiere BF",
        "category": "Electricien",
        "phone": "70001005",
        "latitude": 11.1649,
        "longitude": -4.3052,
        "address_description": "Bobo-Dioulasso, secteur 21, proche du rond-point.",
        "opening_hours": "Lundi-Vendredi 08:00-18:00",
        "status": "unpublished",
    },
]


@dataclass(frozen=True)
class DemoSeedResult:
    owner: User
    businesses: list[Business]


def _upsert_demo_owner(db: Session) -> User:
    owner = db.execute(select(User).where(User.phone == DEMO_OWNER["phone"])).scalar_one_or_none()
    if owner is None:
        owner = User(
            full_name=DEMO_OWNER["full_name"],
            email=DEMO_OWNER["email"],
            phone=DEMO_OWNER["phone"],
            password_hash=hash_password(DEMO_OWNER["password"]),
            is_active=True,
        )
        db.add(owner)
        db.commit()
        db.refresh(owner)
        return owner

    owner.full_name = DEMO_OWNER["full_name"]
    owner.email = DEMO_OWNER["email"]
    owner.password_hash = hash_password(DEMO_OWNER["password"])
    owner.is_active = True
    db.commit()
    db.refresh(owner)
    return owner


def _upsert_demo_business(db: Session, owner: User, payload: dict[str, object]) -> Business:
    business = db.execute(
        select(Business).where(Business.owner_id == owner.id, Business.name == payload["name"])
    ).scalar_one_or_none()
    if business is None:
        business = Business(owner_id=owner.id)
        db.add(business)

    business.name = str(payload["name"])
    business.category = str(payload["category"])
    business.phone = str(payload["phone"])
    business.latitude = float(payload["latitude"])
    business.longitude = float(payload["longitude"])
    business.address_description = str(payload["address_description"])
    business.opening_hours = str(payload["opening_hours"])
    business.status = str(payload["status"])
    business.average_rating = 0.0
    business.ratings_count = 0
    db.commit()
    db.refresh(business)
    return business


def seed_demo_data(db: Session) -> DemoSeedResult:
    owner = _upsert_demo_owner(db)
    businesses = [_upsert_demo_business(db, owner, payload) for payload in DEMO_BUSINESSES]
    return DemoSeedResult(owner=owner, businesses=businesses)
