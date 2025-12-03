import os
from typing import Optional


class Settings:
    """Application configuration settings."""
    
    # Database
    DATABASE_TYPE: str = os.getenv("DB_TYPE", "sqlite")
    
    # SQLite
    SQLITE_DATABASE_URL: str = os.getenv(
        "SQLITE_DATABASE_URL", 
        "sqlite:///./agent_logs.db"
    )
    
    # PostgreSQL (for future)
    POSTGRES_USER: Optional[str] = os.getenv("POSTGRES_USER")
    POSTGRES_PASSWORD: Optional[str] = os.getenv("POSTGRES_PASSWORD")
    POSTGRES_HOST: Optional[str] = os.getenv("POSTGRES_HOST", "localhost")
    POSTGRES_PORT: str = os.getenv("POSTGRES_PORT", "5432")
    POSTGRES_DB: Optional[str] = os.getenv("POSTGRES_DB")
    
    # MySQL (for future)
    MYSQL_USER: Optional[str] = os.getenv("MYSQL_USER")
    MYSQL_PASSWORD: Optional[str] = os.getenv("MYSQL_PASSWORD")
    MYSQL_HOST: Optional[str] = os.getenv("MYSQL_HOST", "localhost")
    MYSQL_PORT: str = os.getenv("MYSQL_PORT", "3306")
    MYSQL_DB: Optional[str] = os.getenv("MYSQL_DB")
    
    @property
    def database_url(self) -> str:
        """Get database URL based on DATABASE_TYPE environment variable."""
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
