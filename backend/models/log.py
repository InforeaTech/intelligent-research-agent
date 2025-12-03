"""
Log ORM model for caching and audit trail.
"""
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from models.database import Base


class Log(Base):
    """Log model for storing interaction logs and caching results."""
    
    __tablename__ = "logs"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True, index=True)
    timestamp = Column(DateTime(timezone=True), server_default=func.now(), index=True)
    action_type = Column(String, nullable=False, index=True)  # 'search_query', 'generate_profile', 'generate_note', etc.
    user_input = Column(JSON, nullable=True)  # Input parameters as JSON
    search_data = Column(JSON, nullable=True)  # Search query or criteria as JSON
    model_input = Column(Text, nullable=True)  # Prompt sent to LLM
    model_output = Column(Text, nullable=True)  # Raw LLM response
    final_output = Column(Text, nullable=True)  # Processed final output (for caching)

    # Relationships
    user = relationship("User", back_populates="logs")

    def __repr__(self):
        return f"<Log(id={self.id}, action_type='{self.action_type}', timestamp={self.timestamp})>"
