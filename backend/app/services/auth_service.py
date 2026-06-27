from sqlalchemy import or_, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.security import create_access_token, hash_password, verify_password
from app.models import User
from app.schemas.auth import RegisterRequest, TokenResponse
from app.schemas.user import UserRead


class AuthConflictError(Exception):
    pass


def get_user_by_identifier(db: Session, identifier: str) -> User | None:
    statement = select(User).where(or_(User.phone == identifier, User.email == identifier))
    return db.execute(statement).scalar_one_or_none()


def register_user(db: Session, payload: RegisterRequest) -> User:
    phone_exists = db.execute(select(User.id).where(User.phone == payload.phone)).scalar_one_or_none()
    if phone_exists is not None:
        raise AuthConflictError("Phone is already used")

    if payload.email is not None:
        email_exists = db.execute(select(User.id).where(User.email == payload.email)).scalar_one_or_none()
        if email_exists is not None:
            raise AuthConflictError("Email is already used")

    user = User(
        full_name=payload.full_name,
        email=payload.email,
        phone=payload.phone,
        password_hash=hash_password(payload.password),
    )
    db.add(user)
    try:
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise AuthConflictError("Identifier is already used") from exc
    db.refresh(user)
    return user


def authenticate_user(db: Session, identifier: str, password: str) -> User | None:
    user = get_user_by_identifier(db, identifier)
    if user is None or not user.is_active:
        return None
    if not verify_password(password, user.password_hash):
        return None
    return user


def build_token_response(user: User) -> TokenResponse:
    return TokenResponse(
        access_token=create_access_token(user.id),
        token_type="bearer",
        user=UserRead.model_validate(user),
    )
