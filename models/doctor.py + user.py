doctor.py + user.py
# backend/app/models/doctor.py
from sqlalchemy import Column, Integer, String, Text, Numeric, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from database.database import Base

class Doctor(Base):
    __tablename__ = "doctors"
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    full_name = Column(String(100), nullable=False)
    specialty = Column(String(100))
    description = Column(Text)
    price = Column(Numeric(10,2))
    rating_avg = Column(Numeric(3,2), default=0)
    total_reviews = Column(Integer, default=0)
    is_hot = Column(Boolean, default=False)
    is_deleted = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    deleted_at = Column(DateTime)
    deleted_by = Column(Integer, ForeignKey("users.id"))