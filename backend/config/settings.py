"""
Application Settings and Configuration
Environment-based configuration management
"""
from pydantic_settings import BaseSettings
from typing import List
import os

class Settings(BaseSettings):
    """Application settings with environment variable support"""
    
    # API Configuration
    api_title: str = "Web Content Analyzer"
    api_version: str = "1.0.0"
    api_description: str = "API for analyzing web content with LLM integration"
    debug: bool = False
    
    # Server Configuration
    host: str = "0.0.0.0"
    port: int = 8000
    reload: bool = False
    
    # Security Configuration
    allowed_origins: List[str] = ["http://localhost:8501", "http://frontend:8501"]
    allowed_domains: List[str] = ["*"]  # Will restrict in production
    max_content_size: int = 10 * 1024 * 1024  # 10MB
    request_timeout: int = 30  # seconds
    max_requests_per_minute: int = 60
    
    # Scraping Configuration
    user_agents: List[str] = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    ]
    
    # Content Processing
    min_content_length: int = 100
    max_text_size: int = 5 * 1024 * 1024  # 5MB for text processing
    max_keywords: int = 20
    
    # Logging Configuration
    log_level: str = "INFO"
    log_format: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    
    # Environment
    environment: str = "development"
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False

# Global settings instance
settings = Settings()

# Environment-specific configurations
def get_settings() -> Settings:
    """Get settings instance for dependency injection"""
    return settings

def is_development() -> bool:
    """Check if running in development mode"""
    return settings.environment.lower() == "development"

def is_production() -> bool:
    """Check if running in production mode"""
    return settings.environment.lower() == "production"
