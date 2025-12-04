"""
Test for Phase 6.3: Agent Integration (Mode Routing)
"""
import sys
import os
from unittest.mock import MagicMock, patch

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

from agent import ResearchAgent
from config import settings

def test_deep_research_with_mode_exists():
    """Test that deep_research_with_mode method exists."""
    print("Testing Phase 6.3: Agent Integration")
    
    agent = ResearchAgent()
    
    # Verify method exists
    assert hasattr(agent, 'deep_research_with_mode')
    print("✓ deep_research_with_mode method exists")

@patch('agent.ResearchAgent.perform_deep_research')
@patch('content_service.ContentService.deep_research_with_tools')
def test_mode_routing(mock_tools, mock_rag):
    """Test that the router calls the correct methods based on mode."""
    print("\nTesting Mode Routing:")
    
    agent = ResearchAgent()
    
    # Mock return values
    mock_rag.return_value = "RAG Report"
    mock_tools.return_value = "Tools Report"
    
    # Test RAG mode
    agent.deep_research_with_mode(
        topic="Test RAG",
        api_key="key",
        search_mode="rag"
    )
    mock_rag.assert_called()
    print("✓ RAG mode calls perform_deep_research")
    
    # Reset mocks
    mock_rag.reset_mock()
    mock_tools.reset_mock()
    
    # Test Tools mode
    agent.deep_research_with_mode(
        topic="Test Tools",
        api_key="key",
        search_mode="tools"
    )
    mock_tools.assert_called()
    print("✓ Tools mode calls deep_research_with_tools")
    
    # Reset mocks
    mock_rag.reset_mock()
    mock_tools.reset_mock()
    
    # Test Hybrid mode
    agent.deep_research_with_mode(
        topic="Test Hybrid",
        api_key="key",
        search_mode="hybrid"
    )
    mock_rag.assert_called()  # Should call RAG first
    mock_tools.assert_called()  # Then call Tools
    print("✓ Hybrid mode calls both RAG and Tools methods")
    
    print("\n✅ All Phase 6.3 tests passed!")

if __name__ == "__main__":
    test_deep_research_with_mode_exists()
    test_mode_routing()
