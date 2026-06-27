from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, field_validator


def _strip_required(value: str) -> str:
    stripped = value.strip()
    if not stripped:
        raise ValueError("field must not be empty")
    return stripped


class CommentBase(BaseModel):
    content: str = Field(min_length=1)

    @field_validator("content")
    @classmethod
    def strip_content(cls, value: str) -> str:
        return _strip_required(value)


class CommentCreate(CommentBase):
    pass


class CommentRead(CommentBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    business_id: int
    user_id: int | None = None
    ai_rating: float | None = Field(default=None, ge=0, le=5)
    ai_sentiment: str | None = None
    ai_reason: str | None = None
    created_at: datetime
