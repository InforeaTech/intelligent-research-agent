"""
Profile ORM model.
"""
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from models.database import Base


class Profile(Base):
    """Profile model for storing generated research profiles."""
    
    __tablename__ = "profiles"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    name = Column(String, nullable=False, index=True)
    company = Column(String, nullable=True)
    additional_info = Column(String, nullable=True)
    profile_text = Column(Text, nullable=False)
    search_provider = Column(String, nullable=False)  # 'ddg', 'serper'
    model_provider = Column(String, nullable=False)   # 'openai', 'gemini', 'grok'
    from_cache = Column(Boolean, default=False)
    timestamp = Column(DateTime(timezone=True), server_default=func.now(), index=True)

    # Relationships
    user = relationship("User", back_populates="profiles")
    notes = relationship("Note", back_populates="profile", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Profile(id={self.id}, name='{self.name}', company='{self.company}')>"
