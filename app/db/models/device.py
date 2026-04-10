from sqlalchemy import Column,Enum, String, Integer, ForeignKey, DateTime, Boolean, Float
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.db.base import Base

class Device(Base):
    __tablename__="devices"
    id=Column(Integer,primary_key=True,index=True)
    owner_id= Column(Integer,ForeignKey("users.id",ondelete="CASCADE"),nullable=False)
    name = Column(String(100), nullable=False)
    device_type = Column(
        Enum("temperature", "humidity", "pressure", "co2", name="device_type"),
        nullable=False,
    )
    location = Column(String(200), nullable=False)
    unit = Column(String(20), nullable=False)
    api_key = Column(String(200), unique=True, nullable=False, index=True)
    threshold_min = Column(Float, nullable=True)
    threshold_max = Column(Float, nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    owner = relationship("User", back_populates="devices")
    readings = relationship("Reading", back_populates="device", cascade="all, delete")
    alerts = relationship("Alert", back_populates="device", cascade="all, delete")
    