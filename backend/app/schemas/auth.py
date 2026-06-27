from pydantic import BaseModel, Field, field_validator

from app.schemas.user import UserRead


def _strip_required(value: str) -> str:
    stripped = value.strip()
    if not stripped:
        raise ValueError("field must not be empty")
    return stripped


def _strip_optional(value: str | None) -> str | None:
    if value is None:
        return None
    stripped = value.strip()
    if not stripped:
        raise ValueError("field must not be empty")
    return stripped


class RegisterRequest(BaseModel):
    full_name: str = Field(min_length=1, max_length=120)
    phone: str = Field(min_length=1, max_length=32)
    password: str = Field(min_length=8, max_length=128)
    email: str | None = Field(default=None, max_length=255)

    @field_validator("full_name", "phone", "password")
    @classmethod
    def strip_required_fields(cls, value: str) -> str:
        return _strip_required(value)

    @field_validator("email")
    @classmethod
    def strip_email(cls, value: str | None) -> str | None:
        return _strip_optional(value)


class LoginRequest(BaseModel):
    identifier: str = Field(min_length=1, max_length=255)
    password: str = Field(min_length=1, max_length=128)

    @field_validator("identifier", "password")
    @classmethod
    def strip_required_fields(cls, value: str) -> str:
        return _strip_required(value)


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserRead


class ForgotPasswordRequest(BaseModel):
    identifier: str = Field(min_length=1, max_length=255)

    @field_validator("identifier")
    @classmethod
    def strip_identifier(cls, value: str) -> str:
        return _strip_required(value)


class ResetPasswordRequest(BaseModel):
    identifier: str = Field(min_length=1, max_length=255)
    code: str = Field(min_length=6, max_length=20)
    new_password: str = Field(min_length=8, max_length=128)

    @field_validator("identifier", "code", "new_password")
    @classmethod
    def strip_required_fields(cls, value: str) -> str:
        return _strip_required(value)


class PasswordResetDemoResponse(BaseModel):
    message: str
    demo_reset_code: str | None = None
