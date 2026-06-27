from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, field_validator


def _strip_optional(value: str | None) -> str | None:
    if value is None:
        return None
    stripped = value.strip()
    if not stripped:
        raise ValueError("field must not be empty")
    return stripped


class UserRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    full_name: str
    email: str | None = None
    phone: str
    is_active: bool
    created_at: datetime
    updated_at: datetime


class UserUpdate(BaseModel):
    full_name: str | None = Field(default=None, max_length=120)
    email: str | None = Field(default=None, max_length=255)
    phone: str | None = Field(default=None, max_length=32)

    @field_validator("full_name", "email", "phone")
    @classmethod
    def strip_optional_fields(cls, value: str | None) -> str | None:
        return _strip_optional(value)
