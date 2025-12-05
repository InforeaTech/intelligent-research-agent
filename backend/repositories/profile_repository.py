"""
Profile repository for research profile management.
"""
from typing import List, Optional
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import or_, desc, asc, func
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from models.profile import Profile
from repositories.base import BaseRepository


class ProfileRepository(BaseRepository[Profile]):
    """Repository for Profile model with search and filtering."""
    
    def __init__(self, db: Session):
        """
        Initialize Profile repository.
        
        Args:
            db: Database session
        """
        super().__init__(Profile, db)

    def get_by_user(
        self, 
        user_id: int, 
        skip: int = 0, 
        limit: int = 20, 
        sort: str = "recent"
    ) -> List[Profile]:
        """
        Get all profiles for a specific user with pagination and sorting.
        
        Args:
            user_id: User's ID
            skip: Number of records to skip (for pagination)
            limit: Maximum number of records to return
            sort: Sorting method ('recent', 'name', 'company')
            
        Returns:
            List of Profile instances
        """
        query = self.db.query(Profile).filter(Profile.user_id == user_id)
        
        # Apply sorting
        if sort == "recent":
            query = query.order_by(desc(Profile.timestamp))
        elif sort == "name":
            query = query.order_by(asc(Profile.name))
        elif sort == "company":
            query = query.order_by(asc(Profile.company))
        else:
            query = query.order_by(desc(Profile.timestamp))
        
        return query.offset(skip).limit(limit).all()

    def search(
        self, 
        user_id: int, 
        query: str, 
        skip: int = 0, 
        limit: int = 20
    ) -> List[Profile]:
        """
        Search profiles by name, company, or content.
        
        Performs case-insensitive search across:
        - Name
        - Company
        - Profile text content
        
        Args:
            user_id: User's ID
            query: Search query string
            skip: Number of records to skip
            limit: Maximum number of records to return
            
        Returns:
            List of matching Profile instances
        """
        search_pattern = f"%{query}%"
        
        return self.db.query(Profile).filter(
            Profile.user_id == user_id,
            or_(
                Profile.name.ilike(search_pattern),
                Profile.company.ilike(search_pattern),
                Profile.profile_text.ilike(search_pattern)
            )
        ).order_by(desc(func.length(Profile.profile_text))).offset(skip).limit(limit).all()

    def get_with_notes(self, profile_id: int, user_id: int) -> Optional[Profile]:
        """
        Get a profile with all its notes eagerly loaded.
        
        This method uses joinedload to fetch the profile and all
        associated notes in a single query (no N+1 problem).
        
        Args:
            profile_id: Profile's ID
            user_id: User's ID (for authorization)
            
        Returns:
            Profile instance with notes loaded, or None if not found
        """
        return self.db.query(Profile).options(
            joinedload(Profile.notes)
        ).filter(
            Profile.id == profile_id,
            Profile.user_id == user_id
        ).first()

    def count_by_user(self, user_id: int) -> int:
        """
        Count total profiles for a user.
        
        Args:
            user_id: User's ID
            
        Returns:
            Total count of profiles
        """
        return self.db.query(Profile).filter(Profile.user_id == user_id).count()

    def delete_by_user(self, profile_id: int, user_id: int) -> bool:
        """
        Delete a profile (with authorization check).
        
        Args:
            profile_id: Profile's ID to delete
            user_id: User's ID (for authorization)
            
        Returns:
            True if deleted, False if not found or unauthorized
        """
        profile = self.db.query(Profile).filter(
            Profile.id == profile_id,
            Profile.user_id == user_id
        ).first()
        
        if profile:
            self.db.delete(profile)
            self.db.commit()
            return True
        return False

    def get_recent_by_user(self, user_id: int, limit: int = 5) -> List[Profile]:
        """
        Get most recent profiles for a user.
        
        Useful for dashboard "recent history" widgets.
        
        Args:
            user_id: User's ID
            limit: Number of recent profiles to return
            
        Returns:
            List of most recent Profile instances
        """
        return self.db.query(Profile).filter(
            Profile.user_id == user_id
        ).order_by(desc(Profile.timestamp)).limit(limit).all()
