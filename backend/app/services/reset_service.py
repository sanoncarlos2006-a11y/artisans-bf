from dataclasses import dataclass
from datetime import datetime, timedelta
from secrets import randbelow

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.security import hash_password, verify_password
from app.models import PasswordReset
from app.services.auth_service import get_user_by_identifier


RESET_CODE_TTL_MINUTES = 15


@dataclass(frozen=True)
class PasswordResetResult:
    message: str
    demo_reset_code: str | None = None


def _generate_reset_code() -> str:
    return f"{randbelow(1_000_000):06d}"


def request_password_reset(db: Session, identifier: str) -> PasswordResetResult:
    user = get_user_by_identifier(db, identifier)
    generic_message = "If the account exists, a reset code has been generated."

    if user is None:
        if settings.DEMO_MODE:
            return PasswordResetResult(message="No matching account found for this demo reset request.")
        return PasswordResetResult(message=generic_message)

    now = datetime.utcnow()
    active_resets = (
        db.execute(
            select(PasswordReset).where(
                PasswordReset.user_id == user.id,
                PasswordReset.used_at.is_(None),
                PasswordReset.expires_at > now,
            )
        )
        .scalars()
        .all()
    )
    for active_reset in active_resets:
        active_reset.used_at = now

    code = _generate_reset_code()
    reset = PasswordReset(
        user_id=user.id,
        code_hash=hash_password(code),
        expires_at=now + timedelta(minutes=RESET_CODE_TTL_MINUTES),
    )
    db.add(reset)
    db.commit()

    if settings.DEMO_MODE:
        return PasswordResetResult(
            message="Demo reset code generated. Use it before it expires.",
            demo_reset_code=code,
        )
    return PasswordResetResult(message=generic_message)


def reset_password_with_code(db: Session, identifier: str, code: str, new_password: str) -> bool:
    user = get_user_by_identifier(db, identifier)
    if user is None:
        return False

    now = datetime.utcnow()
    resets = (
        db.execute(
            select(PasswordReset)
            .where(
                PasswordReset.user_id == user.id,
                PasswordReset.used_at.is_(None),
                PasswordReset.expires_at > now,
            )
            .order_by(PasswordReset.id.desc())
        )
        .scalars()
        .all()
    )

    for reset in resets:
        if verify_password(code, reset.code_hash):
            reset.used_at = now
            user.password_hash = hash_password(new_password)
            db.commit()
            return True

    return False
