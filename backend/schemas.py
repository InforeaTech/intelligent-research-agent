from typing import Optional, Dict, Any
from pydantic import BaseModel

# --- Request Models ---

class ProfileRequest(BaseModel):
    name: str
    company: str = ""
    additional_info: str = ""
    api_key: str
    model_provider: str = "gemini"  # gemini or openai
    serper_api_key: Optional[str] = None
    bypass_cache: bool = False

class DeepResearchRequest(BaseModel):
    topic: str
    api_key: str
    serper_api_key: Optional[str] = None
    bypass_cache: bool = False

class NoteRequest(BaseModel):
    profile_text: str
    length: int = 300
    tone: str = "professional"
    context: str = ""
    api_key: str
    model_provider: str = "gemini"  # gemini or openai
    bypass_cache: bool = False

class SecretRequest(BaseModel):
    key: str
    value: str

# --- Response Models ---

class ProfileResponse(BaseModel):
    research_data: Dict[str, Any]
    profile: str

class NoteResponse(BaseModel):
    note: str

class DeepResearchResponse(BaseModel):
    report: str

class SecretResponse(BaseModel):
    key: str
    value: str

class StatusResponse(BaseModel):
    status: str
    message: str
