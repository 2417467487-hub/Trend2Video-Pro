"""SQLite database setup and repository helpers."""

from __future__ import annotations

from datetime import datetime
from typing import Any

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from config.settings import settings


engine = create_engine(settings.database_url, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def init_db() -> None:
    """Create database tables."""
    from src.database.models import Base

    Base.metadata.create_all(bind=engine)


def upsert_topics(topics: list[dict[str, Any]]) -> int:
    """Insert topics by URL and update snapshots for duplicates."""
    from src.database.models import Topic, TopicSnapshot

    init_db()
    db = SessionLocal()
    updated = 0
    try:
        for item in topics:
            url = item.get("url") or f"manual://{item.get('title', 'untitled')}"
            topic = db.query(Topic).filter(Topic.url == url).one_or_none()
            collected_at = _parse_datetime(item.get("collected_at"))
            if topic is None:
                topic = Topic(url=url, created_at=datetime.utcnow())
                db.add(topic)
            topic.source = item.get("source", "unknown")
            topic.title = item.get("title", "Untitled trend")
            topic.description = item.get("description", "")
            topic.raw_score = float(item.get("raw_score") or 0)
            topic.trend_score = float(item.get("trend_score") or 0)
            topic.competition_score = float(item.get("competition_score") or 0)
            topic.monetization_score = float(item.get("monetization_score") or 0)
            topic.audience_fit_score = float(item.get("audience_fit_score") or 0)
            topic.urgency_score = float(item.get("urgency_score") or 0)
            topic.final_opportunity_score = float(item.get("final_opportunity_score") or 0)
            topic.recommendation_reason = item.get("recommendation_reason", "")
            topic.risk_note = item.get("risk_note", "")
            topic.status = item.get("status", "new")
            topic.collected_at = collected_at
            db.flush()
            for metric_name in ["raw_score", "final_opportunity_score", "trend_score"]:
                db.add(
                    TopicSnapshot(
                        topic_id=topic.id,
                        metric_name=metric_name,
                        metric_value=float(item.get(metric_name) or 0),
                        collected_at=collected_at,
                    )
                )
            updated += 1
        db.commit()
        return updated
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


def list_topics(limit: int = 20) -> list[dict[str, Any]]:
    """List topics by final opportunity score descending."""
    from src.database.models import Topic

    init_db()
    db = SessionLocal()
    try:
        rows = db.query(Topic).order_by(Topic.final_opportunity_score.desc()).limit(limit).all()
        return [_topic_to_dict(row) for row in rows]
    finally:
        db.close()


def get_topic(topic_id: int) -> dict[str, Any] | None:
    """Return one topic by ID."""
    from src.database.models import Topic

    init_db()
    db = SessionLocal()
    try:
        row = db.query(Topic).filter(Topic.id == topic_id).one_or_none()
        return _topic_to_dict(row) if row else None
    finally:
        db.close()


def save_generation_task(
    *,
    topic_id: int | None,
    title: str,
    platform: str,
    style: str,
    duration: int,
    status: str,
    output_video_path: str,
    output_report_path: str,
) -> int:
    """Persist a generation task."""
    from src.database.models import GenerationTask

    init_db()
    db = SessionLocal()
    try:
        task = GenerationTask(
            topic_id=topic_id,
            title=title,
            platform=platform,
            style=style,
            duration=duration,
            status=status,
            output_video_path=output_video_path,
            output_report_path=output_report_path,
        )
        db.add(task)
        db.commit()
        db.refresh(task)
        return int(task.id)
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


def save_viral_prediction(
    *,
    topic_id: int | None,
    title: str,
    platform: str,
    prediction: dict[str, Any],
) -> int:
    """Persist a viral prediction for trend history and future training."""
    from src.database.models import ViralPrediction

    init_db()
    db = SessionLocal()
    try:
        row = ViralPrediction(
            topic_id=topic_id,
            title=title,
            platform=platform,
            viral_probability=float(prediction.get("viral_probability", 0)),
            predicted_view_range=prediction.get("predicted_view_range", prediction.get("predicted_views", "")),
            confidence_level=prediction.get("confidence_level", ""),
            explanation=prediction.get("explanation", ""),
        )
        db.add(row)
        db.commit()
        db.refresh(row)
        return int(row.id)
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


def save_publish_package_record(
    *,
    task_id: int | None,
    title: str,
    package: dict[str, Any],
) -> int:
    """Persist a publish package export."""
    from src.database.models import PublishPackage

    init_db()
    db = SessionLocal()
    try:
        files = package.get("files", {})
        row = PublishPackage(
            task_id=task_id,
            title=title,
            package_dir=package.get("package_dir", ""),
            video_path=files.get("video.mp4", ""),
            thumbnail_path=files.get("thumbnail.png", ""),
            report_path=files.get("quality_report.md", ""),
            metadata_path=files.get("metadata.json", ""),
        )
        db.add(row)
        db.commit()
        db.refresh(row)
        return int(row.id)
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


def save_creator_memory_record(
    *,
    creator_name: str,
    topic_title: str,
    platform: str,
    creator_fit_score: float,
    viral_probability: float,
    actual_views: int = 0,
    notes: str = "",
) -> int:
    """Persist creator memory as structured training data."""
    from src.database.models import CreatorMemoryRecord

    init_db()
    db = SessionLocal()
    try:
        row = CreatorMemoryRecord(
            creator_name=creator_name,
            topic_title=topic_title,
            platform=platform,
            creator_fit_score=creator_fit_score,
            viral_probability=viral_probability,
            actual_views=actual_views,
            notes=notes,
        )
        db.add(row)
        db.commit()
        db.refresh(row)
        return int(row.id)
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


def _parse_datetime(value: Any) -> datetime:
    if isinstance(value, datetime):
        return value
    if isinstance(value, str):
        try:
            return datetime.fromisoformat(value.replace("Z", "+00:00")).replace(tzinfo=None)
        except ValueError:
            return datetime.utcnow()
    return datetime.utcnow()


def _topic_to_dict(row: Any) -> dict[str, Any]:
    return {
        "id": row.id,
        "source": row.source,
        "title": row.title,
        "url": row.url,
        "description": row.description,
        "raw_score": row.raw_score,
        "trend_score": row.trend_score,
        "competition_score": row.competition_score,
        "monetization_score": row.monetization_score,
        "audience_fit_score": row.audience_fit_score,
        "urgency_score": row.urgency_score,
        "final_opportunity_score": row.final_opportunity_score,
        "recommendation_reason": row.recommendation_reason,
        "risk_note": row.risk_note,
        "status": row.status,
        "collected_at": row.collected_at.isoformat() if row.collected_at else "",
        "created_at": row.created_at.isoformat() if row.created_at else "",
    }
