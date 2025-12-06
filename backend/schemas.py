from typing import Optional, Dict, Any, List
from pydantic import BaseModel, field_validator, ValidationError
from config import settings

# --- Request Models ---

class ProfileRequest(BaseModel):
    name: str
    company: str = ""
    additional_info: str = ""
    api_key: str
    model_provider: str = settings.DEFAULT_MODEL_PROVIDER  # gemini, openai, or grok
    search_provider: str = settings.DEFAULT_SEARCH_PROVIDER  # ddg or serper
    serper_api_key: Optional[str] = None
    bypass_cache: bool = False
    search_mode: Optional[str] = None  # rag, tools, or hybrid

    @field_validator('search_mode')
    @classmethod
    def validate_search_mode(cls, v: Optional[str]) -> Optional[str]:
        if v is not None:
            v = v.lower()
            if v not in ["rag", "tools", "hybrid"]:
                raise ValueError("search_mode must be 'rag', 'tools', or 'hybrid'")
        return v
    
    @field_validator('name')
    @classmethod
    def validate_person_name(cls, v: str) -> str:
        """Validate that the name is a person's full name."""
        if not v or not v.strip():
            raise ValueError("Name cannot be empty")
        
        # Remove extra whitespace
        v = v.strip()
        
        # Check if name has at least two parts (first name and last name)
        name_parts = v.split()
        if len(name_parts) < 2:
            raise ValueError("Full name must include at least first and last name (e.g., 'John Doe')")
        
        # Validate that name contains only valid characters for person names
        # Allow letters, spaces, hyphens, apostrophes (for names like O'Brien, Mary-Jane)
        import re
        if not re.match(r"^[a-zA-Z\s\-'\.]+$", v):
            raise ValueError("Name must contain only alphabetic characters, spaces, hyphens, apostrophes, or periods")
        
        return v

class DeepResearchRequest(BaseModel):
    topic: str
    api_key: str
    model_provider: str = settings.DEFAULT_MODEL_PROVIDER  # gemini, openai, or grok
    search_provider: str = settings.DEFAULT_SEARCH_PROVIDER  # ddg or serper
    serper_api_key: Optional[str] = None
    bypass_cache: bool = False
    search_mode: Optional[str] = None  # rag, tools, or hybrid

    @field_validator('search_mode')
    @classmethod
    def validate_search_mode(cls, v: Optional[str]) -> Optional[str]:
        if v is not None:
            v = v.lower()
            if v not in ["rag", "tools", "hybrid"]:
                raise ValueError("search_mode must be 'rag', 'tools', or 'hybrid'")
        return v

class CompanyAnalysisRequest(BaseModel):
    company_name: str
    industry: Optional[str] = None
    focus_areas: Optional[List[str]] = None
    api_key: str
    model_provider: str = settings.DEFAULT_MODEL_PROVIDER
    search_provider: str = settings.DEFAULT_SEARCH_PROVIDER
    serper_api_key: Optional[str] = None
    bypass_cache: bool = False


class NoteRequest(BaseModel):
    profile_text: str
    length: str = "medium"  # short, medium, or long
    tone: str = "professional"
    context: str = ""
    api_key: Optional[str] = None  # Optional - can be retrieved from secrets manager
    model_provider: str = settings.DEFAULT_MODEL_PROVIDER  # gemini, openai, or grok
    bypass_cache: bool = False
    profile_id: Optional[int] = None

class SecretRequest(BaseModel):
    key: str
    value: str

# --- Response Models ---

class ProfileResponse(BaseModel):
    research_data: Dict[str, Any]
    profile: str
    from_cache: bool = False
    cached_note: Optional[str] = None
    cached_note_from_cache: bool = False
    id: Optional[int] = None  # Profile ID for linking to history

class NoteResponse(BaseModel):
    note: str
    from_cache: bool = False

class DeepResearchResponse(BaseModel):
    report: str

class CompanyAnalysisResponse(BaseModel):
    id: Optional[int] = None
    name: str
    analysis: str
    from_cache: bool = False


class SecretResponse(BaseModel):
    key: str
    value: str

class StatusResponse(BaseModel):
    status: str
    message: str

# --- Authentication Models ---

class User(BaseModel):
    id: int
    email: str
    name: Optional[str] = None
    picture: Optional[str] = None
    provider: str

class LoginResponse(BaseModel):
    authorization_url: str
    state: str

class AuthCallbackResponse(BaseModel):
    success: bool
    user: Optional[User] = None
    message: str = ""

# --- History Models ---

from datetime import datetime

class NoteSchema(BaseModel):
    id: int
    profile_id: int
    note_text: str
    tone: str
    length: str  # short, medium, or long
    context: Optional[str] = None
    timestamp: datetime
    
    class Config:
        from_attributes = True

class ProfileSchema(BaseModel):
    id: int
    user_id: int
    name: str
    company: Optional[str] = None
    additional_info: Optional[str] = None
    profile_text: str
    search_provider: str
    model_provider: str
    timestamp: datetime
    
    class Config:
        from_attributes = True


