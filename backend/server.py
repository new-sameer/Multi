#!/usr/bin/env python3
"""
Social Media Automation Platform - FastAPI Backend
Main server application with authentication, user management, and core API endpoints.
"""

import os
import uuid
from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any
from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, EmailStr, Field
from motor.motor_asyncio import AsyncIOMotorClient
from passlib.context import CryptContext
import jwt
from bson import ObjectId
import logging

# Import LLM Manager
from services.llm_manager import UniversalLLMManager, TaskType, LLMProvider

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Environment variables
MONGO_URL = os.environ.get("MONGO_URL", "mongodb://localhost:27017/socialmedia_automation")
JWT_SECRET = os.environ.get("JWT_SECRET", "your-super-secret-jwt-key-change-in-production")
JWT_ALGORITHM = "HS256"

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Security
security = HTTPBearer()

# Database client
mongo_client: Optional[AsyncIOMotorClient] = None
database = None
llm_manager: Optional[UniversalLLMManager] = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager for startup and shutdown events."""
    # Startup
    global mongo_client, database, llm_manager
    try:
        mongo_client = AsyncIOMotorClient(MONGO_URL)
        database = mongo_client.get_default_database()
        logger.info("Connected to MongoDB successfully")
        
        # Create indexes for better performance
        await create_indexes()
        
        # Initialize LLM Manager
        llm_manager = UniversalLLMManager(database)
        logger.info("LLM Manager initialized successfully")
        
        yield
    except Exception as e:
        logger.error(f"Failed to connect to MongoDB: {e}")
        raise
    finally:
        # Shutdown
        if mongo_client:
            mongo_client.close()
            logger.info("MongoDB connection closed")

# FastAPI app initialization
app = FastAPI(
    title="Social Media Automation Platform API",
    description="AI-powered social media automation with success coaching and affiliate marketing",
    version="1.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    openapi_url="/api/openapi.json",
    lifespan=lifespan
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ================================
# Pydantic Models
# ================================

class UserCreate(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=8)
    first_name: str = Field(..., min_length=1)
    last_name: str = Field(..., min_length=1)
    niche: Optional[str] = None
    target_audience: Optional[str] = None

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class UserResponse(BaseModel):
    id: str
    email: str
    first_name: str
    last_name: str
    subscription_tier: str
    success_level: str
    niche: Optional[str]
    target_audience: Optional[str]
    onboarding_completed: bool
    success_score: float
    total_earnings: float
    created_at: datetime

class TokenResponse(BaseModel):
    access_token: str
    token_type: str
    user: UserResponse

class SuccessGoals(BaseModel):
    followers_target: int = Field(default=1000, ge=100)
    engagement_rate_target: float = Field(default=0.03, ge=0.01, le=1.0)
    revenue_target: float = Field(default=100.0, ge=0)
    timeframe_days: int = Field(default=90, ge=30, le=365)

class ContentCreate(BaseModel):
    title: str = Field(..., min_length=1)
    content_type: str = Field(..., pattern="^(text|image|video|carousel)$")
    platform: str = Field(..., pattern="^(instagram|tiktok|linkedin|youtube|twitter|facebook)$")
    text_content: str = Field(..., min_length=1)
    hashtags: List[str] = Field(default=[])
    scheduled_for: Optional[datetime] = None

class ContentResponse(BaseModel):
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
    performance_metrics: Dict[str, Any]

# ================================
# LLM Management Models (Phase 2)
# ================================

class LLMGenerateRequest(BaseModel):
    prompt: str = Field(..., min_length=1, max_length=10000)
    task_type: str = Field(default="general", pattern="^(general|content_generation|success_coaching|content_adaptation)$")
    preferred_provider: Optional[str] = Field(default=None, pattern="^(ollama|groq)$")
    max_tokens: int = Field(default=1000, ge=50, le=4000)
    temperature: float = Field(default=0.7, ge=0.0, le=2.0)

class LLMResponse(BaseModel):
    content: str
    provider: str
    model: str
    tokens_used: int
    response_time: float
    cost: float
    quality_score: Optional[float] = None

class ModelInfo(BaseModel):
    name: str
    provider: str
    available: bool
    size_gb: Optional[float] = None
    context_length: Optional[int] = None
    capabilities: List[str] = []

class UsageStatistics(BaseModel):
    period_days: int
    user_id: Optional[str]
    providers: List[Dict[str, Any]]
    generated_at: datetime

# ================================
# Database Helper Functions
# ================================

async def create_indexes():
    """Create database indexes for better performance."""
    try:
        # User collection indexes
        await database.users.create_index("email", unique=True)
        await database.users.create_index("created_at")
        
        # Content collection indexes
        await database.contents.create_index([("user_id", 1), ("created_at", -1)])
        await database.contents.create_index("platform")
        await database.contents.create_index("status")
        
        # Success journeys indexes
        await database.success_journeys.create_index("user_id", unique=True)
        
        # LLM usage logs indexes
        await database.llm_usage_logs.create_index([("user_id", 1), ("timestamp", -1)])
        await database.llm_usage_logs.create_index("provider")
        await database.llm_usage_logs.create_index("task_type")
        
        logger.info("Database indexes created successfully")
    except Exception as e:
        logger.error(f"Failed to create database indexes: {e}")

def hash_password(password: str) -> str:
    """Hash a password for storing in the database."""
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against its hash."""
    return pwd_context.verify(plain_password, hashed_password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    """Create a JWT access token."""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(hours=24)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, JWT_SECRET, algorithm=JWT_ALGORITHM)
    return encoded_jwt

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Get the current authenticated user."""
    token = credentials.credentials
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        user_id: str = payload.get("sub")
        if user_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )
    except jwt.PyJWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    user = await database.users.find_one({"_id": ObjectId(user_id)})
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return user

def convert_objectid_to_str(doc: dict) -> dict:
    """Convert MongoDB ObjectId to string for JSON serialization."""
    if doc and "_id" in doc:
        doc["id"] = str(doc["_id"])
        del doc["_id"]
    return doc

# ================================
# API Endpoints
# ================================

@app.get("/api/health")
async def health_check():
    """Health check endpoint."""
    try:
        # Test database connection
        await database.command("ping")
        return {
            "status": "healthy",
            "timestamp": datetime.utcnow(),
            "services": {
                "database": "connected",
                "api": "running"
            }
        }
    except Exception as e:
        return JSONResponse(
            status_code=503,
            content={
                "status": "unhealthy",
                "timestamp": datetime.utcnow(),
                "error": str(e)
            }
        )

# ================================
# Authentication Endpoints
# ================================

@app.post("/api/v1/auth/register", response_model=TokenResponse)
async def register_user(user_data: UserCreate):
    """Register a new user."""
    # Check if user already exists
    existing_user = await database.users.find_one({"email": user_data.email})
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User with this email already exists"
        )
    
    # Create new user
    user_dict = {
        "_id": ObjectId(),
        "email": user_data.email,
        "password_hash": hash_password(user_data.password),
        "first_name": user_data.first_name,
        "last_name": user_data.last_name,
        "subscription_tier": "starter",
        "success_level": "beginner",
        "niche": user_data.niche,
        "target_audience": user_data.target_audience,
        "onboarding_completed": False,
        "voice_enabled": False,
        "success_score": 0.0,
        "total_earnings": 0.0,
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow(),
        "last_active": datetime.utcnow()
    }
    
    try:
        result = await database.users.insert_one(user_dict)
        user_dict = convert_objectid_to_str(user_dict)
        
        # Create success journey for new user
        await create_initial_success_journey(str(result.inserted_id))
        
        # Generate access token
        access_token = create_access_token(data={"sub": str(result.inserted_id)})
        
        user_response = UserResponse(**user_dict)
        return TokenResponse(
            access_token=access_token,
            token_type="bearer",
            user=user_response
        )
    except Exception as e:
        logger.error(f"Failed to create user: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create user"
        )

@app.post("/api/v1/auth/login", response_model=TokenResponse)
async def login_user(user_credentials: UserLogin):
    """Login a user."""
    user = await database.users.find_one({"email": user_credentials.email})
    if not user or not verify_password(user_credentials.password, user["password_hash"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Update last active timestamp
    await database.users.update_one(
        {"_id": user["_id"]},
        {"$set": {"last_active": datetime.utcnow()}}
    )
    
    # Generate access token
    access_token = create_access_token(data={"sub": str(user["_id"])})
    
    user = convert_objectid_to_str(user)
    user_response = UserResponse(**user)
    
    return TokenResponse(
        access_token=access_token,
        token_type="bearer",
        user=user_response
    )

# ================================
# User Management Endpoints
# ================================

@app.get("/api/v1/users/profile", response_model=UserResponse)
async def get_user_profile(current_user: dict = Depends(get_current_user)):
    """Get current user's profile."""
    user = convert_objectid_to_str(current_user)
    return UserResponse(**user)

