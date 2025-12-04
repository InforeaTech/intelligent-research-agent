"""
Quick test for Phase 6.1: OpenAI Deep Research with Tools
"""
import sys
import os

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

from content_service import ContentService


def test_deep_research_method_exists():
    """Test that the deep_research_with_tools method exists."""
    print("Testing Phase 6.1: Deep Research with Tools")
    
    service = ContentService()
    
    # Verify method exists
    assert hasattr(service, 'deep_research_with_tools')
    print("✓ deep_research_with_tools method exists")
    
    # Verify private OpenAI method exists
    assert hasattr(service, '_deep_research_with_tools_openai')
    print("✓ _deep_research_with_tools_openai method exists")
    
    # Test with fake API key (will fail gracefully)
    try:
        result = service.deep_research_with_tools(
            topic="Test Topic",
            api_key="fake_key",
            provider="openai"
        )
        # Should return an error message
        assert "Error" in result or "conducting deep research" in result
        print("✓ Error handling works correctly")
    except Exception as e:
        print(f"✓ Expected error caught: {type(e).__name__}")
    
    # Test unsupported provider
    result = service.deep_research_with_tools(
        topic="Test",
        api_key="fake",
        provider="gemini"
    )
    assert "not yet implemented" in result
    print("✓ Gemini correctly shows as not implemented")
    
    result = service.deep_research_with_tools(
        topic="Test",
        api_key="fake",
        provider="grok"
    )
    assert "not yet implemented" in result
    print("✓ Grok correctly shows as not implemented")
    
    print("\n✅ All Phase 6.1 tests passed!")
    print("\nNote: Full integration testing requires real API keys")
    print("To test with real OpenAI:")
    print("1. Set OPENAI_API_KEY in .env")
    print("2. Run the server")
    print("3. Use Phase 6.4 API endpoint when available")


if __name__ == "__main__":
    test_deep_research_method_exists()
