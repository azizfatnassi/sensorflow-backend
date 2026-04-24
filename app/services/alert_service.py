from datetime import datetime, timezone
from typing import List, Optional
from sqlalchemy.orm import Session
from fastapi import HTTPException

from app.db.models import Device, Alert


def create_alert(
    db: Session,
    device: Device,
    value: float,
    reading_id: int,      # ← ajouté
    
    severity: str,
    message: str
) -> Alert:
    """
    Crée une alerte sans commit — le commit est fait par reading_service
    pour garder lecture + alerte dans une seule transaction.
    """
    alert = Alert(
        device_id=device.id,
        value=value,
        reading_id=reading_id, 
        severity=severity,
        message=message,
        resolved=False
    )
    db.add(alert)
    return alert


def get_user_alerts(
    db: Session,
    owner_id: int,
    device_id: Optional[int] = None,
    severity: Optional[str] = None,
    resolved: Optional[bool] = None,
    page: int = 1,
    limit: int = 50
) -> List[Alert]:
    """
    Retourne les alertes de l'utilisateur avec filtres optionnels.
    On joint avec Device pour vérifier le ownership.
    """
    query = (
        db.query(Alert)
        .join(Device, Alert.device_id == Device.id)
        .filter(Device.owner_id == owner_id)
    )

    if device_id is not None:
        query = query.filter(Alert.device_id == device_id)
    if severity is not None:
        query = query.filter(Alert.severity == severity)
    if resolved is not None:
        query = query.filter(Alert.resolved == resolved)

    offset = (page - 1) * limit
    return query.order_by(Alert.created_at.desc()).offset(offset).limit(limit).all()


def resolve_alert(db: Session, alert_id: int, owner_id: int) -> Alert:
    """Résout une alerte — vérifie le ownership via le device."""
    alert = (
        db.query(Alert)
        .join(Device, Alert.device_id == Device.id)
        .filter(Alert.id == alert_id, Device.owner_id == owner_id)
        .first()
    )
    if not alert:
        raise HTTPException(status_code=404, detail="Alert not found")
    if alert.resolved:
        raise HTTPException(status_code=400, detail="Alert already resolved")

    alert.resolved = True
    alert.resolved_at = datetime.now(timezone.utc)
    db.commit()
    db.refresh(alert)
    return alert


def resolve_all_device_alerts(db: Session, device_id: int, owner_id: int) -> int:
    """
    Résout toutes les alertes actives d'un appareil.
    Retourne le nombre d'alertes résolues.
    """
    # Vérifier que le device appartient à l'utilisateur
    device = (
        db.query(Device)
        .filter(Device.id == device_id, Device.owner_id == owner_id)
        .first()
    )
    if not device:
        raise HTTPException(status_code=404, detail="Device not found")

    now = datetime.now(timezone.utc)
    updated = (
        db.query(Alert)
        .filter(Alert.device_id == device_id, Alert.resolved == False)
        .all()
    )
    for alert in updated:
        alert.resolved = True
        alert.resolved_at = now

    db.commit()
    return len(updated)