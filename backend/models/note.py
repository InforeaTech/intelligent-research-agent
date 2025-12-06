"""
Note ORM model.
"""
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from models.database import Base


class Note(Base):
    """Note model for storing generated LinkedIn connection notes."""
    
    __tablename__ = "notes"

    id = Column(Integer, primary_key=True, index=True)
    profile_id = Column(Integer, ForeignKey("profiles.id"), nullable=False, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    note_text = Column(Text, nullable=False)
    tone = Column(String, nullable=False)  # 'professional', 'casual', 'enthusiastic', 'formal'
    length = Column(String, nullable=False)  # 'short', 'medium', or 'long'
    context = Column(String, nullable=True)  # Optional context/reason
    model_provider = Column(String, nullable=False)  # 'openai', 'gemini', 'grok'
    from_cache = Column(Boolean, default=False)
    timestamp = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    profile = relationship("Profile", back_populates="notes")
    user = relationship("User", back_populates="notes")

    def __repr__(self):
        return f"<Note(id={self.id}, profile_id={self.profile_id}, tone='{self.tone}')>"
