#!/usr/bin/env python3
"""
Content-related Pydantic models
Request and response schemas for content management endpoints
"""

from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field, validator
from datetime import datetime

class ContentCreate(BaseModel):
    """Content creation request model"""
    title: str = Field(..., min_length=1, max_length=200)
    content_type: str = Field(..., pattern="^(text|image|video|carousel)$")
    platform: str = Field(..., pattern="^(instagram|tiktok|linkedin|youtube|twitter|facebook)$")
    text_content: str = Field(..., min_length=1, max_length=10000)
    hashtags: List[str] = Field(default=[], max_items=30)
    scheduled_for: Optional[datetime] = None
    
    @validator('hashtags')
    def validate_hashtags(cls, v):
        """Validate hashtags"""
        if not v:
            return v
        
        validated_hashtags = []
        for tag in v:
            if not tag.strip():
                continue
            
            # Ensure hashtag starts with #
            if not tag.startswith('#'):
                tag = f"#{tag}"
            
            # Remove extra spaces and validate format
            tag = tag.strip().replace(' ', '')
            if len(tag) > 1:  # At least # plus one character
                validated_hashtags.append(tag)
        
        return validated_hashtags[:30]  # Limit to 30 hashtags
    
    @validator('text_content')
    def validate_text_content(cls, v):
        """Validate text content"""
        if not v.strip():
            raise ValueError('Text content cannot be empty')
        return v.strip()

class ContentUpdate(BaseModel):
    """Content update request model"""
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    text_content: Optional[str] = Field(None, min_length=1, max_length=10000)
    hashtags: Optional[List[str]] = Field(None, max_items=30)
    scheduled_for: Optional[datetime] = None
    
    @validator('hashtags')
    def validate_hashtags(cls, v):
        """Validate hashtags"""
        if v is None:
            return v
        
        validated_hashtags = []
        for tag in v:
            if not tag.strip():
                continue
            
            if not tag.startswith('#'):
                tag = f"#{tag}"
            
            tag = tag.strip().replace(' ', '')
            if len(tag) > 1:
                validated_hashtags.append(tag)
        
        return validated_hashtags[:30]

class ContentResponse(BaseModel):
    """Content response model"""
    id: str
    user_id: str
    title: str
    content_type: str
    platform: str
    text_content: str
    hashtags: List[str]
    status: str
    quality_score: float
    viral_potential: float
    created_at: datetime
    updated_at: datetime
    scheduled_for: Optional[datetime] = None
    published_at: Optional[datetime] = None
    performance_metrics: Dict[str, Any]
    ai_generated: Optional[bool] = False
    generation_metadata: Optional[Dict[str, Any]] = None
    
    class Config:
        from_attributes = True

class ContentFilter(BaseModel):
    """Content filtering model"""
    platform: Optional[str] = Field(None, pattern="^(instagram|tiktok|linkedin|youtube|twitter|facebook)$")
    status: Optional[str] = Field(None, pattern="^(draft|scheduled|published|archived)$")
    content_type: Optional[str] = Field(None, pattern="^(text|image|video|carousel)$")
    date_from: Optional[datetime] = None
    date_to: Optional[datetime] = None
    search_query: Optional[str] = Field(None, max_length=100)
    
class ContentList(BaseModel):
    """Content list response model"""
    items: List[ContentResponse]
    total: int
    page: int
    per_page: int
    has_next: bool
    has_prev: bool

class ContentAnalytics(BaseModel):
    """Content analytics model"""
    total_content: int
    published_content: int
    avg_quality_score: float
    avg_viral_potential: float
    top_performing_platform: str
    engagement_trend: List[Dict[str, Any]]
    hashtag_performance: Dict[str, Any]

class ContentSchedule(BaseModel):
    """Content schedule model"""
    scheduled_for: datetime
    timezone: str = Field(default="UTC")
    
    @validator('scheduled_for')
    def validate_scheduled_for(cls, v):
        """Validate scheduled datetime"""
        if v <= datetime.utcnow():
            raise ValueError('Scheduled time must be in the future')
        return v

class BulkContentOperation(BaseModel):
    """Bulk content operation model"""
    content_ids: List[str] = Field(..., min_items=1, max_items=100)
    operation: str = Field(..., pattern="^(publish|archive|delete|schedule)$")
    scheduled_for: Optional[datetime] = None
    
    @validator('content_ids')
    def validate_content_ids(cls, v):
        """Validate content IDs"""
        if not v:
            raise ValueError('At least one content ID is required')
        return list(set(v))  # Remove duplicates