#!/usr/bin/env python3
"""
Ollama-specific Pydantic models
Request and response schemas for Ollama management endpoints
"""

from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field, validator
from datetime import datetime

class OllamaModelInstallRequest(BaseModel):
    """Ollama model installation request"""
    model_name: str = Field(..., min_length=1, max_length=100)
    
    @validator('model_name')
    def validate_model_name(cls, v):
        """Validate model name format"""
        if not v.strip():
            raise ValueError('Model name cannot be empty')
        
        # Basic validation for Ollama model name format
        if ':' in v and not v.count(':') == 1:
            raise ValueError('Invalid model name format')
        
        return v.strip()

class OllamaModelResponse(BaseModel):
    """Ollama model information response"""
    name: str
    size_gb: Optional[float] = None
    description: str
    capabilities: List[str] = []
    installed: bool = False
    recommended: bool = False
    performance_score: Optional[float] = None
    
    class Config:
        from_attributes = True

class OllamaHealthCheck(BaseModel):
    """Ollama health check response"""
    status: str  # healthy, unhealthy, error
    connection: str  # active, failed, unknown
    models_available: int
    error: Optional[str] = None
    last_checked: datetime = Field(default_factory=datetime.utcnow)

class OllamaSystemInfo(BaseModel):
    """Ollama system information"""
    status: str
    memory_available_gb: float
    disk_space_gb: float
    gpu_available: bool
    gpu_memory_gb: Optional[float] = None
    recommended_models: List[str] = []
    
    class Config:
        from_attributes = True

class ModelOptimizationRequest(BaseModel):
    """Model optimization request"""
    optimization_goal: str = Field(default="balanced", pattern="^(speed|quality|cost|balanced)$")
    task_types: Optional[List[str]] = None
    resource_constraints: Optional[Dict[str, Any]] = None
    
    @validator('task_types')
    def validate_task_types(cls, v):
        """Validate task types"""
        if v is None:
            return v
        
        valid_tasks = ["general", "content_generation", "success_coaching", "content_adaptation"]
        for task in v:
            if task not in valid_tasks:
                raise ValueError(f'Invalid task type: {task}')
        
        return v

class ModelPerformanceMetrics(BaseModel):
    """Model performance metrics"""
    model_name: str
    avg_response_time: float
    quality_score: float
    resource_usage: Dict[str, float]
    success_rate: float
    user_satisfaction: Optional[float] = None
    
    class Config:
        from_attributes = True

class OllamaConfiguration(BaseModel):
    """Ollama configuration settings"""
    base_url: str = Field(default="http://localhost:11434")
    timeout_seconds: int = Field(default=300, ge=30, le=3600)
    max_concurrent_requests: int = Field(default=4, ge=1, le=16)
    auto_install_models: bool = Field(default=True)
    preferred_models: List[str] = []
    
    @validator('base_url')
    def validate_base_url(cls, v):
        """Validate Ollama base URL"""
        if not v.startswith(('http://', 'https://')):
            raise ValueError('Base URL must start with http:// or https://')
        return v

class ModelInstallationStatus(BaseModel):
    """Model installation status tracking"""
    model_name: str
    status: str  # installing, installed, failed, removing
    progress_percentage: Optional[float] = None
    estimated_time_remaining: Optional[int] = None  # seconds
    error_message: Optional[str] = None
    started_at: datetime = Field(default_factory=datetime.utcnow)
    completed_at: Optional[datetime] = None