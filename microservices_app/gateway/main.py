import os
import json
import requests
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, Dict, Any

app = FastAPI(title="Research Agent Gateway")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Service URLs
SEARCH_SERVICE_URL = "http://localhost:8001"
CONTENT_SERVICE_URL = "http://localhost:8002"
AUDIT_SERVICE_URL = "http://localhost:8003"

# Models (Same as original schemas)
class DeepResearchRequest(BaseModel):
    topic: str
    api_key: str
    serper_api_key: Optional[str] = None

class ProfileRequest(BaseModel):
    name: str
    company: str = ""
    additional_info: str = ""
    api_key: str
    serper_api_key: Optional[str] = None

class NoteRequest(BaseModel):
    profile_text: str
    length: int = 300
    tone: str = "professional"
    context: str = ""
    api_key: str

# Helper to log to Audit Service
def log_interaction(action_type: str, user_input: Dict = None, search_data: Any = None, 
                   model_input: str = None, model_output: str = None, final_output: str = None):
    try:
        requests.post(f"{AUDIT_SERVICE_URL}/logs", json={
            "action_type": action_type,
            "user_input": user_input,
            "search_data": search_data,
            "model_input": model_input,
            "model_output": model_output,
            "final_output": final_output
        })
    except Exception as e:
        print(f"Failed to log interaction: {e}")

@app.post("/api/deep-research")
async def deep_research(request: DeepResearchRequest):
    try:
        # 1. Plan Research (Content Service)
        plan_res = requests.post(f"{CONTENT_SERVICE_URL}/research/plan", json={
            "topic": request.topic, "api_key": request.api_key
        }).json()
        queries = plan_res.get("queries", [])
        
        log_interaction("deep_research_planning", 
                       user_input={"topic": request.topic}, 
                       model_input=plan_res.get("prompt"), 
                       model_output=plan_res.get("raw_response"), 
                       final_output=json.dumps(queries))

        # 2. Execute Searches (Search Service)
        all_results = []
        for q in queries:
            if request.serper_api_key:
                res = requests.post(f"{SEARCH_SERVICE_URL}/search/serper", json={
                    "query": q, "api_key": request.serper_api_key, "max_results": 10
                }).json()
            else:
                res = requests.post(f"{SEARCH_SERVICE_URL}/search/web", json={
                    "query": q, "max_results": 10
                }).json()
            all_results.extend(res)

        # Deduplicate
        unique_results = {r['href']: r for r in all_results if r.get('href')}.values()
        
        # 3. Scrape (Search Service)
        scraped_data = []
        for result in unique_results:
            scrape_res = requests.post(f"{SEARCH_SERVICE_URL}/scrape", json={
                "url": result['href']
            }).json()
            
            scraped_data.append({
                'title': result.get('title', ''),
                'url': result['href'],
                'snippet': result.get('body', ''),
                'content': scrape_res.get('content', '') if scrape_res.get('success') else '(Content not available)'
            })

        # 4. Synthesize (Content Service)
        report_res = requests.post(f"{CONTENT_SERVICE_URL}/research/synthesize", json={
            "topic": request.topic, 
            "context_str": json.dumps(scraped_data), 
            "api_key": request.api_key
        }).json()
        
        report_text = report_res.get("report")
        
        log_interaction("deep_research", 
                       user_input={"topic": request.topic}, 
                       search_data=scraped_data, 
                       model_input=report_res.get("prompt"), 
                       model_output=report_text, 
                       final_output=report_text)
                       
        return {"report": report_text}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
