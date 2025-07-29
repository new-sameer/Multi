#!/usr/bin/env python3
"""
LLM router
API endpoints for LLM generation, model management, and AI content creation
"""

import logging
from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException, status, Query
from motor.motor_asyncio import AsyncIOMotorDatabase

from database import get_database
from dependencies import get_current_user, rate_limit_per_minute
from services.llm_service import LLMService
from services.llm_manager import UniversalLLMManager, TaskType, LLMProvider
from models.llm import (
    LLMGenerateRequest, LLMResponse, ModelInfo, UsageStatistics,
    AIContentRequest, AIContentResponse, LLMHealthCheck
)
from exceptions import LLMError, ContentGenerationError, ValidationError, ServiceUnavailableError

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/llm", tags=["llm"])

# This will be injected during app initialization
llm_manager: Optional[UniversalLLMManager] = None

def set_llm_manager(manager: UniversalLLMManager):
    """Set the LLM manager instance"""
    global llm_manager
    llm_manager = manager

def get_llm_service(
    database: AsyncIOMotorDatabase = Depends(get_database)
) -> LLMService:
    """Get LLM service instance"""
    if not llm_manager:
        raise ServiceUnavailableError("LLM Manager not available")
    
    return LLMService(database, llm_manager)

@router.post("/generate", response_model=LLMResponse)
async def generate_content_with_llm(
    request: LLMGenerateRequest,
    current_user: dict = Depends(rate_limit_per_minute),
    llm_service: LLMService = Depends(get_llm_service)
):
    """Generate content using the Universal LLM Manager"""
    try:
        # Convert string enums to proper enums
        task_type = TaskType(request.task_type)
        preferred_provider = LLMProvider(request.preferred_provider) if request.preferred_provider else None
        
        response = await llm_service.generate_content(
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
    except ValidationError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except LLMError as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"LLM generation failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Content generation failed"
        )

@router.get("/models", response_model=List[ModelInfo])
async def get_available_models(
    current_user: dict = Depends(get_current_user),
    llm_service: LLMService = Depends(get_llm_service)
):
    """Get list of available LLM models"""
    try:
        models = await llm_service.get_available_models()
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
    except LLMError as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Failed to get available models: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get available models"
        )

@router.get("/usage-statistics", response_model=UsageStatistics)
async def get_llm_usage_statistics(
    days: int = Query(default=30, ge=1, le=365),
    current_user: dict = Depends(get_current_user),
    llm_service: LLMService = Depends(get_llm_service)
):
    """Get LLM usage statistics for the current user"""
    try:
        stats = await llm_service.get_usage_statistics(
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
        
    except LLMError as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Failed to get usage statistics: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get usage statistics"
        )

@router.get("/health", response_model=LLMHealthCheck)
async def check_llm_health(
    current_user: dict = Depends(get_current_user),
    llm_service: LLMService = Depends(get_llm_service)
):
    """Check health status of all LLM providers"""
    try:
        health_data = await llm_service.check_llm_health()
        
        return LLMHealthCheck(
            timestamp=health_data["timestamp"],
            providers=health_data["providers"],
            overall_status=health_data["overall_status"]
        )
        
    except Exception as e:
        logger.error(f"Failed to check LLM health: {e}")
        # Return error status instead of raising exception
        from datetime import datetime
        return LLMHealthCheck(
            timestamp=datetime.utcnow(),
            providers={},
            overall_status="error"
        )

@router.post("/content/generate", response_model=AIContentResponse)
async def generate_ai_content(
    request: AIContentRequest,
    current_user: dict = Depends(rate_limit_per_minute),
    llm_service: LLMService = Depends(get_llm_service)
):
    """Generate AI-powered content for social media platforms"""
    try:
        result = await llm_service.generate_social_media_content(
            platform=request.platform,
            content_type=request.content_type,
            topic=request.topic,
            user_id=str(current_user["_id"]),
            target_audience=request.target_audience,
            tone=request.tone,
            hashtag_count=request.hashtag_count,
            save_to_library=True  # Always save to library for now
        )
        
        return AIContentResponse(
            content=result["content"],
            generation_info=result["generation_info"]
        )
        
    except ValidationError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except ContentGenerationError as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"AI content generation failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="AI content generation failed"
        )

@router.post("/content/generate-draft")
async def generate_content_draft(
    request: AIContentRequest,
    current_user: dict = Depends(rate_limit_per_minute),
    llm_service: LLMService = Depends(get_llm_service)
):
    """Generate content draft without saving to library"""
    try:
        result = await llm_service.generate_social_media_content(
            platform=request.platform,
            content_type=request.content_type,
            topic=request.topic,
            user_id=str(current_user["_id"]),
            target_audience=request.target_audience,
            tone=request.tone,
            hashtag_count=request.hashtag_count,
            save_to_library=False  # Don't save to library
        )
        
        return {
            "draft_content": result["parsed_content"],
            "generation_info": result["generation_info"]
        }
        
    except ValidationError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except ContentGenerationError as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Content draft generation failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Content draft generation failed"
        )

@router.get("/providers/status")
async def get_provider_status(
    current_user: dict = Depends(get_current_user),
    llm_service: LLMService = Depends(get_llm_service)
):
    """Get detailed status of all LLM providers"""
    try:
        health_data = await llm_service.check_llm_health()
        
        return {
            "providers": health_data["providers"],
            "recommendation": health_data.get("recommendation", "No recommendation available"),
            "last_checked": health_data["timestamp"]
        }
        
    except Exception as e:
        logger.error(f"Failed to get provider status: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get provider status"
        )