"""
Test for History Recording (Phase 1).
Verifies that profiles and notes are saved to the database.
"""
import sys
import os
import pytest
from unittest.mock import MagicMock, patch
from datetime import datetime

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

from main import research_profile, generate_note, get_db_session
from schemas import ProfileRequest, NoteRequest
from models.profile import Profile
from models.note import Note

# Mock dependencies
@pytest.fixture
def mock_db():
    return MagicMock()

@pytest.fixture
def mock_request():
    req = MagicMock()
    req.cookies.get.return_value = "fake_token"
    return req

@patch('main.get_current_user_id')
@patch('main.secret_manager')
@patch('main.agent')
@patch('main.ProfileRepository')
@patch('main.NoteRepository')
@patch('main.LogRepository')
def test_research_profile_saves_to_db(
    mock_log_repo, mock_note_repo, mock_profile_repo, 
    mock_agent, mock_secrets, mock_get_user_id, 
    mock_db, mock_request
):
    """Test that research_profile endpoint saves profile to DB."""
    
    # Setup mocks
    mock_get_user_id.return_value = 123
    mock_secrets.get_secret.return_value = "fake_key"
    
    # Mock agent response
    mock_agent.generate_profile_with_mode.return_value = (
        "Generated Profile Content", 
        {"some": "data"}, 
        False, 
        None
    )
    
    # Mock repository
    mock_profile_instance = MagicMock()
    mock_profile_instance.create.return_value = Profile(id=1, user_id=123, name="Test Name")
    mock_profile_repo.return_value = mock_profile_instance
    
    # Mock LogRepository to avoid errors
    mock_log_instance = MagicMock()
    mock_log_instance.check_cache.return_value = None
    mock_log_repo.return_value = mock_log_instance

    # Create request
    request = ProfileRequest(
        name="Test Name",
        company="Test Company",
        model_provider="openai",
        search_mode="rag",
        api_key="fake_key"
    )
    
    # Call endpoint
    response = research_profile(request, mock_request, db=mock_db)
    
    # Verify ProfileRepository was initialized
    mock_profile_repo.assert_called_once_with(mock_db)
    
    # Verify create was called with correct data
    mock_profile_instance.create.assert_called_once()
    call_args = mock_profile_instance.create.call_args
    assert call_args.kwargs['user_id'] == 123
    assert call_args.kwargs['name'] == "Test Name"
    assert call_args.kwargs['company'] == "Test Company"
    assert call_args.kwargs['profile_text'] == "Generated Profile Content"
    
    # Verify response contains profile_id
    assert "id" in response
    assert response["id"] == 1
    print("✓ research_profile saves to DB and returns ID")

@patch('main.get_current_user_id')
@patch('main.secret_manager')
@patch('main.agent')
@patch('main.NoteRepository')
def test_generate_note_saves_to_db(
    mock_note_repo, mock_agent, mock_secrets, mock_get_user_id, 
    mock_db, mock_request
):
    """Test that generate_note endpoint saves note to DB."""
    
    # Setup mocks
    mock_get_user_id.return_value = 123
    mock_secrets.get_secret.return_value = "fake_key"
    
    # Mock agent response
    mock_agent.generate_note.return_value = ("Generated Note Content", False)
    
    # Mock repository
    mock_note_instance = MagicMock()
    mock_note_instance.create.return_value = Note(id=1, user_id=123, profile_id=456)
    mock_note_repo.return_value = mock_note_instance
    
    # Create request
    request = NoteRequest(
        profile_text="Profile Context",
        length=100,
        tone="professional",
        model_provider="openai",
        profile_id=456,  # Existing profile ID
        api_key="fake_key"
    )
    
    # Call endpoint
    response = generate_note(request, mock_request, db=mock_db)
    
    # Verify NoteRepository was initialized
    mock_note_repo.assert_called_once_with(mock_db)
    
    # Verify create was called with correct data
    mock_note_instance.create.assert_called_once()
    call_args = mock_note_instance.create.call_args
    assert call_args.kwargs['user_id'] == 123
    assert call_args.kwargs['profile_id'] == 456
    assert call_args.kwargs['note_content'] == "Generated Note Content"
    
    # Verify response contains note_id (if we decide to return it, currently schema might not have it)
    # For now just checking it runs without error and calls save
    print("✓ generate_note saves to DB")

if __name__ == "__main__":
    # Manual run wrapper
    try:
        # We can't easily run these manually without pytest due to mocks
        print("Run this file with pytest: pytest test_history_recording.py")
    except Exception as e:
        print(f"Error: {e}")
