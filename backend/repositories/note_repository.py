"""
Note repository for LinkedIn connection note management.
"""
from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import desc
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from models.note import Note
from repositories.base import BaseRepository


class NoteRepository(BaseRepository[Note]):
    """Repository for Note model."""
    
    def __init__(self, db: Session):
        """
        Initialize Note repository.
        
        Args:
            db: Database session
        """
        super().__init__(Note, db)

    def get_by_profile(self, profile_id: int) -> List[Note]:
        """
        Get all notes for a specific profile.
        
        Notes are ordered chronologically (oldest first) to see
        the evolution of note generation for a profile.
        
        Args:
            profile_id: Profile's ID
            
        Returns:
            List of Note instances
        """
        return self.db.query(Note).filter(
            Note.profile_id == profile_id
        ).order_by(Note.timestamp).all()

    def get_by_user(
        self, 
        user_id: int, 
        skip: int = 0, 
        limit: int = 20
    ) -> List[Note]:
        """
        Get all notes for a specific user with pagination.
        
        Ordered by most recent first.
        
        Args:
            user_id: User's ID
            skip: Number of records to skip
            limit: Maximum number of records to return
            
        Returns:
            List of Note instances
        """
        return self.db.query(Note).filter(
            Note.user_id == user_id
        ).order_by(desc(Note.timestamp)).offset(skip).limit(limit).all()

    def get_latest_for_profile(self, profile_id: int) -> Optional[Note]:
        """
        Get the most recent note for a profile.
        
        Useful for showing "last generated note" or suggesting
        cached notes to users.
        
        Args:
            profile_id: Profile's ID
            
        Returns:
            Most recent Note instance or None
        """
        return self.db.query(Note).filter(
            Note.profile_id == profile_id
        ).order_by(desc(Note.timestamp)).first()

    def count_by_profile(self, profile_id: int) -> int:
        """
        Count total notes for a profile.
        
        Args:
            profile_id: Profile's ID
            
        Returns:
            Total count of notes
        """
        return self.db.query(Note).filter(Note.profile_id == profile_id).count()

    def count_by_user(self, user_id: int) -> int:
        """
        Count total notes for a user.
        
        Args:
            user_id: User's ID
            
        Returns:
            Total count of notes
        """
        return self.db.query(Note).filter(Note.user_id == user_id).count()

    def delete_by_profile(self, profile_id: int) -> int:
        """
        Delete all notes for a profile.
        
        This is typically called when a profile is deleted
        (though cascade delete should handle this automatically).
        
        Args:
            profile_id: Profile's ID
            
        Returns:
            Number of notes deleted
        """
        count = self.count_by_profile(profile_id)
        self.db.query(Note).filter(Note.profile_id == profile_id).delete()
        self.db.commit()
        return count
