from datetime import datetime, timezone
from sqlalchemy.orm import Session
from sqlalchemy import func
from fastapi import HTTPException
from fastapi.responses import StreamingResponse
import csv
import io 
from typing import List,Optional
from app.db.models import Device, Reading
from app.schemas.readings import ReadingCreate
from app.services import alert_service   # ← on délègue proprement
from app.schemas.readings import  ReadingCreate



def ingest_reading(db: Session, device: Device, data: ReadingCreate) -> Reading:
    timestamp = data.timestamp or datetime.now(timezone.utc)

    reading = Reading(
        device_id=device.id,
        value=data.value,
        timestamp=timestamp,
        #alert=False
    )

    #alert = False
    db.add(reading)
    db.flush()
    if device.threshold_min is not None and data.value < device.threshold_min:
        #alert = True
        alert_service.create_alert(     # ← plus de _create_alert interne
            db=db,
            device=device,
            value=data.value,
            reading_id=reading.id,
            severity="warning",
            message=f"Value {data.value} below minimum {device.threshold_min}"
        )

    if device.threshold_max is not None and data.value > device.threshold_max:
       # alert_triggered = True
        alert_service.create_alert(
            db=db,
            device=device,
            value=data.value,
            reading_id=reading.id,
            severity="critical",
            message=f"Value {data.value} above maximum {device.threshold_max}"
        )

   # reading.alert = alert
    #db.add(reading)
    db.commit()        # ← un seul commit : lecture + alertes ensemble
    db.refresh(reading)
    return reading



def get_device_readings( 
        db:Session,
        device_id:int,
        owner_id: int,
        from_date: Optional[datetime]=None,
        to_date:Optional[datetime]=None,
        page: int=1,
        limit:int=100)->List[Reading]:
    
    device=db.query(Device).filter(Device.id==device_id,
                                   Device.owner_id==owner_id).first()
    if not device:
        raise HTTPException(status_code=404,detail="Device not found")
    query = db.query(Reading).filter(Reading.device_id == device_id)

    if from_date:
        query= query.filter(Reading.timestamp>=from_date)
    if to_date:
        query=query.filter(Reading.timestamp<=from_date)

    offset=(page-1)*limit
    return query.order_by(Reading.timestamp.desc()).offset(offset).limit(limit).all()


def get_device_stats(
        db:Session,
        device_id:int,
        owner_id,
        from_date:Optional[datetime]=None,
        to_date:Optional[datetime]=None )->dict:
    
    device=db.query(Device).filter(Device.id==device_id,Device.owner_id==owner_id).first()
    if not device:
        raise HTTPException(status_code=404,detail="Device not found")
    
    query= db.query(
        func.min(Reading.value).label("min"),
        func.max(Reading.value).label("max"),
        func.avg(Reading.value).label("avg"),
        func.count(Reading.id).label("count")

    ).filter(Reading.device_id==device_id)

    if from_date:
        query=query.filter(Reading.timestamp>=from_date)
    if to_date:
        query=query.filter(Reading.timestamp<=to_date)

    result=query.first()

    return {
        "min":round(result.min,2)if result.min is not None else None,
        "max": round(result.max, 2) if result.max is not None else None,
        "avg": round(result.avg, 2) if result.avg is not None else None,
        "count": result.count
    }


def export_readings_csv(
        db:Session,
        device_id:int,
        owner_id:int,
        from_date:Optional[datetime]=None,
        to_date:Optional[datetime]=None)->StreamingResponse:
    device = db.query(Device).filter(
        Device.id == device_id,
        Device.owner_id == owner_id
    ).first()
    if not device:
        raise HTTPException(status_code=404, detail="Device not found")

    query = db.query(Reading).filter(Reading.device_id == device_id)
    if from_date:
        query = query.filter(Reading.timestamp >= from_date)
    if to_date:
        query = query.filter(Reading.timestamp <= to_date)

    readings = query.order_by(Reading.timestamp.asc()).all()

    output= io.StringIo()
    writer = csv.writer(output)

    writer.writerow(["id","device_id","value","timestamp","alert_triggered"])
    
    for r in readings :
        writer.writerow([r.id,r.device_id,r.value,r.timestamp,r.alert])
    output.seek(0)

    return StreamingResponse(
        iter([output.getvalue()]),
        media_type="text/csv",
        headers={
            "Content-Disposition":f"attachment;filename=device_{device_id}_readings.csv"
        }
    )

    



