import os
from typing import Optional
import fastapi
from fastapi import FastAPI, HTTPException, Body, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles
from pydantic import ValidationError
from dotenv import load_dotenv
from agent import ResearchAgent
from schemas import (
    ProfileRequest, ProfileResponse,
    NoteRequest, NoteResponse,
    DeepResearchRequest, DeepResearchResponse,
    SecretRequest, SecretResponse,
    StatusResponse,
    User, LoginResponse, AuthCallbackResponse
)
from secrets_manager import SecretManager
from logger_config import get_logger, set_request_id, log_performance
import uuid
import secrets as secrets_lib

# Import auth functions
import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from auth import (
    get_authorization_url,
    exchange_code_for_token,
    get_user_info,
    create_access_token,
    verify_access_token,
    FRONTEND_URL
)

from models import get_db, init_db, SessionLocal
from repositories import UserRepository, LogRepository
from sqlalchemy.orm import Session
from fastapi import Depends

load_dotenv()

logger = get_logger(__name__)

app = FastAPI(title="Intelligent Research Agent")

# Database startup event
@app.on_event("startup")
async def startup_event():
    """Initialize SQLAlchemy database on startup."""
    init_db()
    logger.info("SQLAlchemy ORM database initialized")

# Database session dependency
def get_db_session() -> Session:
    """Get database session for dependency injection."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Request correlation middleware
@app.middleware("http")
async def add_request_id(request, call_next):
    """Add request ID to each request for correlation."""
    request_id = str(uuid.uuid4())
    set_request_id(request_id)
    logger.info("Request started", extra={'extra_data': {'method': request.method, 'path': request.url.path}})
    
    response = await call_next(request)
    
    logger.info("Request completed", extra={'extra_data': {'status_code': response.status_code}})
    return response

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

# ==================== Authentication Endpoints ====================

@app.get("/auth/login/{provider}")
async def login(provider: str):
    """
    Initiate OAuth login flow for the specified provider.
    Redirects user to provider's authorization page.
    """
    if provider not in ["google", "microsoft", "github"]:
        raise HTTPException(status_code=400, detail=f"Unsupported provider: {provider}")
    
    # Generate random state for CSRF protection
    state = secrets_lib.token_urlsafe(32)
    
    try:
        # Get authorization URL
        auth_url = get_authorization_url(provider, state)
        
        logger.info(f"OAuth login initiated", extra={'extra_data': {'provider': provider}})
        
        # Redirect to OAuth provider
        response = RedirectResponse(url=auth_url)
        # Store state in cookie for verification
        response.set_cookie(
            key="oauth_state",
            value=state,
            httponly=True,
            max_age=600,  # 10 minutes
            samesite="lax"
        )
        return response
        
    except Exception as e:
        logger.error(f"OAuth login failed", extra={'extra_data': {'provider': provider, 'error': str(e)}})
        raise HTTPException(status_code=500, detail=f"Failed to initiate login: {str(e)}")

@app.get("/auth/callback/{provider}")
async def callback(provider: str, code: str, state: str, request: Request, db: Session = Depends(get_db_session)):
    """
    Handle OAuth callback from provider.
    Exchange code for token, fetch user info, create/update user, and set session cookie.
    """
    try:
        # Verify state parameter to prevent CSRF
        stored_state = request.cookies.get("oauth_state")
        if not stored_state or stored_state != state:
            raise HTTPException(status_code=400, detail="Invalid state parameter")
        
        # Exchange code for access token
        token_response = exchange_code_for_token(provider, code)
        access_token = token_response.get("access_token")
        
        if not access_token:
            raise HTTPException(status_code=400, detail="Failed to get access token")
        
        # Fetch user info from provider
        user_info = get_user_info(provider, access_token)
        
        if not user_info.get("email"):
            raise HTTPException(status_code=400, detail="Failed to get user email from provider")
        
        # Create or update user in database using UserRepository
        user_repo = UserRepository(db)
        user = user_repo.create_or_update(
            email=user_info["email"],
            name=user_info.get("name"),
            picture=user_info.get("picture"),
            provider=provider,
            provider_user_id=user_info["provider_user_id"]
        )
        
        # Create JWT token
        token_data = {
            "user_id": user.id,
            "email": user.email,
            "name": user.name
        }
        jwt_token = create_access_token(token_data)
        
        # Redirect to frontend with success
        response = RedirectResponse(url=f"{FRONTEND_URL}/index.html")
        
        # Set JWT cookie (httponly for security)
        response.set_cookie(
            key="access_token",
            value=jwt_token,
            httponly=True,
            max_age=86400,  # 24 hours
            samesite="lax",
            secure=False  # Set to True in production with HTTPS
        )
        
        # Clear oauth_state cookie
        response.delete_cookie("oauth_state")
        
        logger.info(f"User authenticated", extra={'extra_data': {'user_id': user.id, 'provider': provider}})
        
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"OAuth callback failed", extra={'extra_data': {'provider': provider, 'error': str(e)}})
        # Redirect to frontend with error
        return RedirectResponse(url=f"{FRONTEND_URL}/login.html?error={str(e)}")

@app.get("/auth/user")
async def get_current_user(request: Request, db: Session = Depends(get_db_session)):
    """
    Get current authenticated user from JWT token.
    Returns user information if authenticated, 401 if not.
    """
    token = request.cookies.get("access_token")
    
    if not token:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    payload = verify_access_token(token)
    
    if not payload:
        raise HTTPException(status_code=401, detail="Invalid or expired token")
    
    # Get full user info from database using UserRepository
    user_repo = UserRepository(db)
    user = user_repo.get(payload["user_id"])
    
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    return User(
        id=user.id,
        email=user.email,
        name=user.name,
        picture=user.picture,
        provider=user.provider,
        provider_user_id=user.provider_user_id,
        created_at=user.created_at,
        last_login=user.last_login
    )

@app.post("/auth/logout")
async def logout(response: Response):
    """
    Logout user by clearing the access token cookie.
    """
    response.delete_cookie("access_token")
    logger.info("User logged out")
    return {"status": "success", "message": "Logged out successfully"}

# ==================== Helper Functions ====================

def get_current_user_id(request: Request) -> Optional[int]:
    """
    Extract user ID from JWT token if present.
    Returns None if no token or invalid token (doesn't raise exception).
    """
    token = request.cookies.get("access_token")
    if not token:
        return None
    
    payload = verify_access_token(token)
    if not payload:
        return None
    
    return payload.get("user_id")

# ==================== Research Endpoints ====================

@app.post("/api/research", response_model=ProfileResponse)
def research_profile(request: ProfileRequest, req: Request, db: Session = Depends(get_db_session)):
    """
    1. Search web for info.
    2. Generate profile using LLM.
    """
    try:
        # Get current user ID if authenticated
        user_id = get_current_user_id(req)
        
        # Determine API Key based on provider
        if request.model_provider == "gemini":
            api_key = request.api_key or secret_manager.get_secret("GEMINI_API_KEY") or os.getenv("GEMINI_API_KEY")
        elif request.model_provider == "grok":
            api_key = request.api_key or secret_manager.get_secret("GROK_API_KEY") or os.getenv("GROK_API_KEY")
        else:
            api_key = request.api_key or secret_manager.get_secret("OPENAI_API_KEY") or os.getenv("OPENAI_API_KEY")
        
        # Only use Serper if explicitly requested by search_provider
        serper_key = None
        if request.search_provider == "serper":
            serper_key = request.serper_api_key or secret_manager.get_secret("SERPER_API_KEY") or os.getenv("SERPER_API_KEY")

        if not api_key:
            raise HTTPException(status_code=400, detail=f"{request.model_provider.capitalize()} API Key is required.")

        # CACHE LEVEL 1: Check for complete cached result using LogRepository
        complete_cache_key = {
            "name": request.name,
            "company": request.company,
            "additional_info": request.additional_info,
            "search_provider": request.search_provider,
            "model_provider": request.model_provider
        }
        
        if not request.bypass_cache:
            log_repo = LogRepository(db)
            cached_complete = log_repo.check_cache(
                action_type="complete_research",
                search_data=complete_cache_key
            )
            
            if cached_complete:
                logger.info("Cache hit (Complete) - skipping both Serper and LLM", 
                           extra={'extra_data': {'name': request.name, 'company': request.company}})
                import json
                cached_response = json.loads(cached_complete)
                cached_response["from_cache"] = True
                return cached_response

        # CACHE LEVEL 2 & 3: Proceed with gather_info and generate_profile (which have their own caching)
        # CACHE LEVEL 2 & 3: Proceed with research generation
        logger.info("Generating profile", extra={'extra_data': {'model_provider': request.model_provider, 'search_mode': request.search_mode}})
        
        profile_text, research_data, from_cache, cached_note = agent.generate_profile_with_mode(
            name=request.name,
            company=request.company,
            additional_info=request.additional_info,
            api_key=api_key,
            provider=request.model_provider,
            serper_api_key=serper_key,
            bypass_cache=request.bypass_cache,
            search_mode=request.search_mode,
            db=db
        )
        
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
        
        # Cache the complete result for future requests using LogRepository
        if not request.bypass_cache:
            import json
            log_repo = LogRepository(db)
            log_repo.create_log(
                action_type="complete_research",
                user_id=user_id,
                search_data=complete_cache_key,
                model_input="Complete research request",
                model_output="Complete research response",
                final_output=json.dumps(response)
            )
            logger.info("Cached complete result", extra={'extra_data': {'name': request.name}})
        
        return response
    
    except ValidationError as e:
        # Extract the first validation error message
        error_msg = e.errors()[0]['msg'] if e.errors() else "Validation error"
        raise HTTPException(status_code=422, detail=f"Invalid input: {error_msg}")

@app.post("/api/generate-note", response_model=NoteResponse)
def generate_note(request: NoteRequest, req: Request, db: Session = Depends(get_db_session)):
    if request.model_provider == "gemini":
        api_key = request.api_key or secret_manager.get_secret("GEMINI_API_KEY") or os.getenv("GEMINI_API_KEY")
    elif request.model_provider == "grok":
        api_key = request.api_key or secret_manager.get_secret("GROK_API_KEY") or os.getenv("GROK_API_KEY")
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
        bypass_cache=request.bypass_cache,
        db=db
    )
    
    return {
        "note": note,
        "from_cache": from_cache
    }

@app.post("/api/deep-research", response_model=DeepResearchResponse)
def deep_research(request: DeepResearchRequest, req: Request, db: Session = Depends(get_db_session)):
    """
    Performs deep research on a topic using Gemini 1.5 Pro.
    """
    # Get current user ID
    user_id = get_current_user_id(req)
    
    api_key = request.api_key or secret_manager.get_secret("GEMINI_API_KEY") or os.getenv("GEMINI_API_KEY")
    
    # Only use Serper if explicitly requested by search_provider
    serper_key = None
    if request.search_provider == "serper":
        serper_key = request.serper_api_key or secret_manager.get_secret("SERPER_API_KEY") or os.getenv("SERPER_API_KEY")

    if not api_key:
        raise HTTPException(status_code=400, detail="Gemini API Key is required for deep research.")

    try:
        logger.info("Deep research", extra={'extra_data': {'topic': request.topic, 'search_provider': request.search_provider.upper(), 'user_id': user_id}})
        report = agent.perform_deep_research(request.topic, api_key, serper_key, bypass_cache=request.bypass_cache, db=db)
        return {"report": report}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Mount static files (frontend)
# This must be after API routes to avoid shadowing
frontend_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "frontend")
if os.path.exists(frontend_dir):
    app.mount("/", StaticFiles(directory=frontend_dir, html=True), name="static")
else:
    logger.warning(f"Frontend directory not found at {frontend_dir}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

