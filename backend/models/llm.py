#!/usr/bin/env python3
"""
LLM-related Pydantic models
Request and response schemas for LLM endpoints
"""

from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field, validator
from datetime import datetime

class LLMGenerateRequest(BaseModel):
    """LLM generation request model"""
    prompt: str = Field(..., min_length=1, max_length=10000)
    task_type: str = Field(default="general", pattern="^(general|content_generation|success_coaching|content_adaptation)$")
    preferred_provider: Optional[str] = Field(None, pattern="^(ollama|groq)$")
    max_tokens: int = Field(default=1000, ge=50, le=4000)
    temperature: float = Field(default=0.7, ge=0.0, le=2.0)
    
    @validator('prompt')
    def validate_prompt(cls, v):
        """Validate prompt"""
        if not v.strip():
            raise ValueError('Prompt cannot be empty')
        return v.strip()

class LLMResponse(BaseModel):
    """LLM response model"""
    content: str
    provider: str
    model: str
    tokens_used: int
    response_time: float
    cost: float
    quality_score: Optional[float] = None
    
    class Config:
        from_attributes = True

class ModelInfo(BaseModel):
    """Model information model"""
    name: str
    provider: str
    available: bool
    size_gb: Optional[float] = None
    context_length: Optional[int] = None
    capabilities: List[str] = []
    
    class Config:
        from_attributes = True

class UsageStatistics(BaseModel):
    """Usage statistics model"""
    period_days: int
    user_id: Optional[str] = None
    providers: List[Dict[str, Any]]
    generated_at: datetime
    
    class Config:
        from_attributes = True

class AIContentRequest(BaseModel):
    """AI content generation request model"""
    platform: str = Field(..., pattern="^(instagram|tiktok|linkedin|youtube|twitter|facebook)$")
    content_type: str = Field(..., pattern="^(text|image|video|carousel)$")
    topic: str = Field(..., min_length=1, max_length=200)
    target_audience: Optional[str] = Field(None, max_length=200)
    tone: str = Field(default="professional", pattern="^(professional|casual|funny|inspiring|educational)$")
    hashtag_count: int = Field(default=5, ge=0, le=30)
    
    @validator('topic')
    def validate_topic(cls, v):
        """Validate topic"""
        if not v.strip():
            raise ValueError('Topic cannot be empty')
        return v.strip()

class AIContentResponse(BaseModel):
    """AI content generation response model"""
    content: Dict[str, Any]
    generation_info: Dict[str, Any]

class LLMHealthCheck(BaseModel):
    """LLM health check model"""
    timestamp: datetime
    providers: Dict[str, Dict[str, Any]]
    overall_status: str

class ProviderConfig(BaseModel):
    """LLM provider configuration model"""
    provider: str = Field(..., pattern="^(ollama|groq|openai|claude|perplexity)$")
    api_key: Optional[str] = None
    endpoint: Optional[str] = None
    enabled: bool = True
    priority: int = Field(default=1, ge=1, le=10)
    
    @validator('api_key')
    def validate_api_key(cls, v):
        """Validate API key format"""
        if v and len(v.strip()) < 10:
            raise ValueError('API key seems too short')
        return v

class ModelOptimization(BaseModel):
    """Model optimization request model"""
    task_type: str = Field(..., pattern="^(general|content_generation|success_coaching|content_adaptation)$")
    optimization_goal: str = Field(default="balanced", pattern="^(speed|quality|cost|balanced)$")
    user_preferences: Optional[Dict[str, Any]] = None

class BatchLLMRequest(BaseModel):
    """Batch LLM request model"""
    requests: List[LLMGenerateRequest] = Field(..., min_items=1, max_items=10)
    parallel_execution: bool = Field(default=True)
    
    @validator('requests')
    def validate_requests(cls, v):
        """Validate batch requests"""
        if not v:
            raise ValueError('At least one request is required')
        return v

class LLMMetrics(BaseModel):
    """LLM metrics model"""
    total_requests: int
    successful_requests: int
    failed_requests: int
    average_response_time: float
    total_tokens_used: int
    total_cost: float
    provider_breakdown: Dict[str, Any]
    popular_tasks: List[Dict[str, Any]]