"""
Integration Test for Phase 6: Deep Research Function Calling
Tests the full flow from Agent to ContentService with mocked API calls.
"""
import sys
import os
import pytest
from unittest.mock import MagicMock, patch

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

from agent import ResearchAgent
from content_service import ContentService
from schemas import DeepResearchRequest

@pytest.fixture
def agent():
    agent = ResearchAgent()
    # Mock the content service methods directly on the instance
    agent.content_service.deep_research_with_tools = MagicMock(return_value="Tools Research Report")
    agent.content_service.plan_research = MagicMock(return_value=(["query1"], "prompt", "plan"))
    agent.content_service.synthesize_report = MagicMock(return_value=("RAG Research Report", "prompt"))
    return agent

def test_deep_research_rag_mode(agent):
    """Test standard RAG mode (backward compatibility)."""
    print("\nTesting RAG Mode...")
    
    # Mock search service to avoid real calls
    with patch.object(agent.search_service, 'search_web', return_value=[{'href': 'http://test.com', 'body': 'content'}]), \
         patch.object(agent.search_service, 'scrape_webpage', return_value={'success': True, 'content': 'scraped content', 'url': 'http://test.com'}):
        
        result = agent.deep_research_with_mode(
            topic="Test Topic",
            api_key="fake_key",
            search_mode="rag"
        )
        
        assert "RAG Research Report" in result
        # Should NOT call deep_research_with_tools
        agent.content_service.deep_research_with_tools.assert_not_called()
        print("✓ RAG mode successful")

def test_deep_research_tools_mode(agent):
    """Test new Tools mode."""
    print("\nTesting Tools Mode...")
    
    result = agent.deep_research_with_mode(
        topic="Test Topic",
        api_key="fake_key",
        search_mode="tools",
        provider="openai"
    )
    
    assert result == "Tools Research Report"
    agent.content_service.deep_research_with_tools.assert_called_once()
    
    # Verify arguments
    call_args = agent.content_service.deep_research_with_tools.call_args
    assert call_args.kwargs['topic'] == "Test Topic"
    assert call_args.kwargs['provider'] == "openai"
    print("✓ Tools mode successful")

def test_deep_research_hybrid_mode(agent):
    """Test Hybrid mode (RAG + Tools)."""
    print("\nTesting Hybrid Mode...")
    
    # Mock search service
    with patch.object(agent.search_service, 'search_web', return_value=[{'href': 'http://test.com', 'body': 'content'}]), \
         patch.object(agent.search_service, 'scrape_webpage', return_value={'success': True, 'content': 'scraped content', 'url': 'http://test.com'}):
        
        result = agent.deep_research_with_mode(
            topic="Test Topic",
            api_key="fake_key",
            search_mode="hybrid",
            provider="gemini"
        )
        
        # Should return the result from tools (step 2)
        assert result == "Tools Research Report"
        
        # Should have called tools with enhanced context
        agent.content_service.deep_research_with_tools.assert_called_once()
        call_args = agent.content_service.deep_research_with_tools.call_args
        assert "Initial Research Context" in call_args.kwargs['topic']
        assert "RAG Research Report" in call_args.kwargs['topic']
        assert call_args.kwargs['provider'] == "gemini"
        print("✓ Hybrid mode successful")

def test_provider_routing(agent):
    """Test that provider is passed correctly."""
    print("\nTesting Provider Routing...")
    
    providers = ["openai", "gemini", "grok"]
    
    for provider in providers:
        agent.deep_research_with_mode(
            topic="Test",
            api_key="key",
            search_mode="tools",
            provider=provider
        )
        
        # Check last call
        call_args = agent.content_service.deep_research_with_tools.call_args
        assert call_args.kwargs['provider'] == provider
        print(f"✓ Provider '{provider}' routed correctly")
        
        agent.content_service.deep_research_with_tools.reset_mock()

if __name__ == "__main__":
    # Manual run wrapper
    pytest.main([__file__, "-v"])