@app.put("/api/v1/users/profile", response_model=UserResponse)
async def update_user_profile(
    first_name: Optional[str] = None,
    last_name: Optional[str] = None,
    niche: Optional[str] = None,
    target_audience: Optional[str] = None,
    current_user: dict = Depends(get_current_user)
):
    """Update user profile."""
    update_data = {"updated_at": datetime.utcnow()}
    
    if first_name is not None:
        update_data["first_name"] = first_name
    if last_name is not None:
        update_data["last_name"] = last_name
    if niche is not None:
        update_data["niche"] = niche
    if target_audience is not None:
        update_data["target_audience"] = target_audience
    
    await database.users.update_one(
        {"_id": current_user["_id"]},
        {"$set": update_data}
    )
    
    updated_user = await database.users.find_one({"_id": current_user["_id"]})
    updated_user = convert_objectid_to_str(updated_user)
    
    return UserResponse(**updated_user)

@app.post("/api/v1/users/success-goals")
async def set_success_goals(
    goals: SuccessGoals,
    current_user: dict = Depends(get_current_user)
):
    """Set user's success goals."""
    success_journey = await database.success_journeys.find_one({"user_id": str(current_user["_id"])})
    
    goals_dict = {
        "followers_target": goals.followers_target,
        "engagement_rate_target": goals.engagement_rate_target,
        "revenue_target": goals.revenue_target,
        "timeframe_days": goals.timeframe_days,
        "set_at": datetime.utcnow()
    }
    
    if success_journey:
        await database.success_journeys.update_one(
            {"user_id": str(current_user["_id"])},
            {"$set": {
                "success_goals": goals_dict,
                "updated_at": datetime.utcnow()
            }}
        )
    else:
        await create_initial_success_journey(str(current_user["_id"]), goals_dict)
    
    # Mark onboarding as completed if not already done
    if not current_user.get("onboarding_completed"):
        await database.users.update_one(
            {"_id": current_user["_id"]},
            {"$set": {"onboarding_completed": True, "updated_at": datetime.utcnow()}}
        )
    
    return {"message": "Success goals set successfully", "goals": goals_dict}

