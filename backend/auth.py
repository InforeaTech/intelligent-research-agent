"""
Authentication service for OpenID Connect (OIDC) social login.
Supports Google, Microsoft, and GitHub OAuth providers.
"""

import os
import sys
from datetime import datetime, timedelta
from typing import Dict, Optional, Any
from authlib.integrations.requests_client import OAuth2Session
from jose import JWTError, jwt
from dotenv import load_dotenv

# Add backend directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from logger_config import get_logger

load_dotenv()
logger = get_logger(__name__)

# JWT Configuration
JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "dev-secret-key-change-in-prod")
JWT_ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")
JWT_EXPIRATION_HOURS = int(os.getenv("JWT_EXPIRATION_HOURS", "24"))

# OAuth Provider Configuration
OAUTH_PROVIDERS = {
    "google": {
        "client_id": os.getenv("GOOGLE_CLIENT_ID"),
        "client_secret": os.getenv("GOOGLE_CLIENT_SECRET"),
        "authorize_url": "https://accounts.google.com/o/oauth2/v2/auth",
        "token_url": "https://oauth2.googleapis.com/token",
        "userinfo_url": "https://www.googleapis.com/oauth2/v2/userinfo",
        "scope": "openid email profile",
    },
    "microsoft": {
        "client_id": os.getenv("MICROSOFT_CLIENT_ID"),
        "client_secret": os.getenv("MICROSOFT_CLIENT_SECRET"),
        "authorize_url": "https://login.microsoftonline.com/common/oauth2/v2.0/authorize",
        "token_url": "https://login.microsoftonline.com/common/oauth2/v2.0/token",
        "userinfo_url": "https://graph.microsoft.com/v1.0/me",
        "scope": "openid email profile User.Read",
    },
    "github": {
        "client_id": os.getenv("GITHUB_CLIENT_ID"),
        "client_secret": os.getenv("GITHUB_CLIENT_SECRET"),
        "authorize_url": "https://github.com/login/oauth/authorize",
        "token_url": "https://github.com/login/oauth/access_token",
        "userinfo_url": "https://api.github.com/user",
        "scope": "read:user user:email",
    }
}

# OAuth Redirect URI
OAUTH_REDIRECT_URI = os.getenv("OAUTH_REDIRECT_URI", "http://localhost:8000/auth/callback")
FRONTEND_URL = os.getenv("FRONTEND_URL", "http://localhost:8000")


def get_oauth_client(provider: str) -> OAuth2Session:
    """
    Initialize OAuth2 client for the specified provider.
    
    Args:
        provider: OAuth provider name ('google', 'microsoft', 'github')
        
    Returns:
        OAuth2Session configured for the provider
        
    Raises:
        ValueError: If provider is not supported or credentials are missing
    """
    if provider not in OAUTH_PROVIDERS:
        raise ValueError(f"Unsupported OAuth provider: {provider}")
    
    config = OAUTH_PROVIDERS[provider]
    
    if not config["client_id"] or not config["client_secret"]:
        raise ValueError(f"OAuth credentials not configured for {provider}")
    
    client = OAuth2Session(
        client_id=config["client_id"],
        client_secret=config["client_secret"],
        scope=config["scope"],
        redirect_uri=f"{OAUTH_REDIRECT_URI}/{provider}"
    )
    
    logger.info(f"OAuth client initialized", extra={'extra_data': {'provider': provider}})
    return client


def get_authorization_url(provider: str, state: str) -> str:
    """
    Generate OAuth authorization URL for user redirect.
    
    Args:
        provider: OAuth provider name
        state: CSRF token for security
        
    Returns:
        Authorization URL to redirect user to
    """
    config = OAUTH_PROVIDERS[provider]
    client = get_oauth_client(provider)
    
    # Generate authorization URL
    uri, state_from_client = client.create_authorization_url(
        config["authorize_url"],
        state=state
    )
    
    logger.info(f"Authorization URL generated", extra={'extra_data': {'provider': provider}})
    return uri


