from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class CommentCreate(BaseModel):
    comment: str = Field(..., min_length=1, max_length=1000)
    content: Optional[str] = None
    author_name: Optional[str] = "Client"
    user_id: Optional[int] = None


class AIRatingResponse(BaseModel):
    rating: int
    confidence: float
    explanation: str
    model: str


class CommentRead(BaseModel):
    id: int
    business_id: int
    content: Optional[str] = None
    comment: Optional[str] = None
    author_name: Optional[str] = None
    rating: Optional[float] = None
    ai_rating: Optional[float] = None
    justification: Optional[str] = None
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class CommentResponse(BaseModel):
    id: int
    business_id: int
    user_id: Optional[int] = None
    comment: str
    ai_rating: int
    ai_confidence: float
    ai_explanation: Optional[str] = None
    ai_model: str

    class Config:
        from_attributes = True
