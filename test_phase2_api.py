"""
Phase 2: API Endpoint Testing
Tests for history recording API endpoints.
"""
import sys
import os
import pytest
from unittest.mock import MagicMock, patch
from datetime import datetime

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

from main import (
    get_user_profiles, 
    search_profiles, 
    get_profile, 
    delete_profile,
    get_recent_profiles,
    get_db_session
)
from models.profile import Profile
from models.note import Note


# Mock dependencies
@pytest.fixture
def mock_db():
    return MagicMock()


@pytest.fixture
def mock_request():
    """Mock request with authenticated user."""
    req = MagicMock()
    req.cookies.get.return_value = "fake_token"
    return req


@pytest.fixture
def mock_request_unauthenticated():
    """Mock request without authentication."""
    req = MagicMock()
    req.cookies.get.return_value = None
    return req


@patch('main.get_current_user_id')
@patch('main.ProfileRepository')
def test_get_user_profiles_success(mock_profile_repo, mock_get_user_id, mock_db, mock_request):
    """Test GET /api/profiles returns paginated profiles."""
    
    # Setup mocks
    mock_get_user_id.return_value = 123
    
    # Mock repository
    mock_repo_instance = MagicMock()
    mock_repo_instance.get_by_user.return_value = [
        Profile(id=1, user_id=123, name="John Doe", company="Acme Inc"),
        Profile(id=2, user_id=123, name="Jane Smith", company="Tech Co")
    ]
    mock_repo_instance.count_by_user.return_value = 2
    mock_profile_repo.return_value = mock_repo_instance
    
    # Call endpoint
    response = get_user_profiles(skip=0, limit=20, sort="recent", req=mock_request, db=mock_db)
    
    # Verify
    assert "profiles" in response
    assert "total" in response
    assert response["total"] == 2
    assert len(response["profiles"]) == 2
    assert response["skip"] == 0
    assert response["limit"] == 20
    
    mock_repo_instance.get_by_user.assert_called_once_with(123, 0, 20, "recent")
    mock_repo_instance.count_by_user.assert_called_once_with(123)
    print("✓ GET /api/profiles returns paginated profiles")


@patch('main.get_current_user_id')
def test_get_user_profiles_unauthenticated(mock_get_user_id, mock_db, mock_request_unauthenticated):
    """Test GET /api/profiles requires authentication."""
    
    mock_get_user_id.return_value = None
    
    with pytest.raises(Exception) as exc_info:
        get_user_profiles(skip=0, limit=20, req=mock_request_unauthenticated, db=mock_db)
    
    assert "Authentication required" in str(exc_info.value)
    print("✓ GET /api/profiles requires authentication")


@patch('main.get_current_user_id')
@patch('main.ProfileRepository')
def test_search_profiles_success(mock_profile_repo, mock_get_user_id, mock_db, mock_request):
    """Test GET /api/profiles/search finds matching profiles."""
    
    mock_get_user_id.return_value = 123
    
    mock_repo_instance = MagicMock()
    mock_repo_instance.search.return_value = [
        Profile(id=1, user_id=123, name="John Doe", company="Acme Inc")
    ]
    mock_profile_repo.return_value = mock_repo_instance
    
    response = search_profiles(q="John", skip=0, limit=20, req=mock_request, db=mock_db)
    
    assert "results" in response
    assert "query" in response
    assert response["query"] == "John"
    assert response["count"] == 1
    assert len(response["results"]) == 1
    
    mock_repo_instance.search.assert_called_once_with(123, "John", 0, 20)
    print("✓ GET /api/profiles/search finds matching profiles")


@patch('main.get_current_user_id')
def test_search_profiles_invalid_query(mock_get_user_id, mock_db, mock_request):
    """Test search rejects queries shorter than 2 characters."""
    
    mock_get_user_id.return_value = 123
    
    with pytest.raises(Exception) as exc_info:
        search_profiles(q="a", skip=0, limit=20, req=mock_request, db=mock_db)
    
    assert "at least 2 characters" in str(exc_info.value)
    print("✓ Search validates query length")


