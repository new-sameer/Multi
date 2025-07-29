#!/usr/bin/env python3
"""
Configuration management for the Social Media Automation Platform
Centralized environment variable handling and configuration settings
"""

import os
from typing import List, Optional
from pydantic import BaseSettings, validator
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class Settings(BaseSettings):
    """Application settings and configuration"""
    
    # Database Configuration
    MONGO_URL: str = "mongodb://localhost:27017/socialmedia_automation"
    
    # JWT Configuration
    JWT_SECRET: str = "your-super-secret-jwt-key-change-in-production"
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRATION_HOURS: int = 24
    
    # Redis Configuration
    REDIS_URL: str = "redis://localhost:6379"
    
    # API Keys - LLM Integration
    OPENAI_API_KEY: Optional[str] = None
    GROQ_API_KEY: Optional[str] = None
    CLAUDE_API_KEY: Optional[str] = None
    PERPLEXITY_API_KEY: Optional[str] = None
    
    # Ollama Configuration
    OLLAMA_BASE_URL: str = "http://localhost:11434"
    
    # Social Media API Keys
    INSTAGRAM_CLIENT_ID: Optional[str] = None
    INSTAGRAM_CLIENT_SECRET: Optional[str] = None
    TIKTOK_CLIENT_KEY: Optional[str] = None
    TIKTOK_CLIENT_SECRET: Optional[str] = None
    LINKEDIN_CLIENT_ID: Optional[str] = None
    LINKEDIN_CLIENT_SECRET: Optional[str] = None
    YOUTUBE_API_KEY: Optional[str] = None
    TWITTER_API_KEY: Optional[str] = None
    TWITTER_API_SECRET: Optional[str] = None
    FACEBOOK_APP_ID: Optional[str] = None
    FACEBOOK_APP_SECRET: Optional[str] = None
    
    # Voice Processing
    WHISPER_API_KEY: Optional[str] = None
    TTS_SERVICE_URL: str = "http://localhost:5000"
    
    # Email Configuration
    SMTP_SERVER: str = "smtp.gmail.com"
    SMTP_PORT: int = 587
    SMTP_USERNAME: Optional[str] = None
    SMTP_PASSWORD: Optional[str] = None
    
    # Application Configuration
    ENVIRONMENT: str = "development"
    DEBUG: bool = True
    LOG_LEVEL: str = "INFO"
    
    # CORS Configuration
    CORS_ORIGINS: List[str] = ["http://localhost:3000", "http://127.0.0.1:3000"]
    
    # File Upload Configuration
    MAX_FILE_SIZE: int = 10485760  # 10MB in bytes
    UPLOAD_DIR: str = "./uploads"
    
    # Rate Limiting Configuration
    RATE_LIMIT_REQUESTS: int = 100
    RATE_LIMIT_WINDOW: int = 60  # seconds
    
    # Subscription & Billing
    STRIPE_PUBLISHABLE_KEY: Optional[str] = None
    STRIPE_SECRET_KEY: Optional[str] = None
    STRIPE_WEBHOOK_SECRET: Optional[str] = None
    
    # Security Configuration
    BCRYPT_ROUNDS: int = 12
    
    # Performance Configuration
    CONNECTION_POOL_SIZE: int = 10
    DATABASE_TIMEOUT: int = 30
    
    @validator('CORS_ORIGINS', pre=True)
    def parse_cors_origins(cls, v):
        """Parse CORS origins from string or list"""
        if isinstance(v, str):
            return [origin.strip() for origin in v.split(',')]
        return v
    
    class Config:
        env_file = ".env"
        case_sensitive = True

# Global settings instance
settings = Settings()

def get_settings() -> Settings:
    """Get application settings instance"""
    return settings