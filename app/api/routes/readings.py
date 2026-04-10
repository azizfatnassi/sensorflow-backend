

from typing import List, Optional
from datetime import datetime
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from app.schemas.readings import ReadingResponse, ReadingStats
from app.core.dependencies import get_current_user
from app.db.models import User
from app.db.session import get_db
from backend.app.services import readings_service
router = APIRouter(prefix="/api", tags=["readings"])

@router.get("/devices/{device_id}/readings", response_model=List[ReadingResponse])
def get_readings(
    device_id: int,
    from_date: Optional[datetime] = Query(None, alias="from"),
    to_date: Optional[datetime] = Query(None, alias="to"),
    page: int = Query(1, ge=1),
    limit: int = Query(100, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return readings_service.get_device_readings(
        db, device_id, owner_id=current_user.id,
        from_date=from_date, to_date=to_date,
        page=page, limit=limit
    )


@router.get("/devices/{device_id}/readings/stats", response_model=ReadingStats)
def get_stats(
    device_id: int,
    from_date: Optional[datetime] = Query(None, alias="from"),
    to_date: Optional[datetime] = Query(None, alias="to"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return readings_service.get_device_stats(
        db, device_id, owner_id=current_user.id,
        from_date=from_date, to_date=to_date
    )


@router.get("/devices/{device_id}/readings/export")
def export_csv(
    device_id: int,
    from_date: Optional[datetime] = Query(None, alias="from"),
    to_date: Optional[datetime] = Query(None, alias="to"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Pas de response_model ici — StreamingResponse gère ça lui-même."""
    return readings_service.export_readings_csv(
        db, device_id, owner_id=current_user.id,
        from_date=from_date, to_date=to_date
    )