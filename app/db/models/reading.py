from sqlalchemy import Column, DateTime, Float, ForeignKey, Index, Integer
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.db.base import Base


class Reading(Base):
    __tablename__ = "readings"

    id = Column(Integer, primary_key=True, index=True)
    device_id = Column(Integer, ForeignKey("devices.id", ondelete="CASCADE"), nullable=False)
    value = Column(Float, nullable=False)
    timestamp = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    device = relationship("Device", back_populates="readings")
    alert = relationship("Alert", back_populates="reading", uselist=False)

    __table_args__ = (
        Index("ix_readings_device_timestamp", "device_id", "timestamp"),
    )