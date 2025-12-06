"""
Company repository for company analysis management.
"""
from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import or_, desc, asc, func
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from models.company import Company
from repositories.base import BaseRepository


class CompanyRepository(BaseRepository[Company]):
    """Repository for Company model with search and filtering."""
    
    def __init__(self, db: Session):
        """
        Initialize Company repository.
        
        Args:
            db: Database session
        """
        super().__init__(Company, db)

    def create(
        self,
        user_id: Optional[int],
        name: str,
        overview: str,
        search_provider: str,
        model_provider: str,
        ticker: Optional[str] = None,
        industry: Optional[str] = None,
        headquarters: Optional[str] = None,
        website: Optional[str] = None,
        financials: Optional[str] = None,
        competitors: Optional[str] = None,
        swot_strengths: Optional[str] = None,
        swot_weaknesses: Optional[str] = None,
        swot_opportunities: Optional[str] = None,
        swot_threats: Optional[str] = None,
        from_cache: bool = False
    ) -> Company:
        """
        Create a new company analysis record.
        """
        company = Company(
            user_id=user_id,
            name=name,
            ticker=ticker,
            industry=industry,
            headquarters=headquarters,
            website=website,
            overview=overview,
            financials=financials,
            competitors=competitors,
            swot_strengths=swot_strengths,
            swot_weaknesses=swot_weaknesses,
            swot_opportunities=swot_opportunities,
            swot_threats=swot_threats,
            search_provider=search_provider,
            model_provider=model_provider,
            from_cache=from_cache
        )
        self.db.add(company)
        self.db.commit()
        self.db.refresh(company)
        return company

    def get_by_user(
        self, 
        user_id: int, 
        skip: int = 0, 
        limit: int = 20, 
        sort: str = "recent"
    ) -> List[Company]:
        """
        Get all companies for a specific user with pagination and sorting.
        """
        query = self.db.query(Company).filter(Company.user_id == user_id)
        
        # Apply sorting
        if sort == "recent":
            query = query.order_by(desc(Company.timestamp))
        elif sort == "name":
            query = query.order_by(asc(Company.name))
        elif sort == "industry":
            query = query.order_by(asc(Company.industry))
        else:
            query = query.order_by(desc(Company.timestamp))
        
        return query.offset(skip).limit(limit).all()

    def search(
        self, 
        user_id: int, 
        query: str, 
        skip: int = 0, 
        limit: int = 20
    ) -> List[Company]:
        """
        Search companies by name, industry, or content.
        """
        search_pattern = f"%{query}%"
        
        return self.db.query(Company).filter(
            Company.user_id == user_id,
            or_(
                Company.name.ilike(search_pattern),
                Company.industry.ilike(search_pattern),
                Company.ticker.ilike(search_pattern),
                Company.overview.ilike(search_pattern)
            )
        ).order_by(desc(func.length(Company.overview))).offset(skip).limit(limit).all()

    def count_by_user(self, user_id: int) -> int:
        """Count total companies for a user."""
        return self.db.query(Company).filter(Company.user_id == user_id).count()

    def delete_by_user(self, company_id: int, user_id: int) -> bool:
        """Delete a company record (with authorization check)."""
        company = self.db.query(Company).filter(
            Company.id == company_id,
            Company.user_id == user_id
        ).first()
        
        if company:
            self.db.delete(company)
            self.db.commit()
            return True
        return False
