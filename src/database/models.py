"""Database models for generation records."""

from __future__ import annotations

from datetime import datetime

from sqlalchemy import DateTime, Float, Integer, String, Text
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    """SQLAlchemy declarative base."""


class GenerationRecord(Base):
    """A single Trend2Video generation task."""

    __tablename__ = "generation_records"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    url: Mapped[str] = mapped_column(Text, default="")
    platform: Mapped[str] = mapped_column(String(64), nullable=False)
    duration: Mapped[int] = mapped_column(Integer, nullable=False)
    style: Mapped[str] = mapped_column(String(64), nullable=False)
    opportunity_score: Mapped[float] = mapped_column(Float, default=0)
    video_path: Mapped[str] = mapped_column(Text, default="")
    report_path: Mapped[str] = mapped_column(Text, default="")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
