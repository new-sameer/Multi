#!/usr/bin/env python3
"""
User-related Pydantic models
Request and response schemas for user management endpoints
"""

from typing import Optional, Dict, Any
from pydantic import BaseModel, Field, validator
from datetime import datetime

class UserProfileUpdate(BaseModel):
    """User profile update request model"""
    first_name: Optional[str] = Field(None, min_length=1, max_length=100)
    last_name: Optional[str] = Field(None, min_length=1, max_length=100)
    niche: Optional[str] = Field(None, max_length=100)
    target_audience: Optional[str] = Field(None, max_length=200)
    
    @validator('first_name', 'last_name', 'niche', 'target_audience')
    def validate_strings(cls, v):
        """Validate string fields"""
        if v is not None and not v.strip():
            raise ValueError('Field cannot be empty or whitespace only')
        return v.strip() if v else v

class SuccessGoals(BaseModel):
    """Success goals model"""
    followers_target: int = Field(default=1000, ge=100, le=10000000)
    engagement_rate_target: float = Field(default=0.03, ge=0.01, le=1.0)
    revenue_target: float = Field(default=100.0, ge=0, le=1000000.0)
    timeframe_days: int = Field(default=90, ge=30, le=365)
    
    @validator('followers_target')
    def validate_followers_target(cls, v):
        """Validate followers target"""
        if v < 100:
            raise ValueError('Followers target must be at least 100')
        return v
    
    @validator('engagement_rate_target')
    def validate_engagement_rate(cls, v):
        """Validate engagement rate target"""
        if v < 0.01 or v > 1.0:
            raise ValueError('Engagement rate must be between 0.01 and 1.0')
        return v

class SuccessGoalsResponse(BaseModel):
    """Success goals response model"""
    message: str
    goals: Dict[str, Any]

class UserPreferences(BaseModel):
    """User preferences model"""
    voice_enabled: bool = Field(default=False)
    notification_email: bool = Field(default=True)
    notification_push: bool = Field(default=True)
    timezone: str = Field(default="UTC", max_length=50)
    language: str = Field(default="en", max_length=10)
    theme: str = Field(default="light", pattern="^(light|dark|auto)$")
    
    @validator('timezone')
    def validate_timezone(cls, v):
        """Validate timezone"""
        # Basic timezone validation - in production, use pytz for full validation
        if not v or not v.strip():
            raise ValueError('Timezone cannot be empty')
        return v.strip()

class UserStats(BaseModel):
    """User statistics model"""
    total_content_created: int
    total_posts_published: int
    total_engagement: int
    success_score: float
    days_since_registration: int
    current_streak: int
    achievements_unlocked: int

class UserActivity(BaseModel):
    """User activity model"""
    last_login: datetime
    last_content_created: Optional[datetime] = None
    last_post_published: Optional[datetime] = None
    total_sessions: int
    average_session_duration: float  # in minutes

class SubscriptionUpdate(BaseModel):
    """Subscription update model"""
    tier: str = Field(..., pattern="^(starter|professional|enterprise)$")
    billing_period: str = Field(default="monthly", pattern="^(monthly|yearly)$")
    
    @validator('tier')
    def validate_tier(cls, v):
        """Validate subscription tier"""
        valid_tiers = ['starter', 'professional', 'enterprise']
        if v not in valid_tiers:
            raise ValueError(f'Invalid subscription tier. Must be one of: {valid_tiers}')
        return v

class UserDashboard(BaseModel):
    """User dashboard data model"""
    user_info: Dict[str, Any]
    stats: UserStats
    recent_activity: UserActivity
    success_progress: Dict[str, Any]
    quick_actions: list
    notifications: list