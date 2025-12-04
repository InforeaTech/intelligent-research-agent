"""
Tests for Phase 4: Hybrid Mode and Request-Level Control.
"""
import sys
import os
import pytest
from unittest.mock import MagicMock, patch

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

from schemas import ProfileRequest
from agent import ResearchAgent

def test_profile_request_schema_search_mode():
    """Test validation of search_mode in ProfileRequest."""
    # Valid modes
    req = ProfileRequest(
        name="John Doe", 
        api_key="key", 
        search_mode="rag"
    )
    assert req.search_mode == "rag"
    
    req = ProfileRequest(
        name="John Doe", 
        api_key="key", 
        search_mode="TOOLS"  # Case insensitive check
    )
    assert req.search_mode == "tools"
    
    req = ProfileRequest(
        name="John Doe", 
        api_key="key", 
        search_mode="hybrid"
    )
    assert req.search_mode == "hybrid"
    
    # Invalid mode
    with pytest.raises(ValueError) as excinfo:
        ProfileRequest(
            name="John Doe", 
            api_key="key", 
            search_mode="invalid_mode"
        )
    assert "search_mode must be" in str(excinfo.value)

def test_agent_generate_profile_with_mode_return_signature():
    """Test that generate_profile_with_mode returns 4 values."""
    agent = ResearchAgent()
    
    # Mock dependencies
    agent.content_service = MagicMock()
    agent.content_service.generate_profile_with_tools.return_value = "Profile Text"
    agent.gather_info = MagicMock(return_value={"some": "data"})
    agent.generate_profile = MagicMock(return_value=("Profile Text", False, None))
    
    # Test Tools Mode
    res = agent.generate_profile_with_mode(
        name="Test", 
        search_mode="tools"
    )
    assert len(res) == 4
    assert res[0] == "Profile Text"
    assert res[1]["mode"] == "tools"
    
    # Test Hybrid Mode
    res = agent.generate_profile_with_mode(
        name="Test", 
        search_mode="hybrid"
    )
    assert len(res) == 4
    assert res[0] == "Profile Text"
    assert res[1]["mode"] == "hybrid"
    
    # Test RAG Mode
    res = agent.generate_profile_with_mode(
        name="Test", 
        search_mode="rag"
    )
    assert len(res) == 4
    assert res[0] == "Profile Text"
    assert res[1]["mode"] == "rag"

@patch('main.agent')
@patch('main.get_current_user_id')
@patch('main.secret_manager')
def test_api_endpoint_logic(mock_secrets, mock_user, mock_agent):
    """Test that API endpoint calls agent with correct search_mode."""
    from main import research_profile
    
    # Setup mocks
    mock_user.return_value = "user123"
    mock_secrets.get_secret.return_value = "secret_key"
    mock_agent.generate_profile_with_mode.return_value = ("Profile", {}, False, None)
    
    # Create request
    request = ProfileRequest(
        name="John Doe",
        api_key="key",
        search_mode="hybrid",
        model_provider="openai"
    )
    
    # Call endpoint function directly (bypassing FastAPI routing for unit test)
    # We need to mock Request object or pass None if not used
    mock_req = MagicMock()
    mock_db = MagicMock()
    
    response = research_profile(request, mock_req, db=mock_db)
    
    # Verify agent call
    mock_agent.generate_profile_with_mode.assert_called_once()
    call_args = mock_agent.generate_profile_with_mode.call_args
    assert call_args.kwargs['search_mode'] == "hybrid"
    assert call_args.kwargs['provider'] == "openai"
    assert response["profile"] == "Profile"

if __name__ == "__main__":
    # Manual run helper
    try:
        test_profile_request_schema_search_mode()
        print("✓ Schema validation passed")
        test_agent_generate_profile_with_mode_return_signature()
        print("✓ Agent return signature passed")
        print("Run with pytest for full verification")
    except Exception as e:
        print(f"❌ Error: {e}")
