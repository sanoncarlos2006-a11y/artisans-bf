from __future__ import annotations

from datetime import datetime

from sqlalchemy import CheckConstraint, DateTime, Float, ForeignKey, Index, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class Business(Base):
    __tablename__ = "businesses"
    __table_args__ = (
        CheckConstraint(
            "status IN ('draft', 'published', 'unpublished')",
            name="ck_businesses_status",
        ),
        CheckConstraint("average_rating >= 0 AND average_rating <= 5", name="ck_businesses_average_rating"),
        Index("ix_businesses_status_category", "status", "category"),
    )

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    owner_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(160), nullable=False, index=True)
    category: Mapped[str] = mapped_column(String(80), nullable=False, index=True)
    phone: Mapped[str] = mapped_column(String(32), nullable=False)
    latitude: Mapped[float] = mapped_column(Float, nullable=False)
    longitude: Mapped[float] = mapped_column(Float, nullable=False)
    address_description: Mapped[str] = mapped_column(Text, nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    opening_hours: Mapped[str] = mapped_column(String(255), nullable=False)
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="draft", index=True)
    average_rating: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    ratings_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
    )

    owner: Mapped["User"] = relationship("User", back_populates="businesses")
    photos: Mapped[list["BusinessPhoto"]] = relationship(
        "BusinessPhoto",
        back_populates="business",
        cascade="all, delete-orphan",
    )
    comments: Mapped[list["Comment"]] = relationship(
        "Comment",
        back_populates="business",
        cascade="all, delete-orphan",
    )
