"""
Tests for Phase 3: Gemini and Grok Function Calling.
"""
import sys
import os
import pytest
from unittest.mock import MagicMock, patch, PropertyMock

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

from content_service import ContentService
from tool_definitions import get_tools_for_provider


def test_gemini_tool_format():
    """Test that Gemini tools are correctly formatted."""
    tools = get_tools_for_provider("gemini")
    assert len(tools) == 1
    assert "function_declarations" in tools[0]
    funcs = tools[0]["function_declarations"]
    assert len(funcs) == 2
    assert funcs[0]["name"] == "search_web"
    assert funcs[1]["name"] == "scrape_webpage"


def test_grok_tool_format():
    """Test that Grok tools are correctly formatted (OpenAI compatible)."""
    tools = get_tools_for_provider("grok")
    assert len(tools) == 2
    assert tools[0]["type"] == "function"
    assert tools[0]["function"]["name"] == "search_web"


@patch('content_service.genai')
def test_gemini_function_calling_flow(mock_genai):
    """Test the Gemini function calling flow with mocks."""
    # Setup mock
    mock_model = MagicMock()
    mock_chat = MagicMock()
    mock_genai.GenerativeModel.return_value = mock_model
    mock_model.start_chat.return_value = mock_chat
    
    # Mock responses
    # 1. Initial response with function call
    mock_part_call = MagicMock()
    mock_function_call = MagicMock()
    mock_function_call.name = "search_web"
    # Make args behave like a dict
    mock_function_call.args = {"query": "test query"}
    
    # Configure part.function_call to return our mock function call
    # We need to set it as a property value, not a method
    type(mock_part_call).function_call = PropertyMock(return_value=mock_function_call)
    
    mock_response_call = MagicMock()
    mock_response_call.parts = [mock_part_call]
    
    # 2. Final response with text
    mock_part_final = MagicMock()
    mock_part_final.text = "Final profile text"
    # Ensure function_call is None/Falsey
    type(mock_part_final).function_call = PropertyMock(return_value=None)
    
    mock_response_final = MagicMock()
    mock_response_final.parts = [mock_part_final]
    mock_response_final.text = "Final profile text"
    
    # Configure chat.send_message to return sequence of responses
    mock_chat.send_message.side_effect = [mock_response_call, mock_response_final]
    
    # Test execution
    service = ContentService()
    
    # Mock ToolExecutor to avoid actual execution
    with patch('content_service.ToolExecutor') as MockExecutor:
        mock_executor = MockExecutor.return_value
        mock_executor.execute_tool.return_value = "Search results"
        
        result = service._generate_profile_with_tools_gemini(
            name="Test User",
            company="Test Co",
            additional_info="",
            api_key="fake_key",
            serper_api_key=None,
            max_iterations=5
        )
        
        # Verify
        assert result == "Final profile text"
        assert mock_chat.send_message.call_count == 2
        mock_executor.execute_tool.assert_called_with("search_web", {"query": "test query"})


@patch('content_service.OpenAI')
def test_grok_function_calling_flow(mock_openai):
    """Test the Grok function calling flow with mocks."""
    # Setup mock client
    mock_client = MagicMock()
    mock_openai.return_value = mock_client
    
    # Mock responses
    # 1. Response with tool call
    mock_message_call = MagicMock()
    mock_message_call.tool_calls = [
        MagicMock(
            id="call_123",
            function=MagicMock(
                name="search_web",
                arguments='{"query": "test query"}'
            )
        )
    ]
    mock_message_call.content = None
    
    # 2. Final response
    mock_message_final = MagicMock()
    mock_message_final.tool_calls = None
    mock_message_final.content = "Final Grok profile"
    
    # Configure completions.create to return sequence
    mock_response_1 = MagicMock()
    mock_response_1.choices = [MagicMock(message=mock_message_call)]
    
    mock_response_2 = MagicMock()
    mock_response_2.choices = [MagicMock(message=mock_message_final)]
    
    mock_client.chat.completions.create.side_effect = [mock_response_1, mock_response_2]
    
    # Test execution
    service = ContentService()
    
    with patch('content_service.ToolExecutor') as MockExecutor:
        mock_executor = MockExecutor.return_value
        mock_executor.execute_tool.return_value = "Search results"
        mock_executor.format_tool_result_for_llm.return_value = "Formatted results"
        
        result = service._generate_profile_with_tools_grok(
            name="Test User",
            company="Test Co",
            additional_info="",
            api_key="fake_key",
            serper_api_key=None,
            max_iterations=5
        )
        
        # Verify
        assert result == "Final Grok profile"
        assert mock_client.chat.completions.create.call_count == 2
        # Verify correct model was used
        call_args = mock_client.chat.completions.create.call_args_list[0]
        assert call_args.kwargs['model'] == "grok-4-1-fast"


def test_routing():
    """Test that generate_profile_with_tools routes correctly."""
    service = ContentService()
    
    with patch.object(service, '_generate_profile_with_tools_openai') as mock_openai, \
         patch.object(service, '_generate_profile_with_tools_gemini') as mock_gemini, \
         patch.object(service, '_generate_profile_with_tools_grok') as mock_grok:
        
        # Test OpenAI routing
        service.generate_profile_with_tools("Name", "Co", "", "key", "openai")
        mock_openai.assert_called_once()
        
        # Test Gemini routing
        service.generate_profile_with_tools("Name", "Co", "", "key", "gemini")
        mock_gemini.assert_called_once()
        
        # Test Grok routing
        service.generate_profile_with_tools("Name", "Co", "", "key", "grok")
        mock_grok.assert_called_once()


def main():
    """Run tests manually."""
    print("=" * 60)
    print("Testing Phase 3: Gemini and Grok Function Calling")
    print("=" * 60 + "\n")
    
    try:
        test_gemini_tool_format()
        print("✓ Gemini tool format valid")
        
        test_grok_tool_format()
        print("✓ Grok tool format valid")
        
        # Run mocked tests
        # We need to run these with pytest or manually invoke them
        # Since we're in a script, we'll invoke them manually but we need to handle the decorators
        # It's easier to just run this file with pytest
        print("Please run this file with pytest for full verification:")
        print("pytest test_phase3.py")
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    # If run directly, just check formats. For full mock tests, use pytest.
    main()