@patch('main.get_current_user_id')
@patch('main.ProfileRepository')
def test_get_profile_success(mock_profile_repo, mock_get_user_id, mock_db, mock_request):
    """Test GET /api/profiles/{id} returns profile with notes."""
    
    mock_get_user_id.return_value = 123
    
    # Create mock profile with notes
    mock_profile = Profile(id=1, user_id=123, name="John Doe", company="Acme Inc")
    mock_profile.notes = [
        Note(id=1, profile_id=1, user_id=123, note_text="Test note")
    ]
    
    mock_repo_instance = MagicMock()
    mock_repo_instance.get_with_notes.return_value = mock_profile
    mock_profile_repo.return_value = mock_repo_instance
    
    response = get_profile(profile_id=1, req=mock_request, db=mock_db)
    
    assert response.id == 1
    assert response.name == "John Doe"
    assert len(response.notes) == 1
    
    mock_repo_instance.get_with_notes.assert_called_once_with(1, 123)
    print("✓ GET /api/profiles/{id} returns profile with notes")


@patch('main.get_current_user_id')
@patch('main.ProfileRepository')
def test_get_profile_not_found(mock_profile_repo, mock_get_user_id, mock_db, mock_request):
    """Test GET /api/profiles/{id} returns 404 for missing profile."""
    
    mock_get_user_id.return_value = 123
    
    mock_repo_instance = MagicMock()
    mock_repo_instance.get_with_notes.return_value = None
    mock_profile_repo.return_value = mock_repo_instance
    
    with pytest.raises(Exception) as exc_info:
        get_profile(profile_id=999, req=mock_request, db=mock_db)
    
    assert "not found" in str(exc_info.value).lower()
    print("✓ GET /api/profiles/{id} returns 404 for missing profile")


@patch('main.get_current_user_id')
@patch('main.ProfileRepository')
def test_delete_profile_success(mock_profile_repo, mock_get_user_id, mock_db, mock_request):
    """Test DELETE /api/profiles/{id} removes profile."""
    
    mock_get_user_id.return_value = 123
    
    mock_repo_instance = MagicMock()
    mock_repo_instance.delete_by_user.return_value = True
    mock_profile_repo.return_value = mock_repo_instance
    
    response = delete_profile(profile_id=1, req=mock_request, db=mock_db)
    
    assert response["status"] == "success"
    assert "deleted" in response["message"].lower()
    
    mock_repo_instance.delete_by_user.assert_called_once_with(1, 123)
    print("✓ DELETE /api/profiles/{id} removes profile")


@patch('main.get_current_user_id')
@patch('main.ProfileRepository')
def test_delete_profile_not_found(mock_profile_repo, mock_get_user_id, mock_db, mock_request):
    """Test DELETE /api/profiles/{id} returns 404 for missing profile."""
    
    mock_get_user_id.return_value = 123
    
    mock_repo_instance = MagicMock()
    mock_repo_instance.delete_by_user.return_value = False
    mock_profile_repo.return_value = mock_repo_instance
    
    with pytest.raises(Exception) as exc_info:
        delete_profile(profile_id=999, req=mock_request, db=mock_db)
    
    assert "not found" in str(exc_info.value).lower() or "unauthorized" in str(exc_info.value).lower()
    print("✓ DELETE /api/profiles/{id} returns 404 for missing profile")


@patch('main.get_current_user_id')
@patch('main.ProfileRepository')
def test_get_recent_profiles(mock_profile_repo, mock_get_user_id, mock_db, mock_request):
    """Test GET /api/profiles/recent/{limit} returns recent profiles."""
    
    mock_get_user_id.return_value = 123
    
    mock_repo_instance = MagicMock()
    mock_repo_instance.get_recent_by_user.return_value = [
        Profile(id=3, user_id=123, name="Recent User", company="New Co"),
        Profile(id=2, user_id=123, name="John Doe", company="Acme Inc")
    ]
    mock_profile_repo.return_value = mock_repo_instance
    
    response = get_recent_profiles(limit=5, req=mock_request, db=mock_db)
    
    assert "profiles" in response
    assert len(response["profiles"]) == 2
    
    mock_repo_instance.get_recent_by_user.assert_called_once_with(123, 5)
    print("✓ GET /api/profiles/recent/{limit} returns recent profiles")


if __name__ == "__main__":
    # Manual run wrapper
    try:
        print("Run this file with pytest: pytest test_phase2_api.py")
    except Exception as e:
        print(f"Error: {e}")
