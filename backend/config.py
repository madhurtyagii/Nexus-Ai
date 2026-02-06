"""
Nexus AI - Application Configuration
Centralized configuration using Pydantic Settings
"""

from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    """Application settings loaded from environment variables"""
    
    # Database
    database_url: str
    
    # Redis
    redis_url: str = "redis://localhost:6379/0"
    
    # JWT Authentication
    secret_key: str
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 1440  # 24 hours
    
    # LLM Configuration
    ollama_base_url: str = "http://localhost:11434"
    groq_api_key: str = ""
    
    # Search Configuration
    tavily_api_key: str = ""
    
    # Server
    host: str = "0.0.0.0"
    port: int = 8000
    debug: bool = True
    
    # Frontend URL (for CORS)
    frontend_url: str = "http://localhost:5173"
    
    # Storage Configuration
    upload_dir: str = "./storage/uploads"
    max_file_size: int = 10485760  # 10MB
    allowed_extensions: str = "csv,txt,pdf,png,jpg,jpeg,xlsx,json"
    
    # Logging & Monitoring
    log_format: str = "text"  # "text" or "json"
    enable_metrics: bool = True
    
    class Config:
        env_file = ".env"
        case_sensitive = False
        extra = "ignore"


def get_settings() -> Settings:
    """
    Get settings instance.
    Reads .env file on every call to ensure fresh configuration in development.
    """
    return Settings()
