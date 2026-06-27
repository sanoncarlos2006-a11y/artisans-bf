from pydantic import BaseModel, Field


class CommentCreate(BaseModel):
    comment: str = Field(..., min_length=1, max_length=1000)
    user_id: int | None = None


class AIRatingResponse(BaseModel):
    rating: int
    confidence: float
    explanation: str
    model: str


class CommentResponse(BaseModel):
    id: int
    business_id: int
    user_id: int | None
    comment: str
    ai_rating: int
    ai_confidence: float
    ai_explanation: str | None
    ai_model: str

    model_config = {"from_attributes": True}
