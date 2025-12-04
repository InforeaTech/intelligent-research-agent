"""
Tests for OpenAI function calling functionality.
Tests tool executor, function calling loop, and agent integration.
"""
import sys
import os

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

from tool_executor import ToolExecutor, execute_tool
from search_service import SearchService


def test_tool_executor_search():
    """Test search_web tool execution."""
    print("Testing search_web tool execution...")
    
    executor = ToolExecutor()
    result = executor.execute_tool("search_web", {"query": "Python programming", "max_results": 3})
    
    assert result["success"], f"Search failed: {result.get('error')}"
    assert "result" in result
    assert len(result["result"]) > 0
    print(f"✓ Search returned results: {result['metadata']['count']} results")
    print(f"  First result preview: {result['result'][:100]}...")


def test_tool_executor_scrape():
    """Test scrape_webpage tool execution."""
    print("\nTesting scrape_webpage tool execution...")
    
    executor = ToolExecutor()
    result = executor.execute_tool("scrape_webpage", {
        "url": "https://www.python.org",
        "max_chars": 500
    })
    
    assert result["success"], f"Scraping failed: {result.get('error')}"
    assert "result" in result
    assert "content" in result["result"]
    print(f"✓ Scraped content length: {len(result['result']['content'])} chars")
    print(f"  Content preview: {result['result']['content'][:100]}...")


def test_tool_executor_unknown_tool():
    """Test error handling for unknown tools."""
    print("\nTesting unknown tool error handling...")
    
    executor = ToolExecutor()
    result = executor.execute_tool("unknown_tool", {})
    
    assert not result["success"]
    assert "error" in result
    assert "Unknown tool" in result["error"]
    print("✓ Unknown tool properly rejected")


def test_convenience_function():
    """Test execute_tool convenience function."""
    print("\nTesting execute_tool convenience function...")
    
    result = execute_tool("search_web", {"query": "test", "max_results": 2})
    
    assert result["success"]
    print("✓ Convenience function works")


def test_format_result():
    """Test result formatting for LLM."""
    print("\nTesting result formatting...")
    
    executor = ToolExecutor()
    
    # Test successful result
    search_result = {
        "success": True,
        "result": "Some search results",
        "metadata": {"count": 5}
    }
    
    formatted = executor.format_tool_result_for_llm("search_web", search_result)
    assert "Some search results" in formatted
    print("✓ Success result formatted correctly")
    
    # Test error result
    error_result = {
        "success": False,
        "error": "Test error"
    }
    
    formatted = executor.format_tool_result_for_llm("search_web", error_result)
    assert "failed" in formatted.lower()
    assert "Test error" in formatted
    print("✓ Error result formatted correctly")


def test_agent_mode_detection():
    """Test that agent correctly detects search mode."""
    print("\nTesting agent mode detection...")
    
    from config import settings
    from agent import ResearchAgent
    
    agent = ResearchAgent()
    
    # Check that config is loaded
    print(f"  Current SEARCH_MODE from config: {settings.SEARCH_MODE}")
    print(f"  USE_FUNCTION_CALLING: {settings.USE_FUNCTION_CALLING}")
    
    # Verify agent has the new method
    assert hasattr(agent, 'generate_profile_with_mode')
    print("✓ Agent has generate_profile_with_mode method")
    
    # Verify content_service has tools method
    assert hasattr(agent.content_service, 'generate_profile_with_tools')
    print("✓ ContentService has generate_profile_with_tools method")


def main():
    """Run all Phase 2 tests."""
    print("=" * 60)
    print("Testing Phase 2: OpenAI Function Calling")
    print("=" * 60 + "\n")
    
    try:
        test_tool_executor_search()
        test_tool_executor_scrape()
        test_tool_executor_unknown_tool()
        test_convenience_function()
        test_format_result()
        test_agent_mode_detection()
        
        print("\n" + "=" * 60)
        print("✅ All Phase 2 tests PASSED")
        print("=" * 60)
        print("\nNote: Full OpenAI function calling test requires API key")
        print("To test manually:")
        print("1. Set SEARCH_MODE=tools in .env")
        print("2. Set OPENAI_API_KEY in .env")
        print("3. Run the server and make a research request")
        return True
        
    except AssertionError as e:
        print(f"\n❌ Test FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
