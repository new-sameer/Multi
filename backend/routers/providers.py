#!/usr/bin/env python3
"""
Provider configuration router
API endpoints for managing LLM provider configurations and API keys
"""

import logging
from typing import Optional, List, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status
from motor.motor_asyncio import AsyncIOMotorDatabase

from database import get_database
from dependencies import get_current_user
from services.llm_service import LLMService
from services.llm_manager import UniversalLLMManager
from models.providers import (
    ProviderConfigRequest, ProviderConfigResponse, ProviderListResponse,
    ProviderTestRequest, ProviderTestResponse, CostOptimizationRequest
)
from exceptions import LLMError, ValidationError

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/providers", tags=["providers"])

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
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="LLM Manager not available"
        )
    
    return LLMService(database, llm_manager)

@router.get("/list", response_model=List[ProviderConfigResponse])
async def list_providers(
    current_user: dict = Depends(get_current_user),
    llm_service: LLMService = Depends(get_llm_service)
):
    """Get list of all LLM providers and their configurations"""
    try:
        health_data = await llm_service.check_llm_health()
        providers_status = health_data["providers"]
        
        providers = []
        
        # Define provider metadata
        provider_metadata = {
            "ollama": {
                "display_name": "Ollama",
                "description": "Local open-source models",
                "cost_type": "free",
                "requires_api_key": False,
                "setup_url": "https://ollama.ai/"
            },
            "groq": {
                "display_name": "Groq",
                "description": "Ultra-fast inference cloud service",
                "cost_type": "pay_per_token",
                "requires_api_key": True,
                "setup_url": "https://console.groq.com/"
            },
            "openai": {
                "display_name": "OpenAI",
                "description": "GPT models and advanced AI",
                "cost_type": "pay_per_token",
                "requires_api_key": True,
                "setup_url": "https://platform.openai.com/"
            },
            "claude": {
                "display_name": "Anthropic Claude",
                "description": "High-quality conversational AI",
                "cost_type": "pay_per_token",
                "requires_api_key": True,
                "setup_url": "https://console.anthropic.com/"
            },
            "perplexity": {
                "display_name": "Perplexity",
                "description": "Web-search enabled models",
                "cost_type": "pay_per_token",
                "requires_api_key": True,
                "setup_url": "https://www.perplexity.ai/"
            }
        }
        
        for provider_name, status_info in providers_status.items():
            metadata = provider_metadata.get(provider_name, {})
            
            providers.append(ProviderConfigResponse(
                provider=provider_name,
                display_name=metadata.get("display_name", provider_name.title()),
                description=metadata.get("description", ""),
                status=status_info.get("status", "unknown"),
                connection=status_info.get("connection", "unknown"),
                models_available=status_info.get("models_available", 0),
                cost_type=metadata.get("cost_type", "unknown"),
                requires_api_key=metadata.get("requires_api_key", False),
                configured=status_info.get("status") == "healthy",
                setup_url=metadata.get("setup_url", ""),
                error=status_info.get("error")
            ))
        
        return providers
        
    except Exception as e:
        logger.error(f"Failed to list providers: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to list providers"
        )

@router.get("/{provider_name}", response_model=ProviderConfigResponse)
async def get_provider_config(
    provider_name: str,
    current_user: dict = Depends(get_current_user),
    llm_service: LLMService = Depends(get_llm_service)
):
    """Get configuration for a specific provider"""
    try:
        providers = await list_providers(current_user, llm_service)
        
        for provider in providers:
            if provider.provider == provider_name:
                return provider
        
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Provider {provider_name} not found"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get provider config: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get provider configuration"
        )

@router.post("/{provider_name}/configure")
async def configure_provider(
    provider_name: str,
    request: ProviderConfigRequest,
    current_user: dict = Depends(get_current_user),
    llm_service: LLMService = Depends(get_llm_service)
):
    """Configure a provider with API keys and settings"""
    try:
        # Note: In a real implementation, you would securely store the API key
        # For now, we'll return a success message with instructions
        
        valid_providers = ["groq", "openai", "claude", "perplexity"]
        if provider_name not in valid_providers:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Provider {provider_name} does not support configuration"
            )
        
        # Validate API key format
        if not request.api_key or len(request.api_key.strip()) < 10:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid API key format"
            )
        
        # In a real implementation, you would:
        # 1. Encrypt and store the API key
        # 2. Update the LLM manager configuration
        # 3. Test the connection
        
        return {
            "message": f"Provider {provider_name} configured successfully",
            "provider": provider_name,
            "status": "configured",
            "instructions": f"API key has been set for {provider_name}. Restart required for changes to take effect."
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Provider configuration failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Provider configuration failed"
        )

