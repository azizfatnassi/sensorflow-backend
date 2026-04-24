from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class AlertResponse(BaseModel):
    id: int
    device_id: int
    value: float
    severity: str        # "warning" ou "critical"
    message: str
    resolved: bool
    resolved_at: Optional[datetime] = None 
    created_at: datetime

    model_config = {"from_attributes": True}


class AlertResolve(BaseModel):
    """Body optionnel pour ajouter une note de résolution plus tard."""
    note: Optional[str] = None