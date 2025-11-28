import os
import fastapi
from fastapi import FastAPI, HTTPException, Body
from fastapi.middleware.cors import CORSMiddleware
from pydantic import ValidationError
from dotenv import load_dotenv
from agent import ResearchAgent
from schemas import (
    ProfileRequest, ProfileResponse,
    NoteRequest, NoteResponse,
    DeepResearchRequest, DeepResearchResponse,
    SecretRequest, SecretResponse,
    StatusResponse
)
from secrets_manager import SecretManager

load_dotenv()

app = FastAPI(title="Intelligent Research Agent")

# CORS Setup
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # WARNING: In production, replace "*" with specific frontend origin(s)
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

agent = ResearchAgent()
secret_manager = SecretManager()

@app.get("/", response_model=StatusResponse)
def read_root():
    return {"status": "online", "message": "Intelligent Research Agent API is running."}

@app.post("/api/secrets/set", response_model=StatusResponse)
def set_secret(request: SecretRequest):
    """Store an encrypted secret (API key)."""
    try:
        secret_manager.set_secret(request.key, request.value)
        return {"status": "success", "message": f"Secret '{request.key}' stored securely."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/secrets/get/{key}", response_model=SecretResponse)
def get_secret(key: str):
    """Retrieve a stored secret."""
    try:
        value = secret_manager.get_secret(key)
        if value is None:
            raise HTTPException(status_code=404, detail=f"Secret '{key}' not found.")
        return {"key": key, "value": value}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/research", response_model=ProfileResponse)
def research_profile(request: ProfileRequest):
    """
    1. Search web for info.
    2. Generate profile using LLM.
    """
    try:
        # Determine API Key based on provider
        if request.model_provider == "gemini":
            api_key = request.api_key or secret_manager.get_secret("GEMINI_API_KEY") or os.getenv("GEMINI_API_KEY")
        else:
            api_key = request.api_key or secret_manager.get_secret("OPENAI_API_KEY") or os.getenv("OPENAI_API_KEY")
        
        # Only use Serper if explicitly requested by search_provider
        serper_key = None
        if request.search_provider == "serper":
            serper_key = request.serper_api_key or secret_manager.get_secret("SERPER_API_KEY") or os.getenv("SERPER_API_KEY")

        if not api_key:
            raise HTTPException(status_code=400, detail=f"{request.model_provider.capitalize()} API Key is required.")

        # 1. Gather Info
        print(f"Gathering info for {request.name} using {request.search_provider.upper()}...")
        research_data = agent.gather_info(request.name, request.company, request.additional_info, serper_key)
        
        # 2. Generate Profile
        print(f"Generating profile using {request.model_provider}...")
        profile_text, from_cache, cached_note = agent.generate_profile(research_data, api_key, request.model_provider, bypass_cache=request.bypass_cache)
        
        # Prepare response
        response = {
            "research_data": research_data,
            "profile": profile_text,
            "from_cache": from_cache
        }
        
        # Include cached note if available
        if cached_note:
            response["cached_note"] = cached_note.get('note')
            response["cached_note_from_cache"] = True
        
        return response
    
    except ValidationError as e:
        # Extract the first validation error message
        error_msg = e.errors()[0]['msg'] if e.errors() else "Validation error"
        raise HTTPException(status_code=422, detail=f"Invalid input: {error_msg}")

@app.post("/api/generate-note", response_model=NoteResponse)
def generate_note(request: NoteRequest):
    if request.model_provider == "gemini":
        api_key = request.api_key or secret_manager.get_secret("GEMINI_API_KEY") or os.getenv("GEMINI_API_KEY")
    else:
        api_key = request.api_key or secret_manager.get_secret("OPENAI_API_KEY") or os.getenv("OPENAI_API_KEY")
    
    if not api_key:
        raise HTTPException(status_code=400, detail=f"{request.model_provider.capitalize()} API Key is required.")

    note, from_cache = agent.generate_note(
        request.profile_text, 
        request.length, 
        request.tone, 
        request.context, 
        api_key,
        request.model_provider,
        bypass_cache=request.bypass_cache
    )
    
    return {
        "note": note,
        "from_cache": from_cache
    }

@app.post("/api/deep-research", response_model=DeepResearchResponse)
def deep_research(request: DeepResearchRequest):
    """
    Performs deep research on a topic using Gemini 1.5 Pro.
    """
    api_key = request.api_key or secret_manager.get_secret("GEMINI_API_KEY") or os.getenv("GEMINI_API_KEY")
    
    # Only use Serper if explicitly requested by search_provider
    serper_key = None
    if request.search_provider == "serper":
        serper_key = request.serper_api_key or secret_manager.get_secret("SERPER_API_KEY") or os.getenv("SERPER_API_KEY")

    if not api_key:
        raise HTTPException(status_code=400, detail="Gemini API Key is required for deep research.")

    try:
        print(f"Deep research using {request.search_provider.upper()}...")
        report = agent.perform_deep_research(request.topic, api_key, serper_key, bypass_cache=request.bypass_cache)
        return {"report": report}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

