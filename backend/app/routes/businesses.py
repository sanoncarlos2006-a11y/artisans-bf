from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, get_db
from app.models import Business, User
from app.schemas.business import BusinessCreate, BusinessOwnerRead, BusinessPhotoRead, BusinessPublicRead, BusinessUpdate
from app.schemas.common import MessageResponse
from app.services.business_service import (
    BusinessNotFoundError,
    create_business,
    delete_business,
    get_owned_business_or_404,
    get_published_business_or_404,
    list_owner_businesses,
    list_published_businesses,
    publish_business,
    unpublish_business,
    update_business,
)
from app.services.upload_service import (
    PhotoNotFoundError,
    UploadValidationError,
    delete_business_photo,
    list_business_photos,
    upload_business_photo,
)


router = APIRouter(tags=["Businesses"])


def _business_not_found(exc: BusinessNotFoundError) -> HTTPException:
    return HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc))


def _bad_upload_request(exc: UploadValidationError) -> HTTPException:
    return HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc))


@router.get("/businesses", response_model=list[BusinessPublicRead])
def read_published_businesses(db: Session = Depends(get_db)) -> list[Business]:
    return list_published_businesses(db)


@router.post("/businesses", response_model=BusinessOwnerRead, status_code=status.HTTP_201_CREATED)
def create_my_business(
    payload: BusinessCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Business:
    return create_business(db, current_user, payload)


@router.get("/my-businesses", response_model=list[BusinessOwnerRead])
def read_my_businesses(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> list[Business]:
    return list_owner_businesses(db, current_user)


@router.get("/businesses/{business_id}/owner", response_model=BusinessOwnerRead)
def read_my_business_detail(
    business_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Business:
    try:
        return get_owned_business_or_404(db, current_user, business_id)
    except BusinessNotFoundError as exc:
        raise _business_not_found(exc) from exc


@router.get("/businesses/{business_id}", response_model=BusinessPublicRead)
def read_published_business_detail(
    business_id: int,
    db: Session = Depends(get_db),
) -> Business:
    try:
        return get_published_business_or_404(db, business_id)
    except BusinessNotFoundError as exc:
        raise _business_not_found(exc) from exc


@router.put("/businesses/{business_id}", response_model=BusinessOwnerRead)
def update_my_business(
    business_id: int,
    payload: BusinessUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Business:
    try:
        return update_business(db, current_user, business_id, payload)
    except BusinessNotFoundError as exc:
        raise _business_not_found(exc) from exc


@router.patch("/businesses/{business_id}/publish", response_model=BusinessOwnerRead)
def publish_my_business(
    business_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Business:
    try:
        return publish_business(db, current_user, business_id)
    except BusinessNotFoundError as exc:
        raise _business_not_found(exc) from exc


@router.patch("/businesses/{business_id}/unpublish", response_model=BusinessOwnerRead)
def unpublish_my_business(
    business_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Business:
    try:
        return unpublish_business(db, current_user, business_id)
    except BusinessNotFoundError as exc:
        raise _business_not_found(exc) from exc


@router.post("/businesses/{business_id}/photos", response_model=BusinessPhotoRead, status_code=status.HTTP_201_CREATED)
async def upload_my_business_photo(
    business_id: int,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> BusinessPhotoRead:
    try:
        return await upload_business_photo(db, current_user, business_id, file)
    except BusinessNotFoundError as exc:
        raise _business_not_found(exc) from exc
    except UploadValidationError as exc:
        raise _bad_upload_request(exc) from exc


@router.get("/businesses/{business_id}/photos", response_model=list[BusinessPhotoRead])
def read_my_business_photos(
    business_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> list[BusinessPhotoRead]:
    try:
        return list_business_photos(db, current_user, business_id)
    except BusinessNotFoundError as exc:
        raise _business_not_found(exc) from exc


@router.delete("/businesses/{business_id}/photos/{photo_id}", response_model=MessageResponse)
def delete_my_business_photo(
    business_id: int,
    photo_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> MessageResponse:
    try:
        delete_business_photo(db, current_user, business_id, photo_id)
    except BusinessNotFoundError as exc:
        raise _business_not_found(exc) from exc
    except PhotoNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    return MessageResponse(message="Photo deleted successfully.")


@router.delete("/businesses/{business_id}", response_model=MessageResponse)
def delete_my_business(
    business_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> MessageResponse:
    try:
        delete_business(db, current_user, business_id)
    except BusinessNotFoundError as exc:
        raise _business_not_found(exc) from exc
    return MessageResponse(message="Business deleted successfully.")
