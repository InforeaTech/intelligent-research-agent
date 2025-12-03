"""
User repository for authentication and user management.
"""
from typing import Optional
from sqlalchemy.orm import Session
from datetime import datetime
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from models.user import User
from repositories.base import BaseRepository


class UserRepository(BaseRepository[User]):
    """Repository for User model with authentication-specific methods."""
    
    def __init__(self, db: Session):
        """
        Initialize User repository.
        
        Args:
            db: Database session
        """
        super().__init__(User, db)

    def get_by_email(self, email: str) -> Optional[User]:
        """
        Get user by email address.
        
        Args:
            email: User's email address
            
        Returns:
            User instance or None if not found
        """
        return self.db.query(User).filter(User.email == email).first()

    def get_by_provider(self, provider: str, provider_user_id: str) -> Optional[User]:
        """
        Get user by OAuth provider and provider user ID.
        
        Args:
            provider: OAuth provider name ('google', 'microsoft', 'github')
            provider_user_id: User ID from the OAuth provider
            
        Returns:
            User instance or None if not found
        """
        return self.db.query(User).filter(
            User.provider == provider,
            User.provider_user_id == provider_user_id
        ).first()

    def create_or_update(
        self, 
        email: str, 
        provider: str, 
        provider_user_id: str, 
        name: Optional[str] = None,
        picture: Optional[str] = None
    ) -> User:
        """
        Create a new user or update existing user from OAuth callback.
        
        This method handles the OAuth flow where we either:
        1. Create a new user if they don't exist
        2. Update existing user's info and last_login timestamp
        
        Args:
            email: User's email address
            provider: OAuth provider ('google', 'microsoft', 'github')
            provider_user_id: User ID from OAuth provider
            name: User's display name (optional)
            picture: User's profile picture URL (optional)
            
        Returns:
            User instance (either created or updated)
        """
        # Try to find existing user by provider
        user = self.get_by_provider(provider, provider_user_id)
        
        if user:
            # Update existing user
            user.email = email  # Email might have changed
            if name is not None:
                user.name = name
            if picture is not None:
                user.picture = picture
            user.last_login = datetime.utcnow()
            self.db.commit()
            self.db.refresh(user)
        else:
            # Create new user
            user = User(
                email=email,
                name=name,
                picture=picture,
                provider=provider,
                provider_user_id=provider_user_id
            )
            self.db.add(user)
            self.db.commit()
            self.db.refresh(user)
        
        return user

    def update_last_login(self, user_id: int) -> Optional[User]:
        """
        Update user's last login timestamp.
        
        Args:
            user_id: User's ID
            
        Returns:
            Updated user or None if not found
        """
        user = self.get(user_id)
        if user:
            user.last_login = datetime.utcnow()
            self.db.commit()
            self.db.refresh(user)
        return user
