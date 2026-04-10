import secrets
from typing import List, Optional
from sqlalchemy.orm import Session
from fastapi import HTTPException

from app.db.models import Device  # ton modèle SQLAlchemy
from app.schemas.device import DeviceCreate, DeviceUpdate
def generate_api_key()->str:
    return f"sf_{secrets.token_urlsafe(32)}"

def create_device(db:Session, data: DeviceCreate, owner_id: int)->Device:
    api_key= generate_api_key()
    
    device= Device(**data.model_dump(),
                   api_key=api_key,
                   owner_id=owner_id)
    db.add(device)
    db.commit()
    db.refresh(device)
    return device


def get_user_devices(db:Session,owner_id:int)->List[Device]:
    return db.query(Device).filter(Device.owner_id==owner_id).all()

def get_device_by_id(db:Session,device_id:int,owner_id:int)->Device:
   device = db.query(Device).filter(
        Device.id == device_id,
        Device.owner_id == owner_id
    ).first()
   if not device:
        raise HTTPException(status_code=404, detail="Device not found")
   return device

def update_device(
    db: Session,
    device_id: int,
    owner_id: int,
    data: DeviceUpdate
) -> Device:
    device = get_device_by_id(db, device_id, owner_id)
    # On ne met à jour que les champs envoyés (exclude_unset)
    update_data = data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(device, field, value)
    db.commit()
    db.refresh(device)
    return device

def delete_device(db: Session, device_id: int, owner_id: int) -> None:
    device = get_device_by_id(db, device_id, owner_id)
    db.delete(device)
    db.commit()


def regenerate_api_key(db: Session, device_id: int, owner_id: int) -> Device:
    device = get_device_by_id(db, device_id, owner_id)
    device.api_key = generate_api_key()
    db.commit()
    db.refresh(device)
    return device