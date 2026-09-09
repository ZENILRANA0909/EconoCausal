from sqlalchemy.orm import Session
from app.models.activity import ActivityLog


def log_activity(db: Session, event_type: str, message: str, firmware_id: str = "") -> ActivityLog:
    entry = ActivityLog(event_type=event_type, message=message, firmware_id=firmware_id)
    db.add(entry)
    db.commit()
    db.refresh(entry)
    return entry


def get_recent_activity(db: Session, limit: int = 50):
    return (
        db.query(ActivityLog)
        .order_by(ActivityLog.created_at.desc())
        .limit(limit)
        .all()
    )