# ================================
# Content Management Endpoints
# ================================

@app.post("/api/v1/content/create", response_model=ContentResponse)
async def create_content(
    content_data: ContentCreate,
    current_user: dict = Depends(get_current_user)
):
    """Create new content."""
    content_dict = {
        "_id": ObjectId(),
        "user_id": str(current_user["_id"]),
        "title": content_data.title,
        "content_type": content_data.content_type,
        "platform": content_data.platform,
        "text_content": content_data.text_content,
        "hashtags": content_data.hashtags,
        "status": "draft",
        "quality_score": 0.0,  # Will be calculated by AI later
        "viral_potential": 0.0,  # Will be calculated by AI later
        "scheduled_for": content_data.scheduled_for,
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow(),
        "performance_metrics": {}
    }
    
    try:
        result = await database.contents.insert_one(content_dict)
        content_dict = convert_objectid_to_str(content_dict)
        return ContentResponse(**content_dict)
    except Exception as e:
        logger.error(f"Failed to create content: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create content"
        )

@app.get("/api/v1/content/list", response_model=List[ContentResponse])
async def list_user_content(
    platform: Optional[str] = None,
    status: Optional[str] = None,
    limit: int = 50,
    skip: int = 0,
    current_user: dict = Depends(get_current_user)
):
    """List user's content with optional filtering."""
    filter_query = {"user_id": str(current_user["_id"])}
    
    if platform:
        filter_query["platform"] = platform
    if status:
        filter_query["status"] = status
    
    contents = await database.contents.find(filter_query).sort("created_at", -1).skip(skip).limit(limit).to_list(length=None)
    
    content_list = []
    for content in contents:
        content = convert_objectid_to_str(content)
        content_list.append(ContentResponse(**content))
    
    return content_list

