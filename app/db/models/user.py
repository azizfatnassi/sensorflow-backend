
from sqlalchemy import Column, String, Integer, Boolean, DateTime, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.base import Base


class User(Base):
    __tablename__="users" 
    id=Column(Integer,primary_key=True,index=True)

    email=Column(String(255),unique=True,index=True,nullable=False)
    hashed_password= Column(String(255),nullable= False)
    full_name = Column( String(100),nullable=False)
    role= Column(Enum("user","admin",name="user_role",default="user"))
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    devices = relationship("Device",back_populates="owner",cascade="all, delete-orphan")

