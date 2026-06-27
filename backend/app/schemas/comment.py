from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class CommentCreate(BaseModel):
    content: str = Field(..., min_length=2)
    author_name: Optional[str] = "Client"


class CommentRead(BaseModel):
    id: int
    business_id: int
    content: str
    author_name: Optional[str] = None
    rating: Optional[float] = None
    ai_rating: Optional[float] = None
    justification: Optional[str] = None
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class CommentResponse(BaseModel):
    comment: CommentRead
