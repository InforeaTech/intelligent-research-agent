"""
Tests for tool_definitions module.
Verifies that tool schemas are correctly formatted for each provider.
"""
import sys
import os

# Add backend directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

from tool_definitions import (
    get_openai_tools,
    get_gemini_tools,
    get_grok_tools,
    get_tools_for_provider,
    get_tool_names,
    get_tool_description
)


def test_openai_tools():
    """Test OpenAI tool schema format."""
    print("Testing OpenAI tool schemas...")
    tools = get_openai_tools()
    
    assert isinstance(tools, list), "Tools should be a list"
    assert len(tools) == 2, "Should have 2 tools"
    
    # Check search_web tool
    search_tool = tools[0]
    assert search_tool["type"] == "function"
    assert search_tool["function"]["name"] == "search_web"
    assert "query" in search_tool["function"]["parameters"]["properties"]
    print("✓ OpenAI search_web tool schema valid")
    
    # Check scrape_webpage tool
    scrape_tool = tools[1]
    assert scrape_tool["type"] == "function"
    assert scrape_tool["function"]["name"] == "scrape_webpage"
    assert "url" in scrape_tool["function"]["parameters"]["properties"]
    print("✓ OpenAI scrape_webpage tool schema valid")
    
    print("✓ OpenAI tools passed\n")


def test_gemini_tools():
    """Test Gemini tool schema format."""
    print("Testing Gemini tool schemas...")
    tools = get_gemini_tools()
    
    assert isinstance(tools, list), "Tools should be a list"
    assert len(tools) == 1, "Should have 1 item (function_declarations wrapper)"
    assert "function_declarations" in tools[0]
    
    functions = tools[0]["function_declarations"]
    assert len(functions) == 2, "Should have 2 function declarations"
    
    # Check search_web tool
    search_func = functions[0]
    assert search_func["name"] == "search_web"
    assert "query" in search_func["parameters"]["properties"]
    print("✓ Gemini search_web tool schema valid")
    
    # Check scrape_webpage tool
    scrape_func = functions[1]
    assert scrape_func["name"] == "scrape_webpage"
    assert "url" in scrape_func["parameters"]["properties"]
    print("✓ Gemini scrape_webpage tool schema valid")
    
    print("✓ Gemini tools passed\n")


def test_grok_tools():
    """Test Grok tool schema format."""
    print("Testing Grok tool schemas...")
    tools = get_grok_tools()
    
    # Grok uses OpenAI format
    assert isinstance(tools, list), "Tools should be a list"
    assert len(tools) == 2, "Should have 2 tools"
    assert tools[0]["type"] == "function"
    assert tools[0]["function"]["name"] == "search_web"
    print("✓ Grok uses OpenAI-compatible format")
    print("✓ Grok tools passed\n")


def test_get_tools_for_provider():
    """Test provider-specific tool retrieval."""
    print("Testing get_tools_for_provider...")
    
    # Test each provider
    openai_tools = get_tools_for_provider("openai")
    assert len(openai_tools) == 2
    print("✓ Retrieved OpenAI tools")
    
    gemini_tools = get_tools_for_provider("gemini")
    assert "function_declarations" in gemini_tools[0]
    print("✓ Retrieved Gemini tools")
    
    grok_tools = get_tools_for_provider("grok")
    assert len(grok_tools) == 2
    print("✓ Retrieved Grok tools")
    
    # Test case insensitivity
    tools = get_tools_for_provider("OpenAI")
    assert len(tools) == 2
    print("✓ Case-insensitive provider names")
    
    # Test invalid provider
    try:
        get_tools_for_provider("invalid")
        assert False, "Should have raised ValueError"
    except ValueError as e:
        assert "Unsupported provider" in str(e)
        print("✓ Rejects invalid providers")
    
    print("✓ get_tools_for_provider passed\n")


def test_utility_functions():
    """Test utility functions."""
    print("Testing utility functions...")
    
    # Test get_tool_names
    names = get_tool_names()
    assert names == ["search_web", "scrape_webpage"]
    print("✓ get_tool_names returns correct list")
    
    # Test get_tool_description
    desc = get_tool_description("search_web")
    assert "search" in desc.lower()
    print("✓ get_tool_description for search_web")
    
    desc = get_tool_description("scrape_webpage")
    assert "webpage" in desc.lower()
    print("✓ get_tool_description for scrape_webpage")
    
    # Test invalid tool
    try:
        get_tool_description("invalid_tool")
        assert False, "Should have raised ValueError"
    except ValueError:
        print("✓ Rejects invalid tool names")
    
    print("✓ Utility functions passed\n")


def test_tool_schema_completeness():
    """Test that tool schemas have all required fields."""
    print("Testing tool schema completeness...")
    
    tools = get_openai_tools()
    
    for tool in tools:
        # Check required fields
        assert "type" in tool
        assert "function" in tool
        assert "name" in tool["function"]
        assert "description" in tool["function"]
        assert "parameters" in tool["function"]
        assert "properties" in tool["function"]["parameters"]
        assert "required" in tool["function"]["parameters"]
        
        print(f"  ✓ {tool['function']['name']} has all required fields")
    
    print("✓ Schema completeness passed\n")


def main():
    """Run all tests."""
    print("=" * 60)
    print("Testing Tool Definitions")
    print("=" * 60 + "\n")
    
    try:
        test_openai_tools()
        test_gemini_tools()
        test_grok_tools()
        test_get_tools_for_provider()
        test_utility_functions()
        test_tool_schema_completeness()
        
        print("=" * 60)
        print("✅ All tests PASSED")
        print("=" * 60)
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