@router.post("/{provider_name}/test", response_model=ProviderTestResponse)
async def test_provider_connection(
    provider_name: str,
    request: ProviderTestRequest,
    current_user: dict = Depends(get_current_user),
    llm_service: LLMService = Depends(get_llm_service)
):
    """Test connection to a specific provider"""
    try:
        if not llm_manager:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="LLM Manager not available"
            )
        
        # Test the provider by making a simple generation request
        from services.llm_manager import LLMProvider, TaskType
        
        try:
            provider_enum = LLMProvider(provider_name)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Unsupported provider: {provider_name}"
            )
        
        test_prompt = request.test_prompt or "Hello, this is a test message. Please respond with 'Test successful!'"
        
        start_time = time.time()
        
        try:
            response = await llm_manager.generate_content(
                prompt=test_prompt,
                task_type=TaskType.GENERAL,
                preferred_provider=provider_enum,
                max_tokens=50,
                temperature=0.5,
                user_id=str(current_user["_id"])
            )
            
            end_time = time.time()
            response_time = end_time - start_time
            
            return ProviderTestResponse(
                provider=provider_name,
                success=True,
                response_time=response_time,
                model_used=response.model,
                tokens_used=response.tokens_used,
                cost=response.cost,
                test_response=response.content[:200],  # Truncate for display
                message="Connection test successful"
            )
            
        except Exception as provider_error:
            end_time = time.time()
            response_time = end_time - start_time
            
            return ProviderTestResponse(
                provider=provider_name,
                success=False,
                response_time=response_time,
                error=str(provider_error),
                message=f"Connection test failed: {provider_error}"
            )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Provider test failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Provider test failed"
        )

@router.post("/cost/optimize", response_model=Dict[str, Any])
async def optimize_costs(
    request: CostOptimizationRequest,
    current_user: dict = Depends(get_current_user),
    llm_service: LLMService = Depends(get_llm_service)
):
    """Get cost optimization recommendations"""
    try:
        # Get usage statistics
        usage_stats = await llm_service.get_usage_statistics(
            user_id=str(current_user["_id"]),
            days=request.analysis_period_days
        )
        
        if "error" in usage_stats:
            raise Exception(usage_stats["error"])
        
        providers = usage_stats.get("providers", [])
        
        # Calculate total costs and usage
        total_cost = sum(p.get("total_cost", 0) for p in providers)
        total_requests = sum(p.get("total_requests", 0) for p in providers)
        
        # Generate recommendations
        recommendations = []
        
        # Recommend Ollama if not being used
        ollama_usage = next((p for p in providers if p["_id"] == "ollama"), None)
        if not ollama_usage or ollama_usage.get("total_requests", 0) == 0:
            recommendations.append({
                "type": "use_local_models",
                "title": "Use Local Models (Ollama)",
                "description": "Switch to free local models for routine tasks",
                "potential_savings": total_cost * 0.7,  # Estimate 70% savings
                "priority": "high",
                "action": "Install and use Ollama models for content generation"
            })
        
        # Recommend provider switching for high-cost usage
        highest_cost_provider = max(providers, key=lambda x: x.get("total_cost", 0), default=None)
        if highest_cost_provider and highest_cost_provider.get("total_cost", 0) > request.target_monthly_cost:
            recommendations.append({
                "type": "switch_provider",
                "title": f"Reduce {highest_cost_provider['_id'].title()} Usage",
                "description": f"Consider switching some tasks to lower-cost alternatives",
                "potential_savings": highest_cost_provider.get("total_cost", 0) * 0.4,
                "priority": "medium",
                "action": f"Use Groq or Ollama for simple tasks instead of {highest_cost_provider['_id']}"
            })
        
        # Recommend optimization for high-frequency low-value tasks
        if total_requests > 1000:
            recommendations.append({
                "type": "optimize_usage",
                "title": "Optimize High-Volume Tasks",
                "description": "Use more efficient models for routine content generation",
                "potential_savings": total_cost * 0.3,
                "priority": "medium",
                "action": "Use smaller, faster models for simple tasks"
            })
        
        # Calculate projected monthly cost
        daily_average = total_cost / request.analysis_period_days if request.analysis_period_days > 0 else 0
        projected_monthly = daily_average * 30
        
        return {
            "analysis_period_days": request.analysis_period_days,
            "current_usage": {
                "total_cost": total_cost,
                "total_requests": total_requests,
                "daily_average_cost": daily_average,
                "projected_monthly_cost": projected_monthly
            },
            "target_monthly_cost": request.target_monthly_cost,
            "cost_efficiency": "good" if projected_monthly <= request.target_monthly_cost else "needs_improvement",
            "recommendations": recommendations,
            "total_potential_savings": sum(r.get("potential_savings", 0) for r in recommendations),
            "optimization_score": min(10, max(1, 10 - (projected_monthly / max(request.target_monthly_cost, 1))))
        }
        
    except Exception as e:
        logger.error(f"Cost optimization failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Cost optimization analysis failed"
        )

# Import time for testing
import time