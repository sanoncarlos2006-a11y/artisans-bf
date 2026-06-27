from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.models.comment import Comment
from app.schemas.comment import CommentCreate, CommentRead
from app.services.comment_service import create_comment_with_ai

router = APIRouter(tags=["Commentaires + IA"])


@router.post("/businesses/{business_id}/comments", response_model=CommentRead)
def create_business_comment(business_id: int, payload: CommentCreate, db: Session = Depends(get_db)):
    try:
        comment = create_comment_with_ai(db, business_id, payload.comment, payload.user_id)
        return {
            "id": comment.id,
            "business_id": comment.business_id,
            "user_id": comment.user_id,
            "comment": comment.comment,
            "content": comment.comment,
            "rating": comment.ai_rating,
            "ai_rating": comment.ai_rating,
            "ai_confidence": comment.ai_confidence,
            "ai_explanation": comment.ai_explanation,
            "ai_model": comment.ai_model,
            "justification": comment.ai_explanation,
            "created_at": None,
        }
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.get("/businesses/{business_id}/comments", response_model=list[CommentRead])
def list_business_comments(business_id: int, db: Session = Depends(get_db)):
    comments = db.query(Comment).filter(Comment.business_id == business_id).order_by(Comment.id.desc()).all()
    return [
        {
            "id": comment.id,
            "business_id": comment.business_id,
            "user_id": comment.user_id,
            "comment": comment.comment,
            "content": comment.comment,
            "rating": comment.ai_rating,
            "ai_rating": comment.ai_rating,
            "ai_confidence": comment.ai_confidence,
            "ai_explanation": comment.ai_explanation,
            "ai_model": comment.ai_model,
            "justification": comment.ai_explanation,
            "created_at": None,
        }
        for comment in comments
    ]
