from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.storage.database import get_db
from app.schemas.system import ActivityItem
from app.services.activity_service import get_recent_activity

router = APIRouter(tags=["activity"])


@router.get("/activity", response_model=list[ActivityItem])
def activity_feed(db: Session = Depends(get_db)):
    entries = get_recent_activity(db)
    return [ActivityItem.model_validate(item) for item in entries]
