from pathlib import Path
from uuid import uuid4

from fastapi import UploadFile
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.core.config import BACKEND_DIR, settings
from app.models import BusinessPhoto, User
from app.services.business_service import get_owned_business_or_404


ALLOWED_IMAGE_TYPES = {
    "image/jpeg": ".jpg",
    "image/png": ".png",
    "image/webp": ".webp",
}


class UploadValidationError(Exception):
    pass


class PhotoNotFoundError(Exception):
    pass


def get_upload_dir() -> Path:
    upload_dir = Path(settings.UPLOAD_DIR)
    if not upload_dir.is_absolute():
        upload_dir = BACKEND_DIR / upload_dir
    upload_dir.mkdir(parents=True, exist_ok=True)
    return upload_dir


def _max_upload_size_bytes() -> int:
    return settings.MAX_UPLOAD_SIZE_MB * 1024 * 1024


async def upload_business_photo(db: Session, owner: User, business_id: int, file: UploadFile) -> BusinessPhoto:
    get_owned_business_or_404(db, owner, business_id)

    photo_count = db.execute(
        select(func.count(BusinessPhoto.id)).where(BusinessPhoto.business_id == business_id)
    ).scalar_one()
    if photo_count >= settings.MAX_PHOTOS_PER_BUSINESS:
        raise UploadValidationError(f"Maximum {settings.MAX_PHOTOS_PER_BUSINESS} photos per business is allowed")

    content_type = file.content_type or ""
    extension = ALLOWED_IMAGE_TYPES.get(content_type)
    if extension is None:
        raise UploadValidationError("Only jpeg, png and webp images are allowed")

    content = await file.read()
    if not content:
        raise UploadValidationError("Uploaded file is empty")
    if len(content) > _max_upload_size_bytes():
        raise UploadValidationError(f"File exceeds {settings.MAX_UPLOAD_SIZE_MB} MB")

    stored_name = f"{business_id}_{uuid4().hex}{extension}"
    upload_dir = get_upload_dir()
    destination = upload_dir / stored_name
    destination.write_bytes(content)

    photo = BusinessPhoto(
        business_id=business_id,
        file_path=f"/uploads/{stored_name}",
        file_name=stored_name,
        content_type=content_type,
    )
    db.add(photo)
    db.commit()
    db.refresh(photo)
    return photo


def list_business_photos(db: Session, owner: User, business_id: int) -> list[BusinessPhoto]:
    get_owned_business_or_404(db, owner, business_id)
    statement = (
        select(BusinessPhoto)
        .where(BusinessPhoto.business_id == business_id)
        .order_by(BusinessPhoto.created_at.asc(), BusinessPhoto.id.asc())
    )
    return list(db.execute(statement).scalars().all())


def delete_business_photo(db: Session, owner: User, business_id: int, photo_id: int) -> None:
    get_owned_business_or_404(db, owner, business_id)
    photo = db.execute(
        select(BusinessPhoto).where(BusinessPhoto.id == photo_id, BusinessPhoto.business_id == business_id)
    ).scalar_one_or_none()
    if photo is None:
        raise PhotoNotFoundError("Photo not found")

    file_path = get_upload_dir() / photo.file_name
    db.delete(photo)
    db.commit()
    if file_path.exists() and file_path.is_file():
        file_path.unlink()
