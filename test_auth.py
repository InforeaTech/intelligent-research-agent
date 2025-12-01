"""
Authentication Test Suite
Tests for OIDC authentication functionality including JWT, user management, and protected routes.
"""

import sys
import os
import pytest
from datetime import datetime, timedelta

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

from auth import create_access_token, verify_access_token, OAUTH_PROVIDERS
from database import DatabaseManager


class TestJWTTokens:
    """Test JWT token creation and verification"""
    
    def test_create_token(self):
        """Test JWT token creation"""
        user_data = {"user_id": 1, "email": "test@example.com", "name": "Test User"}
        token = create_access_token(user_data)
        
        assert isinstance(token, str)
        assert len(token) > 0
        print("✓ JWT token created successfully")
    
    def test_verify_valid_token(self):
        """Test verifying a valid JWT token"""
        user_data = {"user_id": 1, "email": "test@example.com"}
        token = create_access_token(user_data)
        
        payload = verify_access_token(token)
        
        assert payload is not None
        assert payload["user_id"] == 1
        assert payload["email"] == "test@example.com"
        print("✓ Valid token verified successfully")
    
    def test_verify_invalid_token(self):
        """Test verifying an invalid JWT token"""
        invalid_token = "invalid.token.here"
        
        payload = verify_access_token(invalid_token)
        
        assert payload is None
        print("✓ Invalid token correctly rejected")
    
    def test_token_expiration(self):
        """Test that token expiration is set correctly"""
        user_data = {"user_id": 1, "email": "test@example.com"}
        token = create_access_token(user_data)
        
        payload = verify_access_token(token)
        
        assert "exp" in payload
        assert "iat" in payload
        
        # Verify expiration is in the future
        exp_timestamp = payload["exp"]
        assert exp_timestamp > datetime.utcnow().timestamp()
        print("✓ Token expiration set correctly")


class TestUserManagement:
    """Test user database operations"""
    
    @pytest.fixture
    def db(self):
        """Create a test database"""
        test_db = DatabaseManager("test_auth_users.db")
        yield test_db
        # Cleanup
        if os.path.exists("backend/test_auth_users.db"):
            os.remove("backend/test_auth_users.db")
    
    def test_create_user(self, db):
        """Test creating a new user"""
        user = db.create_or_update_user(
            email="newuser@example.com",
            name="New User",
            picture="http://example.com/pic.jpg",
            provider="google",
            provider_user_id="google_123"
        )
        
        assert user is not None
        assert user["email"] == "newuser@example.com"
        assert user["provider"] == "google"
        assert "id" in user
        print("✓ User created successfully")
    
    def test_update_existing_user(self, db):
        """Test updating an existing user"""
        # Create user
        user1 = db.create_or_update_user(
            email="update@example.com",
            name="Initial Name",
            picture=None,
            provider="microsoft",
            provider_user_id="ms_456"
        )
        
        # Update user (same provider + provider_user_id)
        user2 = db.create_or_update_user(
            email="updated@example.com",
            name="Updated Name",
            picture="http://example.com/new.jpg",
            provider="microsoft",
            provider_user_id="ms_456"
        )
        
        assert user1["id"] == user2["id"]  # Same user
        assert user2["email"] == "updated@example.com"
        assert user2["name"] == "Updated Name"
        print("✓ User updated successfully")
    
    def test_get_user_by_id(self, db):
        """Test retrieving user by ID"""
        created_user = db.create_or_update_user(
            email="retrieve@example.com",
            name="Retrieve User",
            picture=None,
            provider="google",
            provider_user_id="google_789"
        )
        
        retrieved_user = db.get_user_by_id(created_user["id"])
        
        assert retrieved_user is not None
        assert retrieved_user["email"] == "retrieve@example.com"
        print("✓ User retrieved by ID successfully")
    
    def test_get_user_by_email(self, db):
        """Test retrieving user by email"""
        db.create_or_update_user(
            email="email@example.com",
            name="Email User",
            picture=None,
            provider="github",
            provider_user_id="gh_999"
        )
        
        retrieved_user = db.get_user_by_email("email@example.com")
        
        assert retrieved_user is not None
        assert retrieved_user["provider"] == "github"
        print("✓ User retrieved by email successfully")
    
    def test_update_last_login(self, db):
        """Test updating last login timestamp"""
        user = db.create_or_update_user(
            email="login@example.com",
            name="Login User",
            picture=None,
            provider="google",
            provider_user_id="google_login"
        )
        
        import time
        time.sleep(1)  # Wait to see timestamp difference
        
        db.update_last_login(user["id"])
        
        # Verify it doesn't raise an error
        updated_user = db.get_user_by_id(user["id"])
        assert updated_user is not None
        print("✓ Last login updated successfully")


class TestOAuthConfiguration:
    """Test OAuth provider configuration"""
    
    def test_oauth_providers_exist(self):
        """Test that all OAuth providers are configured"""
        assert "google" in OAUTH_PROVIDERS
        assert "microsoft" in OAUTH_PROVIDERS
        assert "github" in OAUTH_PROVIDERS
        print("✓ All OAuth providers configured")
    
    def test_google_config(self):
        """Test Google OAuth configuration"""
        google_config = OAUTH_PROVIDERS["google"]
        
        assert "client_id" in google_config
        assert "client_secret" in google_config
        assert "authorize_url" in google_config
        assert "token_url" in google_config
        print("✓ Google OAuth configuration valid")
    
    def test_microsoft_config(self):
        """Test Microsoft OAuth configuration"""
        microsoft_config = OAUTH_PROVIDERS["microsoft"]
        
        assert "client_id" in microsoft_config
        assert "client_secret" in microsoft_config
        assert "authorize_url" in microsoft_config
        assert "token_url" in microsoft_config
        print("✓ Microsoft OAuth configuration valid")


class TestDatabaseLogging:
    """Test logging interactions with user_id"""
    
    @pytest.fixture
    def db(self):
        """Create a test database"""
        test_db = DatabaseManager("test_auth_logging.db")
        yield test_db
        # Cleanup
        if os.path.exists("backend/test_auth_logging.db"):
            os.remove("backend/test_auth_logging.db")
    
    def test_log_with_user_id(self, db):
        """Test logging interaction with user_id"""
        # Create a test user first
        user = db.create_or_update_user(
            email="logger@example.com",
            name="Logger User",
            picture=None,
            provider="google",
            provider_user_id="google_logger"
        )
        
        # Log an interaction with user_id
        db.log_interaction(
            action_type="test_action",
            user_input={"test": "data"},
            final_output="Test result",
            user_id=user["id"]
        )
        
        # Retrieve logs and verify user_id is included
        logs = db.get_logs(limit=1)
        assert len(logs) > 0
        assert logs[0]["user_id"] == user["id"]
        print("✓ Interaction logged with user_id")
    
    def test_log_without_user_id(self, db):
        """Test logging interaction without user_id (optional)"""
        db.log_interaction(
            action_type="test_action_no_user",
            final_output="Result without user"
        )
        
        logs = db.get_logs(limit=1)
        assert len(logs) > 0
        assert logs[0]["user_id"] is None
        print("✓ Interaction logged without user_id (optional)")


if __name__ == "__main__":
    print("\n" + "=" * 60)
    print("Running Authentication Tests")
    print("=" * 60 + "\n")
    
    # Run pytest
    pytest.main([__file__, "-v", "--tb=short"])
