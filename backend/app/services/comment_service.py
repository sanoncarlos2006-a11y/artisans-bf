from sqlalchemy.orm import Session

from app.models.business import Business
from app.models.comment import Comment
from app.services.ai_service import rate_comment


def recalculate_business_rating(db: Session, business_id: int) -> None:
    comments = db.query(Comment).filter(Comment.business_id == business_id).all()
    business = db.query(Business).filter(Business.id == business_id).first()
    if not business:
        return

    ratings = [comment.ai_rating for comment in comments if comment.ai_rating is not None]
    if not ratings:
        business.average_rating = 0.0
        business.ratings_count = 0
    else:
        business.ratings_count = len(ratings)
        business.average_rating = round(sum(ratings) / len(ratings), 2)

    db.add(business)
    db.commit()


def create_comment_with_ai(db: Session, business_id: int, comment_text: str, user_id: int | None = None) -> Comment:
    business = db.query(Business).filter(Business.id == business_id).first()
    if not business:
        raise ValueError("Commerce introuvable.")
    if business.status != "published":
        raise ValueError("Impossible de commenter un commerce non publié.")

    ai_result = rate_comment(comment_text)

    comment = Comment(
        business_id=business_id,
        user_id=user_id,
        comment=comment_text,
        ai_rating=ai_result.rating,
        ai_confidence=ai_result.confidence,
        ai_explanation=ai_result.explanation,
        ai_model=ai_result.model,
    )
    db.add(comment)
    db.commit()
    db.refresh(comment)

    recalculate_business_rating(db, business_id)
    return comment
