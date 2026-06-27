from sqlalchemy import Column, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship

from app.db.base import Base


class Comment(Base):
    __tablename__ = "comments"

    id = Column(Integer, primary_key=True, index=True)
    business_id = Column(Integer, ForeignKey("businesses.id"), nullable=False, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True)

    comment = Column(Text, nullable=False)
    ai_rating = Column(Integer, nullable=False)
    ai_confidence = Column(Float, default=0.0)
    ai_explanation = Column(String(500), nullable=True)
    ai_model = Column(String(100), nullable=False)

    business = relationship("Business", back_populates="comments")
    user = relationship("User", back_populates="comments")
