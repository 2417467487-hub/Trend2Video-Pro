"""Database models for trends, creator memory, predictions, packages, and generation tasks."""

from __future__ import annotations

from datetime import datetime

from sqlalchemy import DateTime, Float, ForeignKey, Integer, String, Text, UniqueConstraint
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    """SQLAlchemy declarative base."""


class Topic(Base):
    """A collected trend topic.

    The class keeps the historical Python name `Topic`, while the database table
    is intentionally named `trends` to match the product language.
    """

    __tablename__ = "trends"
    __table_args__ = (UniqueConstraint("url", name="uq_trends_url"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    source: Mapped[str] = mapped_column(String(64), default="manual", index=True)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    url: Mapped[str] = mapped_column(Text, nullable=False)
    description: Mapped[str] = mapped_column(Text, default="")
    raw_score: Mapped[float] = mapped_column(Float, default=0)
    trend_score: Mapped[float] = mapped_column(Float, default=0)
    competition_score: Mapped[float] = mapped_column(Float, default=0)
    monetization_score: Mapped[float] = mapped_column(Float, default=0)
    audience_fit_score: Mapped[float] = mapped_column(Float, default=0)
    urgency_score: Mapped[float] = mapped_column(Float, default=0)
    final_opportunity_score: Mapped[float] = mapped_column(Float, default=0, index=True)
    recommendation_reason: Mapped[str] = mapped_column(Text, default="")
    risk_note: Mapped[str] = mapped_column(Text, default="")
    status: Mapped[str] = mapped_column(String(32), default="new")
    collected_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class TopicSnapshot(Base):
    """A metric snapshot for a trend."""

    __tablename__ = "topic_snapshots"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    topic_id: Mapped[int] = mapped_column(ForeignKey("trends.id"), index=True)
    metric_name: Mapped[str] = mapped_column(String(64), nullable=False)
    metric_value: Mapped[float] = mapped_column(Float, default=0)
    collected_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class CreatorMemoryRecord(Base):
    """Persisted creator memory events for future model training."""

    __tablename__ = "creator_memory"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    creator_name: Mapped[str] = mapped_column(String(128), default="")
    topic_title: Mapped[str] = mapped_column(String(255), default="")
    platform: Mapped[str] = mapped_column(String(64), default="")
    creator_fit_score: Mapped[float] = mapped_column(Float, default=0)
    viral_probability: Mapped[float] = mapped_column(Float, default=0)
    actual_views: Mapped[int] = mapped_column(Integer, default=0)
    notes: Mapped[str] = mapped_column(Text, default="")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class ViralPrediction(Base):
    """Stored viral prediction output."""

    __tablename__ = "viral_predictions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    topic_id: Mapped[int | None] = mapped_column(ForeignKey("trends.id"), nullable=True)
    title: Mapped[str] = mapped_column(String(255), default="")
    platform: Mapped[str] = mapped_column(String(64), default="")
    viral_probability: Mapped[float] = mapped_column(Float, default=0)
    predicted_view_range: Mapped[str] = mapped_column(String(64), default="")
    confidence_level: Mapped[str] = mapped_column(String(64), default="")
    explanation: Mapped[str] = mapped_column(Text, default="")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class PublishPackage(Base):
    """Stored publish package export."""

    __tablename__ = "publish_packages"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    task_id: Mapped[int | None] = mapped_column(ForeignKey("generation_tasks.id"), nullable=True)
    title: Mapped[str] = mapped_column(String(255), default="")
    package_dir: Mapped[str] = mapped_column(Text, default="")
    video_path: Mapped[str] = mapped_column(Text, default="")
    thumbnail_path: Mapped[str] = mapped_column(Text, default="")
    report_path: Mapped[str] = mapped_column(Text, default="")
    metadata_path: Mapped[str] = mapped_column(Text, default="")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class GenerationTask(Base):
    """A one-click video generation task."""

    __tablename__ = "generation_tasks"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    topic_id: Mapped[int | None] = mapped_column(ForeignKey("trends.id"), nullable=True)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    platform: Mapped[str] = mapped_column(String(64), nullable=False)
    style: Mapped[str] = mapped_column(String(64), nullable=False)
    duration: Mapped[int] = mapped_column(Integer, nullable=False)
    status: Mapped[str] = mapped_column(String(32), default="completed")
    output_video_path: Mapped[str] = mapped_column(Text, default="")
    output_report_path: Mapped[str] = mapped_column(Text, default="")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


GenerationRecord = GenerationTask
