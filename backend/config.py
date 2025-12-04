import os
from typing import Optional

try:
    from pydantic_settings import BaseSettings
except ImportError:
    # Fallback for environments without pydantic-settings
    from pydantic import BaseModel as BaseSettings


class Settings(BaseSettings):
    """Application configuration settings with .env support."""
    
    # === LLM Provider Settings ===
    DEFAULT_MODEL_PROVIDER: str = "gemini"
    DEFAULT_SEARCH_PROVIDER: str = "ddg"
    
    # === OpenAI Settings ===
    OPENAI_MODEL: str = "gpt-5-nano"
    OPENAI_TEMPERATURE: float = 1.0
    OPENAI_MAX_TOKENS: int = 4096
    
    # === Gemini Settings ===
    GEMINI_MODEL: str = "gemini-2.5-flash"
    GEMINI_TEMPERATURE: float = 0.7
    GEMINI_MAX_TOKENS: int = 8192
    
    # === Grok Settings ===
    GROK_MODEL: str = "grok-4-1-fast"
    GROK_TEMPERATURE: float = 0.8
    GROK_MAX_TOKENS: int = 4096
    
    # === Database Settings ===
    DATABASE_TYPE: str = "sqlite"
    
    # SQLite
    SQLITE_DATABASE_URL: str = "sqlite:///./agent_logs.db"
    
    # PostgreSQL (for future)
    POSTGRES_USER: Optional[str] = None
    POSTGRES_PASSWORD: Optional[str] = None
    POSTGRES_HOST: str = "localhost"
    POSTGRES_PORT: str = "5432"
    POSTGRES_DB: Optional[str] = None
    
    # MySQL (for future)
    MYSQL_USER: Optional[str] = None
    MYSQL_PASSWORD: Optional[str] = None
    MYSQL_HOST: str = "localhost"
    MYSQL_PORT: str = "3306"
    MYSQL_DB: Optional[str] = None
    
    # === Function Calling / Tool Use ===
    USE_FUNCTION_CALLING: bool = False
    SEARCH_MODE: str = "rag"  # Options: 'rag', 'tools', 'hybrid'
    MAX_ITERATIONS: int = 10  # Max tool calling iterations
    
    model_config = {
        "env_file": ".env",
        "env_file_encoding": "utf-8",
        "extra": "ignore"
    }
    
    def get_provider_config(self, provider: str) -> dict:
        """Return config dict for a specific LLM provider."""
        configs = {
            "openai": {
                "model": self.OPENAI_MODEL,
                "temperature": self.OPENAI_TEMPERATURE,
                "max_tokens": self.OPENAI_MAX_TOKENS
            },
            "gemini": {
                "model": self.GEMINI_MODEL,
                "temperature": self.GEMINI_TEMPERATURE,
                "max_tokens": self.GEMINI_MAX_TOKENS
            },
            "grok": {
                "model": self.GROK_MODEL,
                "temperature": self.GROK_TEMPERATURE,
                "max_tokens": self.GROK_MAX_TOKENS
            },
        }
        return configs.get(provider, configs["gemini"])
    
    @property
    def database_url(self) -> str:
        """Get database URL based on DATABASE_TYPE."""
        if self.DATABASE_TYPE == "sqlite":
            return self.SQLITE_DATABASE_URL
        elif self.DATABASE_TYPE == "postgresql":
            if not all([self.POSTGRES_USER, self.POSTGRES_PASSWORD, self.POSTGRES_DB]):
                raise ValueError("PostgreSQL credentials not properly configured")
            return (
                f"postgresql://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}"
                f"@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
            )
        elif self.DATABASE_TYPE == "mysql":
            if not all([self.MYSQL_USER, self.MYSQL_PASSWORD, self.MYSQL_DB]):
                raise ValueError("MySQL credentials not properly configured")
            return (
                f"mysql+pymysql://{self.MYSQL_USER}:{self.MYSQL_PASSWORD}"
                f"@{self.MYSQL_HOST}:{self.MYSQL_PORT}/{self.MYSQL_DB}"
            )
        else:
            raise ValueError(f"Unsupported database type: {self.DATABASE_TYPE}")


settings = Settings()
