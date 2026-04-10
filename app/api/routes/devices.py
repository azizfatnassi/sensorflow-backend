

from typing import List
from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.core.dependencies import get_current_user  # ta dépendance auth existante
from app.db.models import User
from app.db.models.device import Device
from app.schemas.device import (
    DeviceCreate, DeviceUpdate,
    DeviceResponse, DeviceCreateResponse
)
from app.services import device_service

router= APIRouter(prefix="/api/devices",tags=["Devices"])

@router.post("",response_model=DeviceCreateResponse,status_code=status.HTTP_201_CREATED)
def create_device(data:DeviceCreate,
                  db:Session=Depends(get_db),
                  current_user:User=Depends(get_current_user)):
    return device_service.create_device(db,data,current_user.id)

@router.get("",response_model=List[DeviceResponse])
def list_devices(db:Session=Depends(get_db),current_user:User=Depends(get_current_user)):
    return device_service.get_user_devices(db,current_user.id)
@router.get("/{device_id}", response_model=DeviceResponse)
def get_device(
    device_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return device_service.get_device_by_id(db, device_id, owner_id=current_user.id)


@router.put("/{device_id}", response_model=DeviceResponse)
def update_device(
    device_id: int,
    data: DeviceUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return device_service.update_device(db, device_id, owner_id=current_user.id, data=data)


@router.delete("/{device_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_device(
    device_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    device_service.delete_device(db, device_id, owner_id=current_user.id)


@router.post("/{device_id}/regenerate-key", response_model=DeviceCreateResponse)
def regenerate_key(
    device_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Génère une nouvelle api_key. L'ancienne est invalidée immédiatement."""
    return device_service.regenerate_api_key(db, device_id, owner_id=current_user.id)