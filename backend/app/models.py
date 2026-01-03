from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime
from sqlalchemy.sql import func
from .database import Base
from pydantic import BaseModel
from typing import Optional
import datetime

# --- DATABASE MODELS ---
class VerificationJob(Base):
    __tablename__ = "verification_jobs"

    id = Column(Integer, primary_key=True, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    status = Column(String, default="PENDING") # PENDING, PROCESSING, COMPLETED, FAILED
    user_id = Column(Integer, nullable=True) # Link to User
    
    video_filename = Column(String)
    gyro_filename = Column(String)
    
    score = Column(Float, nullable=True)
    is_consistent = Column(Boolean, nullable=True)
    message = Column(String, nullable=True)

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    is_active = Column(Boolean, default=True)
    is_admin = Column(Boolean, default=False)

class ApiKey(Base):
    __tablename__ = "api_keys"
    id = Column(Integer, primary_key=True, index=True)
    key = Column(String, unique=True, index=True)
    user_id = Column(Integer) # ForeignKey in real app
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

# --- API SCHEMAS ---
class VerificationResponse(BaseModel):
    id: int
    status: str
    score: Optional[float] = None
    verified: Optional[bool] = None
    message: Optional[str] = None

class JobStatus(BaseModel):
    id: int
    status: str
