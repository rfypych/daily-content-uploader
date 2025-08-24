from sqlalchemy import Column, Integer, String, DateTime, Text, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from database import Base
from datetime import datetime
import bcrypt

class Content(Base):
    __tablename__ = "contents"
    
    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String(255), nullable=False)
    file_path = Column(String(500), nullable=False)
    caption = Column(Text)
    platform = Column(String(50), nullable=False)  # instagram, tiktok, both
    file_type = Column(String(100))  # image/video, video/mp4, etc
    file_size = Column(Integer)  # File size in bytes
    status = Column(String(50), default="uploaded")  # uploaded, scheduled, published, failed
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationship
    schedules = relationship("Schedule", back_populates="content")

class Schedule(Base):
    __tablename__ = "schedules"
    
    id = Column(Integer, primary_key=True, index=True)
    content_id = Column(Integer, ForeignKey("contents.id", ondelete="CASCADE"))
    platform = Column(String(50), nullable=False)  # instagram, tiktok
    scheduled_time = Column(DateTime, nullable=False)
    status = Column(String(50), default="pending")  # pending, completed, failed
    error_message = Column(Text)
    retry_count = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationship
    content = relationship("Content", back_populates="schedules")

class Account(Base):
    __tablename__ = "accounts"
    
    id = Column(Integer, primary_key=True, index=True)
    platform = Column(String(50), nullable=False)  # instagram, tiktok
    username = Column(String(255), nullable=False)
    password = Column(Text, nullable=False)  # Encrypted
    is_active = Column(Boolean, default=True)
    last_login = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def set_password(self, password: str):
        """Hash and set password"""
        salt = bcrypt.gensalt()
        self.password = bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')
    
    def check_password(self, password: str) -> bool:
        """Check if password matches"""
        return bcrypt.checkpw(password.encode('utf-8'), self.password.encode('utf-8'))
