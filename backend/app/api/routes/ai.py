from fastapi import APIRouter
from pydantic import BaseModel, Field

from app.schemas.comment import AIRatingResponse
from app.services.ai_service import get_ai_status, rate_comment

router = APIRouter(tags=["IA"])


class RateCommentRequest(BaseModel):
    comment: str = Field(..., min_length=1, max_length=1000)


@router.get("/ai/status")
def ai_status():
    return get_ai_status()


@router.post("/ai/rate-comment", response_model=AIRatingResponse)
def rate_comment_route(payload: RateCommentRequest):
    return rate_comment(payload.comment)
