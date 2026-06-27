from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator


BusinessStatus = Literal["draft", "published", "unpublished"]


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


class BusinessPhotoRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    business_id: int
    file_path: str
    file_name: str
    content_type: str
    created_at: datetime


class BusinessBase(BaseModel):
    name: str = Field(min_length=1, max_length=160)
    category: str = Field(min_length=1, max_length=80)
    phone: str = Field(min_length=1, max_length=32)
    latitude: float = Field(ge=-90, le=90)
    longitude: float = Field(ge=-180, le=180)
    address_description: str = Field(min_length=1)
    opening_hours: str = Field(min_length=1, max_length=255)

    @field_validator("name", "category", "phone", "address_description", "opening_hours")
    @classmethod
    def strip_required_fields(cls, value: str) -> str:
        return _strip_required(value)


class BusinessCreate(BusinessBase):
    pass


class BusinessUpdate(BaseModel):
    name: str | None = Field(default=None, max_length=160)
    category: str | None = Field(default=None, max_length=80)
    phone: str | None = Field(default=None, max_length=32)
    latitude: float | None = Field(default=None, ge=-90, le=90)
    longitude: float | None = Field(default=None, ge=-180, le=180)
    address_description: str | None = None
    opening_hours: str | None = Field(default=None, max_length=255)

    @field_validator("name", "category", "phone", "address_description", "opening_hours")
    @classmethod
    def strip_optional_fields(cls, value: str | None) -> str | None:
        return _strip_optional(value)


class BusinessRead(BusinessBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    owner_id: int
    status: BusinessStatus
    average_rating: float = Field(ge=0, le=5)
    ratings_count: int = Field(ge=0)
    created_at: datetime
    updated_at: datetime
    photos: list[BusinessPhotoRead] = Field(default_factory=list)


class BusinessOwnerRead(BusinessRead):
    pass


class BusinessPublicRead(BusinessBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    status: BusinessStatus
    average_rating: float = Field(ge=0, le=5)
    ratings_count: int = Field(ge=0)
    photos: list[BusinessPhotoRead] = Field(default_factory=list)
