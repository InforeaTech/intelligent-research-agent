import json
import requests
from typing import List, Dict
from ddgs import DDGS
from logger_config import get_logger, log_performance

logger = get_logger(__name__)

class SearchService:
    def __init__(self):
        self.ddgs = DDGS()

    @log_performance()
    def search_serper(self, query: str, api_key: str, max_results: int = 10) -> List[Dict]:
        """Performs a web search using Serper.dev."""
        logger.info("Searching Serper", extra={'extra_data': {'query': query, 'max_results': max_results}})
        url = "https://google.serper.dev/search"
        payload = json.dumps({"q": query, "num": max_results})
        headers = {
            'X-API-KEY': api_key,
            'Content-Type': 'application/json',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36'
        }
        try:
            response = requests.post(url, headers=headers, data=payload)
            if response.status_code != 200:
                logger.error("Serper API Error", extra={'extra_data': {'status_code': response.status_code, 'response_text': response.text}})
                return []
            
            data = response.json()
            results = data.get("organic", [])
            return [{"title": r.get("title"), "href": r.get("link"), "body": r.get("snippet")} for r in results]
        except Exception as e:
            logger.error("Serper search failed", extra={'extra_data': {'error': str(e)}}, exc_info=True)
            if 'response' in locals():
                logger.debug("Response content", extra={'extra_data': {'content': response.text}})
            return []

    @log_performance()
    def search_web(self, query: str, max_results: int = 10) -> List[Dict]:
        """Performs a web search using DuckDuckGo."""
        logger.info("Searching DDG", extra={'extra_data': {'query': query, 'max_results': max_results}})
        try:
            results = list(self.ddgs.text(query, max_results=max_results))
            return results
        except Exception as e:
            logger.error("DDG search failed", extra={'extra_data': {'error': str(e)}}, exc_info=True)
            return []

    @log_performance()
    def scrape_webpage(self, url: str, max_chars: int = 5000) -> Dict[str, str]:
        """Scrapes webpage and extracts main content."""
        try:
            logger.info("Scraping webpage", extra={'extra_data': {'url': url}})
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            response = requests.get(url, headers=headers, timeout=5)
            response.raise_for_status()
            
            from bs4 import BeautifulSoup
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Remove script, style, nav, footer elements
            for element in soup(['script', 'style', 'nav', 'footer', 'header', 'aside']):
                element.decompose()
            
            # Get text content
            text = soup.get_text(separator=' ', strip=True)
            
            # Clean up whitespace
            text = ' '.join(text.split())
            
            # Limit length
            if len(text) > max_chars:
                text = text[:max_chars] + '...'
            
            return {
                'url': url,
                'content': text,
                'success': True
            }
        except Exception as e:
            logger.error("Scraping failed", extra={'extra_data': {'url': url, 'error': str(e)}}, exc_info=True)
            return {
                'url': url,
                'content': '',
                'success': False,
                'error': str(e)
            }