def exchange_code_for_token(provider: str, code: str) -> Dict[str, Any]:
    """
    Exchange authorization code for access token.
    
    Args:
        provider: OAuth provider name
        code: Authorization code from OAuth callback
        
    Returns:
        Token response containing access_token and other data
        
    Raises:
        Exception: If token exchange fails
    """
    config = OAUTH_PROVIDERS[provider]
    client = get_oauth_client(provider)
    
    try:
        # Exchange code for token
        token = client.fetch_token(
            config["token_url"],
            code=code,
            grant_type="authorization_code"
        )
        
        logger.info(f"Token exchanged successfully", extra={'extra_data': {'provider': provider}})
        return token
    except Exception as e:
        logger.error(f"Token exchange failed", extra={'extra_data': {'provider': provider, 'error': str(e)}})
        raise


def get_user_info(provider: str, access_token: str) -> Dict[str, Any]:
    """
    Fetch user information from OAuth provider.
    
    Args:
        provider: OAuth provider name
        access_token: Access token from OAuth flow
        
    Returns:
        User information dictionary with standardized fields:
        - email: User's email address
        - name: User's display name
        - picture: Profile picture URL
        - provider_user_id: User ID from provider
        
    Raises:
        Exception: If fetching user info fails
    """
    config = OAUTH_PROVIDERS[provider]
    
    try:
        import requests
        
        headers = {"Authorization": f"Bearer {access_token}"}
        response = requests.get(config["userinfo_url"], headers=headers)
        response.raise_for_status()
        
        user_data = response.json()
        
        # Normalize user data across providers
        if provider == "google":
            normalized = {
                "email": user_data.get("email"),
                "name": user_data.get("name"),
                "picture": user_data.get("picture"),
                "provider_user_id": user_data.get("id"),
            }
        elif provider == "microsoft":
            normalized = {
                "email": user_data.get("mail") or user_data.get("userPrincipalName"),
                "name": user_data.get("displayName"),
                "picture": None,  # Microsoft Graph requires separate photo endpoint
                "provider_user_id": user_data.get("id"),
            }
        elif provider == "github":
            normalized = {
                "email": user_data.get("email"),
                "name": user_data.get("name") or user_data.get("login"),
                "picture": user_data.get("avatar_url"),
                "provider_user_id": str(user_data.get("id")),
            }
            
            # GitHub may not return email in main response if private
            if not normalized["email"]:
                emails_response = requests.get(
                    "https://api.github.com/user/emails",
                    headers=headers
                )
                if emails_response.ok:
                    emails = emails_response.json()
                    primary_email = next(
                        (e["email"] for e in emails if e.get("primary")),
                        emails[0]["email"] if emails else None
                    )
                    normalized["email"] = primary_email
        else:
            normalized = {}
        
        logger.info(f"User info fetched", extra={'extra_data': {'provider': provider, 'email': normalized.get('email')}})
        return normalized
        
    except Exception as e:
        logger.error(f"Failed to fetch user info", extra={'extra_data': {'provider': provider, 'error': str(e)}})
        raise


def create_access_token(user_data: Dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
    """
    Create JWT access token for authenticated user.
    
    Args:
        user_data: User information to encode in token
        expires_delta: Optional custom expiration time
        
    Returns:
        Encoded JWT token string
    """
    to_encode = user_data.copy()
    
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(hours=JWT_EXPIRATION_HOURS)
    
    to_encode.update({
        "exp": expire,
        "iat": datetime.utcnow()
    })
    
    encoded_jwt = jwt.encode(to_encode, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)
    
    logger.info(f"JWT token created", extra={'extra_data': {'user_id': user_data.get('user_id'), 'expires': expire.isoformat()}})
    return encoded_jwt


def verify_access_token(token: str) -> Optional[Dict[str, Any]]:
    """
    Verify and decode JWT access token.
    
    Args:
        token: JWT token string to verify
        
    Returns:
        Decoded token payload if valid, None if invalid
    """
    try:
        payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM])
        
        # Check if token is expired
        exp = payload.get("exp")
        if exp and datetime.fromtimestamp(exp) < datetime.utcnow():
            logger.warning("Token expired")
            return None
        
        logger.debug(f"Token verified", extra={'extra_data': {'user_id': payload.get('user_id')}})
        return payload
        
    except JWTError as e:
        logger.warning(f"Token verification failed", extra={'extra_data': {'error': str(e)}})
        return None
