"""
Company ORM model.
Stores company research/analysis data.
"""
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from models.database import Base


class Company(Base):
    """Company model for storing company research and analysis."""
    
    __tablename__ = "companies"

    # Primary key
    id = Column(Integer, primary_key=True, index=True)
    
    # Foreign key to users (nullable for anonymous usage)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True, index=True)
    
    # Basic company info
    name = Column(String(255), nullable=False, index=True)
    ticker = Column(String(10), nullable=True)  # Stock ticker symbol
    industry = Column(String(100), nullable=True)
    headquarters = Column(String(255), nullable=True)
    website = Column(String(500), nullable=True)
    
    # Generated content
    overview = Column(Text, nullable=False)  # Company overview/description
    financials = Column(Text, nullable=True)  # Financial summary
    competitors = Column(Text, nullable=True)  # JSON array of competitors
    
    # SWOT Analysis (separate columns for easier querying)
    swot_strengths = Column(Text, nullable=True)
    swot_weaknesses = Column(Text, nullable=True)
    swot_opportunities = Column(Text, nullable=True)
    swot_threats = Column(Text, nullable=True)
    
    # Provider tracking
    search_provider = Column(String(50), nullable=False)  # 'ddg', 'serper'
    model_provider = Column(String(50), nullable=False)   # 'gemini', 'openai', 'grok'
    from_cache = Column(Boolean, default=False)
    
    # Timestamp
    timestamp = Column(DateTime(timezone=True), server_default=func.now(), index=True)

    # Relationships
    user = relationship("User", back_populates="companies")

    def __repr__(self):
        return f"<Company(id={self.id}, name='{self.name}', industry='{self.industry}')>"
    
    def to_dict(self):
        """Convert to dictionary for JSON serialization."""
        return {
            "id": self.id,
            "user_id": self.user_id,
            "name": self.name,
            "ticker": self.ticker,
            "industry": self.industry,
            "headquarters": self.headquarters,
            "website": self.website,
            "overview": self.overview,
            "financials": self.financials,
            "competitors": self.competitors,
            "swot": {
                "strengths": self.swot_strengths,
                "weaknesses": self.swot_weaknesses,
                "opportunities": self.swot_opportunities,
                "threats": self.swot_threats
            },
            "search_provider": self.search_provider,
            "model_provider": self.model_provider,
            "from_cache": self.from_cache,
            "timestamp": self.timestamp.isoformat() if self.timestamp else None
        }
