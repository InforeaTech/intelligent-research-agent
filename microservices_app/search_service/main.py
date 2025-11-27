import json
import requests
from typing import List, Dict, Optional
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from ddgs import DDGS

app = FastAPI(title="Search Service")

# Models
class SearchRequest(BaseModel):
    query: str
    max_results: int = 10
    api_key: Optional[str] = None

class ScrapeRequest(BaseModel):
    url: str
    max_chars: int = 5000

# Service Logic (Migrated)
class SearchService:
    def __init__(self):
        self.ddgs = DDGS()

    def search_serper(self, query: str, api_key: str, max_results: int = 10) -> List[Dict]:
        print(f"Searching Serper for: {query}")
        url = "https://google.serper.dev/search"
        payload = json.dumps({"q": query, "num": max_results})
        headers = {
            'X-API-KEY': api_key,
            'Content-Type': 'application/json'
        }
        try:
            response = requests.post(url, headers=headers, data=payload)
            if response.status_code != 200:
                print(f"Serper API Error: {response.status_code} - {response.text}")
                return []
            
            data = response.json()
            results = data.get("organic", [])
            return [{"title": r.get("title"), "href": r.get("link"), "body": r.get("snippet")} for r in results]
        except Exception as e:
            print(f"Serper error: {e}")
            return []

    def search_web(self, query: str, max_results: int = 10) -> List[Dict]:
        print(f"Searching DDG for: {query}")
        try:
            results = list(self.ddgs.text(query, max_results=max_results))
            return results
        except Exception as e:
            print(f"Search error: {e}")
            return []

    def scrape_webpage(self, url: str, max_chars: int = 5000) -> Dict[str, str]:
        try:
            print(f"Scraping: {url}")
            headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
            response = requests.get(url, headers=headers, timeout=5)
            response.raise_for_status()
            
            from bs4 import BeautifulSoup
            soup = BeautifulSoup(response.content, 'html.parser')
            
            for element in soup(['script', 'style', 'nav', 'footer', 'header', 'aside']):
                element.decompose()
            
            text = soup.get_text(separator=' ', strip=True)
            text = ' '.join(text.split())
            
            if len(text) > max_chars:
                text = text[:max_chars] + '...'
            
            return {'url': url, 'content': text, 'success': True}
        except Exception as e:
            print(f"Scraping error for {url}: {e}")
            return {'url': url, 'content': '', 'success': False, 'error': str(e)}

service = SearchService()

# Routes
@app.post("/search/serper")
async def search_serper(request: SearchRequest):
    if not request.api_key:
        raise HTTPException(status_code=400, detail="API Key required for Serper")
    return service.search_serper(request.query, request.api_key, request.max_results)

@app.post("/search/web")
async def search_web(request: SearchRequest):
    return service.search_web(request.query, request.max_results)

@app.post("/scrape")
async def scrape(request: ScrapeRequest):
    return service.scrape_webpage(request.url, request.max_chars)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)
