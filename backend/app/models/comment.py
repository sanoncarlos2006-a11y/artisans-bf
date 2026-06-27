from __future__ import annotations

from datetime import datetime

from sqlalchemy import CheckConstraint, DateTime, Float, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class Comment(Base):
    __tablename__ = "comments"
    __table_args__ = (
        CheckConstraint("ai_rating IS NULL OR (ai_rating >= 0 AND ai_rating <= 5)", name="ck_comments_ai_rating"),
    )

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    business_id: Mapped[int] = mapped_column(
        ForeignKey("businesses.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    user_id: Mapped[int | None] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    ai_rating: Mapped[float | None] = mapped_column(Float, nullable=True)
    ai_sentiment: Mapped[str | None] = mapped_column(String(30), nullable=True)
    ai_reason: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow)

    business: Mapped["Business"] = relationship("Business", back_populates="comments")
    user: Mapped["User | None"] = relationship("User", back_populates="comments")
