
from typing import List, Optional
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.core.dependencies import get_current_user
from app.db.models import User
from app.schemas.alert import AlertResponse
from app.services import alert_service

router = APIRouter(tags=["alerts"])


@router.get("/api/alerts", response_model=List[AlertResponse])
def list_alerts(
    device_id: Optional[int] = Query(None),
    severity: Optional[str] = Query(None),
    resolved: Optional[bool] = Query(None),
    page: int = Query(1, ge=1),
    limit: int = Query(50, ge=1, le=50),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Retourne les alertes de l'utilisateur.
    Filtres optionnels : ?device_id=1&severity=critical&resolved=false
    """
    return alert_service.get_user_alerts(
        db=db,
        owner_id=current_user.id,
        device_id=device_id,
        severity=severity,
        resolved=resolved,
        page=page,
        limit=limit
    )


@router.patch("/api/alerts/{alert_id}/resolve", response_model=AlertResponse)
def resolve_alert(
    alert_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return alert_service.resolve_alert(db, alert_id, owner_id=current_user.id)


@router.post(
    "/api/devices/{device_id}/alerts/resolve-all",
    status_code=status.HTTP_200_OK
)
def resolve_all_alerts(
    device_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    count = alert_service.resolve_all_device_alerts(db, device_id, owner_id=current_user.id)
    return {"resolved_count": count, "message": f"{count} alerts resolved"}