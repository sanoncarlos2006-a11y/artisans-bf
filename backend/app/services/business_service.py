from sqlalchemy import func, select
from sqlalchemy.orm import Session, selectinload

from app.models import Business, Comment, User
from app.schemas.business import BusinessCreate, BusinessUpdate


class BusinessNotFoundError(Exception):
    pass


def create_business(db: Session, owner: User, payload: BusinessCreate) -> Business:
    business = Business(
        owner_id=owner.id,
        name=payload.name,
        category=payload.category,
        phone=payload.phone,
        latitude=payload.latitude,
        longitude=payload.longitude,
        address_description=payload.address_description,
        description=payload.description,
        opening_hours=payload.opening_hours,
        status="draft",
    )
    db.add(business)
    db.commit()
    db.refresh(business)
    return business


def list_owner_businesses(db: Session, owner: User) -> list[Business]:
    statement = (
        select(Business)
        .options(selectinload(Business.photos))
        .where(Business.owner_id == owner.id)
        .order_by(Business.created_at.desc(), Business.id.desc())
    )
    return list(db.execute(statement).scalars().all())


def list_published_businesses(db: Session) -> list[Business]:
    # Public listing is intentionally limited to published businesses.
    statement = (
        select(Business)
        .options(selectinload(Business.photos))
        .where(Business.status == "published")
        .order_by(Business.name.asc(), Business.id.asc())
    )
    return list(db.execute(statement).scalars().all())


def get_published_business_or_404(db: Session, business_id: int) -> Business:
    # Public detail must not reveal draft or unpublished businesses.
    statement = (
        select(Business)
        .options(selectinload(Business.photos))
        .where(Business.id == business_id, Business.status == "published")
    )
    business = db.execute(statement).scalar_one_or_none()
    if business is None:
        raise BusinessNotFoundError("Business not found")
    return business


def get_owned_business_or_404(db: Session, owner: User, business_id: int) -> Business:
    # Owner routes return 404 for missing or foreign businesses to avoid leaking ownership.
    statement = (
        select(Business)
        .options(selectinload(Business.photos))
        .where(Business.id == business_id, Business.owner_id == owner.id)
    )
    business = db.execute(statement).scalar_one_or_none()
    if business is None:
        raise BusinessNotFoundError("Business not found")
    return business


def recalculate_business_rating(db: Session, business_id: int) -> Business:
    business = db.get(Business, business_id)
    if business is None:
        raise BusinessNotFoundError("Business not found")

    average_rating, ratings_count = db.execute(
        select(func.avg(Comment.ai_rating), func.count(Comment.ai_rating)).where(
            Comment.business_id == business_id,
            Comment.ai_rating.is_not(None),
        )
    ).one()

    business.average_rating = round(float(average_rating), 2) if average_rating is not None else 0.0
    business.ratings_count = int(ratings_count)
    db.commit()
    db.refresh(business)
    return business


def update_business(db: Session, owner: User, business_id: int, payload: BusinessUpdate) -> Business:
    business = get_owned_business_or_404(db, owner, business_id)
    updates = payload.model_dump(exclude_unset=True)
    for field, value in updates.items():
        setattr(business, field, value)
    db.commit()
    db.refresh(business)
    return business


def publish_business(db: Session, owner: User, business_id: int) -> Business:
    business = get_owned_business_or_404(db, owner, business_id)
    business.status = "published"
    db.commit()
    db.refresh(business)
    return business


def unpublish_business(db: Session, owner: User, business_id: int) -> Business:
    business = get_owned_business_or_404(db, owner, business_id)
    business.status = "unpublished"
    db.commit()
    db.refresh(business)
    return business


def delete_business(db: Session, owner: User, business_id: int) -> None:
    business = get_owned_business_or_404(db, owner, business_id)
    db.delete(business)
    db.commit()
