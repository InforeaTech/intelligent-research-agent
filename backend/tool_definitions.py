"""
Tool definitions for function calling across different LLM providers.

Provides standardized tool schemas for:
- OpenAI (GPT-4o)
- Google Gemini
- xAI Grok

Available tools:
- search_web: Perform web search using DuckDuckGo or Serper
- scrape_webpage: Extract content from a URL
"""

from typing import Dict, List, Any


def get_openai_tools() -> List[Dict[str, Any]]:
    """
    Get tool definitions in OpenAI function calling format.
    
    Returns:
        List of tool schemas compatible with OpenAI API
    """
    return [
        {
            "type": "function",
            "function": {
                "name": "search_web",
                "description": "Perform a web search to find information. Use this when you need to search for information about a person, company, or topic.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "query": {
                            "type": "string",
                            "description": "The search query string. Be specific and include relevant keywords."
                        },
                        "max_results": {
                            "type": "integer",
                            "description": "Maximum number of search results to return (default: 10, max: 20)",
                            "default": 10
                        }
                    },
                    "required": ["query"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "scrape_webpage",
                "description": "Extract and read the main content from a specific webpage URL. Use this to get detailed information from a specific page.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "url": {
                            "type": "string",
                            "description": "The full URL of the webpage to scrape"
                        },
                        "max_chars": {
                            "type": "integer",
                            "description": "Maximum characters to extract from the page (default: 5000)",
                            "default": 5000
                        }
                    },
                    "required": ["url"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "get_user_research_history",
                "description": "Search and retrieve the user's past research profiles and notes. Use this to find information the user has already researched.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "query": {
                            "type": "string",
                            "description": "Optional search query to filter history (e.g., person name, company, topic)."
                        },
                        "limit": {
                            "type": "integer",
                            "description": "Maximum number of history items to return (default: 5)",
                            "default": 5
                        }
                    },
                    "required": []
                }
            }
        }
    ]


def get_gemini_tools() -> List[Dict[str, Any]]:
    """
    Get tool definitions in Google Gemini function calling format.
    
    Returns:
        List of tool schemas compatible with Gemini API
    """
    return [
        {
            "function_declarations": [
                {
                    "name": "search_web",
                    "description": "Perform a web search to find information. Use this when you need to search for information about a person, company, or topic.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "query": {
                                "type": "string",
                                "description": "The search query string. Be specific and include relevant keywords."
                            },
                            "max_results": {
                                "type": "integer",
                                "description": "Maximum number of search results to return (default: 10, max: 20)"
                            }
                        },
                        "required": ["query"]
                    }
                },
                {
                    "name": "scrape_webpage",
                    "description": "Extract and read the main content from a specific webpage URL. Use this to get detailed information from a specific page.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "url": {
                                "type": "string",
                                "description": "The full URL of the webpage to scrape"
                            },
                            "max_chars": {
                                "type": "integer",
                                "description": "Maximum characters to extract from the page (default: 5000)"
                            }
                        },
                        "required": ["url"]
                    }
                },
                {
                    "name": "get_user_research_history",
                    "description": "Search and retrieve the user's past research profiles and notes. Use this to find information the user has already researched.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "query": {
                                "type": "string",
                                "description": "Optional search query to filter history (e.g., person name, company, topic)."
                            },
                            "limit": {
                                "type": "integer",
                                "description": "Maximum number of history items to return (default: 5)"
                            }
                        },
                        "required": []
                    }
                }
            ]
        }
    ]


def get_grok_tools() -> List[Dict[str, Any]]:
    """
    Get tool definitions in Grok (xAI) function calling format.
    
    Grok uses OpenAI-compatible API, so this returns the same format as OpenAI.
    
    Returns:
        List of tool schemas compatible with Grok API
    """
    return get_openai_tools()  # Grok uses OpenAI-compatible format


def get_tools_for_provider(provider: str) -> List[Dict[str, Any]]:
    """
    Get tool definitions for a specific provider.
    
    Args:
        provider: LLM provider name ('openai', 'gemini', 'grok')
        
    Returns:
        List of tool schemas for the provider
        
    Raises:
        ValueError: If provider is not supported
    """
    provider = provider.lower()
    
    if provider == "openai":
        return get_openai_tools()
    elif provider == "gemini":
        return get_gemini_tools()
    elif provider == "grok":
        return get_grok_tools()
    else:
        raise ValueError(f"Unsupported provider: {provider}. Must be 'openai', 'gemini', or 'grok'.")


def get_tool_names() -> List[str]:
    """
    Get list of available tool names.
    
    Returns:
        List of tool function names
    """
    return ["search_web", "scrape_webpage", "get_user_research_history"]


def get_tool_description(tool_name: str) -> str:
    """
    Get human-readable description of a tool.
    
    Args:
        tool_name: Name of the tool
        
    Returns:
        Description string
        
    Raises:
        ValueError: If tool_name is not recognized
    """
    descriptions = {
        "search_web": "Perform web search using DuckDuckGo or Serper",
        "scrape_webpage": "Extract main content from a webpage URL",
        "get_user_research_history": "Retrieve past research profiles and notes"
    }
    
    if tool_name not in descriptions:
        raise ValueError(f"Unknown tool: {tool_name}")
    
    return descriptions[tool_name]
