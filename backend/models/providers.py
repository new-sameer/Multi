#!/usr/bin/env python3
"""
Provider configuration Pydantic models
Request and response schemas for provider management endpoints
"""

from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field, validator
from datetime import datetime

class ProviderConfigRequest(BaseModel):
    """Provider configuration request"""
    api_key: str = Field(..., min_length=10)
    endpoint: Optional[str] = None
    enabled: bool = Field(default=True)
    priority: int = Field(default=5, ge=1, le=10)
    
    @validator('api_key')
    def validate_api_key(cls, v):
        """Validate API key"""
        if not v.strip():
            raise ValueError('API key cannot be empty')
        if len(v.strip()) < 10:
            raise ValueError('API key appears to be too short')
        return v.strip()

class ProviderConfigResponse(BaseModel):
    """Provider configuration response"""
    provider: str
    display_name: str
    description: str
    status: str  # healthy, unhealthy, unavailable
    connection: str  # active, failed, not_configured
    models_available: int
    cost_type: str  # free, pay_per_token, subscription
    requires_api_key: bool
    configured: bool
    setup_url: str
    error: Optional[str] = None
    
    class Config:
        from_attributes = True

class ProviderListResponse(BaseModel):
    """Provider list response"""
    providers: List[ProviderConfigResponse]
    total_providers: int
    healthy_providers: int
    
    class Config:
        from_attributes = True

class ProviderTestRequest(BaseModel):
    """Provider connection test request"""
    test_prompt: Optional[str] = Field(None, max_length=100)
    
    @validator('test_prompt')
    def validate_test_prompt(cls, v):
        """Validate test prompt"""
        if v and not v.strip():
            return None
        return v.strip() if v else v

class ProviderTestResponse(BaseModel):
    """Provider connection test response"""
    provider: str
    success: bool
    response_time: float
    model_used: Optional[str] = None
    tokens_used: Optional[int] = None
    cost: Optional[float] = None
    test_response: Optional[str] = None
    error: Optional[str] = None
    message: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        from_attributes = True

class CostOptimizationRequest(BaseModel):
    """Cost optimization analysis request"""
    analysis_period_days: int = Field(default=30, ge=7, le=90)
    target_monthly_cost: float = Field(default=50.0, ge=0)
    optimization_goals: List[str] = Field(default=["reduce_cost", "maintain_quality"])
    
    @validator('optimization_goals')
    def validate_optimization_goals(cls, v):
        """Validate optimization goals"""
        valid_goals = ["reduce_cost", "maintain_quality", "increase_speed", "reduce_tokens"]
        for goal in v:
            if goal not in valid_goals:
                raise ValueError(f'Invalid optimization goal: {goal}')
        return v

class ProviderMetrics(BaseModel):
    """Provider performance metrics"""
    provider: str
    avg_response_time: float
    success_rate: float
    cost_per_request: float
    quality_score: float
    reliability_score: float
    last_30_days_requests: int
    
    class Config:
        from_attributes = True

class ProviderQuota(BaseModel):
    """Provider usage quota information"""
    provider: str
    daily_limit: Optional[int] = None
    monthly_limit: Optional[int] = None
    current_daily_usage: int = 0
    current_monthly_usage: int = 0
    quota_reset_date: Optional[datetime] = None
    quota_exceeded: bool = False
    
    class Config:
        from_attributes = True

class ModelRecommendation(BaseModel):
    """Model recommendation based on task and constraints"""
    model_name: str
    provider: str
    confidence_score: float
    reasoning: str
    estimated_cost: float
    estimated_time: float
    quality_prediction: float
    
    class Config:
        from_attributes = True

class ProviderMigration(BaseModel):
    """Provider migration suggestion"""
    from_provider: str
    to_provider: str
    migration_reason: str
    estimated_savings: float
    quality_impact: str  # positive, neutral, negative
    complexity: str  # low, medium, high
    recommended: bool
    
    class Config:
        from_attributes = True