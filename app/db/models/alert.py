from sqlalchemy import Boolean, Column, DateTime, Enum, ForeignKey, Integer, String
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.db.base import Base


class Alert(Base):
    __tablename__ = "alerts"

    id = Column(Integer, primary_key=True, index=True)
    device_id = Column(Integer, ForeignKey("devices.id", ondelete="CASCADE"), nullable=False)
    reading_id = Column(Integer, ForeignKey("readings.id", ondelete="CASCADE"), nullable=False)
    severity = Column(
        Enum("warning", "critical", name="alert_severity"),
        nullable=False,
    )
    message = Column(String(500), nullable=False)
    resolved = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    device = relationship("Device", back_populates="alerts")
    reading = relationship("Reading", back_populates="alert")