# ================================
# LLM Management Endpoints (Phase 2)
# ================================

@app.post("/api/v1/llm/generate", response_model=LLMResponse)
async def generate_content_with_llm(
    request: LLMGenerateRequest,
    current_user: dict = Depends(get_current_user)
):
    """Generate content using the Universal LLM Manager"""
    if not llm_manager:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="LLM Manager not available"
        )
    
    try:
        # Convert string enums to proper enums
        task_type = TaskType(request.task_type)
        preferred_provider = LLMProvider(request.preferred_provider) if request.preferred_provider else None
        
        response = await llm_manager.generate_content(
            prompt=request.prompt,
            task_type=task_type,
            preferred_provider=preferred_provider,
            max_tokens=request.max_tokens,
            temperature=request.temperature,
            user_id=str(current_user["_id"])
        )
        
        return LLMResponse(
            content=response.content,
            provider=response.provider,
            model=response.model,
            tokens_used=response.tokens_used,
            response_time=response.response_time,
            cost=response.cost,
            quality_score=response.quality_score
        )
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid parameter: {e}"
        )
    except Exception as e:
        logger.error(f"LLM generation failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Content generation failed: {str(e)}"
        )

@app.get("/api/v1/llm/models", response_model=List[ModelInfo])
async def get_available_models(current_user: dict = Depends(get_current_user)):
    """Get list of available LLM models"""
    if not llm_manager:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="LLM Manager not available"
        )
    
    try:
        models = await llm_manager.get_available_models()
        return [
            ModelInfo(
                name=model.name,
                provider=model.provider,
                available=model.available,
                size_gb=model.size_gb,
                context_length=model.context_length,
                capabilities=model.capabilities or []
            ) for model in models
        ]
    except Exception as e:
        logger.error(f"Failed to get available models: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get available models"
        )

@app.get("/api/v1/llm/usage-statistics", response_model=UsageStatistics)
async def get_llm_usage_statistics(
    days: int = 30,
    current_user: dict = Depends(get_current_user)
):
    """Get LLM usage statistics for the current user"""
    if not llm_manager:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="LLM Manager not available"
        )
    
    try:
        stats = await llm_manager.get_usage_statistics(
            user_id=str(current_user["_id"]),
            days=days
        )
        
        if "error" in stats:
            raise Exception(stats["error"])
        
        return UsageStatistics(
            period_days=stats["period_days"],
            user_id=stats["user_id"],
            providers=stats["providers"],
            generated_at=stats["generated_at"]
        )
        
    except Exception as e:
        logger.error(f"Failed to get usage statistics: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get usage statistics"
        )

@app.get("/api/v1/llm/health")
async def check_llm_health(current_user: dict = Depends(get_current_user)):
    """Check health status of all LLM providers"""
    if not llm_manager:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="LLM Manager not available"
        )
    
    try:
        health_status = {}
        
        # Check Ollama health
        ollama_healthy = await llm_manager._check_ollama_health()
        health_status["ollama"] = {
            "status": "healthy" if ollama_healthy else "unhealthy",
            "provider": "ollama",
            "cost": "free"
        }
        
        # Check Groq health
        groq_healthy = llm_manager.groq_client is not None
        health_status["groq"] = {
            "status": "healthy" if groq_healthy else "unhealthy",
            "provider": "groq",
            "cost": "paid"
        }
        
        return {
            "timestamp": datetime.utcnow(),
            "providers": health_status,
            "overall_status": "healthy" if any(
                provider["status"] == "healthy" 
                for provider in health_status.values()
            ) else "unhealthy"
        }
        
    except Exception as e:
        logger.error(f"Failed to check LLM health: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to check LLM health"
        )

# ================================
# Enhanced Content Generation with LLM
# ================================

