"""
Tool executor for LLM function calling.

Executes tools requested by LLMs and returns results in a format they can understand.
"""

import json
from typing import Dict, Any, Optional
from search_service import SearchService
from logger_config import get_logger

logger = get_logger(__name__)


class ToolExecutor:
    """Executes tools requested by LLMs during function calling."""
    
    def __init__(self, search_service: Optional[SearchService] = None, serper_api_key: Optional[str] = None):
        """
        Initialize tool executor.
        
        Args:
            search_service: SearchService instance (creates new one if not provided)
            serper_api_key: API key for Serper search (optional)
        """
        self.search_service = search_service or SearchService()
        self.serper_api_key = serper_api_key
        
    def execute_tool(self, tool_name: str, tool_args: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute a tool and return the result.
        
        Args:
            tool_name: Name of the tool to execute
            tool_args: Arguments for the tool
            
        Returns:
            Dictionary with 'success', 'result', and optional 'error' keys
        """
        logger.info(f"Executing tool: {tool_name}", extra={'extra_data': {'args': tool_args}})
        
        try:
            if tool_name == "search_web":
                return self._execute_search_web(tool_args)
            elif tool_name == "scrape_webpage":
                return self._execute_scrape_webpage(tool_args)
            else:
                error_msg = f"Unknown tool: {tool_name}"
                logger.error(error_msg)
                return {
                    "success": False,
                    "error": error_msg
                }
        except Exception as e:
            logger.error(f"Tool execution failed: {tool_name}", 
                        extra={'extra_data': {'error': str(e)}}, 
                        exc_info=True)
            return {
                "success": False,
                "error": f"Tool execution error: {str(e)}"
            }
    
    def _execute_search_web(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Execute search_web tool."""
        query = args.get("query")
        max_results = args.get("max_results", 10)
        
        if not query:
            return {
                "success": False,
                "error": "Missing required argument: query"
            }
        
        # Use Serper if API key is available, otherwise DuckDuckGo
        if self.serper_api_key:
            results = self.search_service.search_serper(query, self.serper_api_key, max_results)
            source = "Serper"
        else:
            results = self.search_service.search_web(query, max_results)
            source = "DuckDuckGo"
        
        logger.info(f"Search completed", 
                   extra={'extra_data': {'query': query, 'source': source, 'results_count': len(results)}})
        
        # Format results for LLM
        formatted_results = self._format_search_results(results)
        
        return {
            "success": True,
            "result": formatted_results,
            "metadata": {
                "query": query,
                "source": source,
                "count": len(results)
            }
        }
    
    def _execute_scrape_webpage(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Execute scrape_webpage tool."""
        url = args.get("url")
        max_chars = args.get("max_chars", 5000)
        
        if not url:
            return {
                "success": False,
                "error": "Missing required argument: url"
            }
        
        result = self.search_service.scrape_webpage(url, max_chars)
        
        if result['success']:
            logger.info(f"Scraping completed", 
                       extra={'extra_data': {'url': url, 'content_length': len(result['content'])}})
            return {
                "success": True,
                "result": {
                    "url": result['url'],
                    "content": result['content']
                }
            }
        else:
            logger.warning(f"Scraping failed", 
                          extra={'extra_data': {'url': url, 'error': result.get('error')}})
            return {
                "success": False,
                "error": result.get('error', 'Scraping failed')
            }
    
    def _format_search_results(self, results: list) -> str:
        """
        Format search results into a readable string for LLM.
        
        Args:
            results: List of search result dicts
            
        Returns:
            Formatted string
        """
        if not results:
            return "No results found."
        
        formatted = []
        for i, result in enumerate(results, 1):
            title = result.get('title', 'No title')
            url = result.get('href', 'No URL')
            snippet = result.get('body', 'No snippet available')
            
            formatted.append(f"{i}. {title}\n   URL: {url}\n   {snippet}\n")
        
        return "\n".join(formatted)
    
    def format_tool_result_for_llm(self, tool_name: str, execution_result: Dict[str, Any]) -> str:
        """
        Format tool execution result for LLM consumption.
        
        Args:
            tool_name: Name of the tool that was executed
            execution_result: Result from execute_tool()
            
        Returns:
            Formatted string to pass back to LLM
        """
        if not execution_result.get('success'):
            error = execution_result.get('error', 'Unknown error')
            return f"Tool '{tool_name}' failed: {error}"
        
        result = execution_result.get('result', '')
        
        if isinstance(result, dict):
            # For structured results like scrape_webpage
            return json.dumps(result, indent=2)
        else:
            # For string results like search_web
            return str(result)


def execute_tool(tool_name: str, tool_args: Dict[str, Any], serper_api_key: Optional[str] = None) -> Dict[str, Any]:
    """
    Convenience function to execute a tool without creating executor instance.
    
    Args:
        tool_name: Name of the tool
        tool_args: Tool arguments
        serper_api_key: Optional Serper API key
        
    Returns:
        Tool execution result
    """
    executor = ToolExecutor(serper_api_key=serper_api_key)
    return executor.execute_tool(tool_name, tool_args)