@app.post("/api/v1/content/generate")
async def generate_content_with_ai(
    platform: str,
    content_type: str,
    topic: str,
    target_audience: Optional[str] = None,
    tone: str = "professional",
    hashtag_count: int = 5,
    current_user: dict = Depends(get_current_user)
):
    """Generate AI-powered content for social media platforms"""
    if not llm_manager:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="LLM Manager not available"
        )
    
    try:
        # Build content generation prompt
        user_niche = current_user.get("niche", "general")
        user_audience = target_audience or current_user.get("target_audience", "general audience")
        
        prompt = f"""Create a {tone} {content_type} post for {platform} about "{topic}".

Target Audience: {user_audience}
Niche: {user_niche}
Platform: {platform}
Content Type: {content_type}
Tone: {tone}

Requirements:
- Write engaging content optimized for {platform}
- Include {hashtag_count} relevant hashtags
- Target the {user_audience} audience
- Keep the {tone} tone throughout
- Make it suitable for {content_type} format

Format your response as:
Content: [Your main content here]
Hashtags: [List of hashtags separated by spaces]
"""
        
        # Generate content using LLM
        response = await llm_manager.generate_content(
            prompt=prompt,
            task_type=TaskType.CONTENT_GENERATION,
            max_tokens=800,
            temperature=0.8,
            user_id=str(current_user["_id"])
        )
        
        # Parse the generated content
        content_lines = response.content.split('\n')
        main_content = ""
        hashtags = []
        
        for line in content_lines:
            if line.startswith("Content:"):
                main_content = line.replace("Content:", "").strip()
            elif line.startswith("Hashtags:"):
                hashtag_text = line.replace("Hashtags:", "").strip()
                hashtags = [tag.strip() for tag in hashtag_text.split() if tag.startswith('#')]
        
        # If parsing fails, use the raw content
        if not main_content:
            main_content = response.content
            # Extract hashtags from content if present
            import re
            hashtags = re.findall(r'#\w+', main_content)
        
        # Create content entry in database
        content_dict = {
            "_id": ObjectId(),
            "user_id": str(current_user["_id"]),
            "title": f"AI Generated: {topic}",
            "content_type": content_type,
            "platform": platform,
            "text_content": main_content,
            "hashtags": hashtags[:hashtag_count],  # Limit to requested count
            "status": "draft",
            "quality_score": 0.8,  # Default AI quality score
            "viral_potential": 0.6,  # Default viral potential
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow(),
            "performance_metrics": {},
            "ai_generated": True,
            "generation_metadata": {
                "provider": response.provider,
                "model": response.model,
                "tokens_used": response.tokens_used,
                "cost": response.cost,
                "generation_time": response.response_time
            }
        }
        
        # Save to database
        result = await database.contents.insert_one(content_dict)
        content_dict = convert_objectid_to_str(content_dict)
        
        return {
            "content": ContentResponse(**content_dict),
            "generation_info": {
                "provider": response.provider,
                "model": response.model,
                "tokens_used": response.tokens_used,
                "cost": response.cost,
                "response_time": response.response_time
            }
        }
        
    except Exception as e:
        logger.error(f"AI content generation failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"AI content generation failed: {str(e)}"
        )

async def create_initial_success_journey(user_id: str, goals: Optional[dict] = None):
    """Create initial success journey for a new user."""
    journey_dict = {
        "_id": ObjectId(),
        "user_id": user_id,
        "current_phase": "onboarding",
        "milestones_completed": [],
        "daily_actions": [],
        "blockers_identified": [],
        "coach_sessions": 0,
        "progress_score": 0.0,
        "success_probability": 0.5,
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow()
    }
    
    if goals:
        journey_dict["success_goals"] = goals
    
    try:
        await database.success_journeys.insert_one(journey_dict)
        logger.info(f"Created initial success journey for user {user_id}")
    except Exception as e:
        logger.error(f"Failed to create success journey for user {user_id}: {e}")

# ================================
# Error Handlers
# ================================

@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    """Handle HTTP exceptions."""
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": exc.detail,
            "status_code": exc.status_code,
            "timestamp": datetime.utcnow().isoformat()
        }
    )

@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    """Handle general exceptions."""
    logger.error(f"Unhandled exception: {exc}")
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal server error",
            "status_code": 500,
            "timestamp": datetime.utcnow().isoformat()
        }
    )

if __name__ == "__main__":
    uvicorn.run(
        "server:app",
        host="0.0.0.0",
        port=8001,
        reload=True,
        log_level="info"
    )