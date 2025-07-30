#!/usr/bin/env python3
"""
Ollama management router
API endpoints for Ollama model management and optimization
"""

import logging
from typing import Optional, List, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status
from motor.motor_asyncio import AsyncIOMotorDatabase

from database import get_database
from dependencies import get_current_user
from services.llm_service import LLMService
from services.llm_manager import UniversalLLMManager
from models.ollama import (
    OllamaModelInstallRequest, OllamaModelResponse, OllamaSystemInfo,
    ModelOptimizationRequest, OllamaHealthCheck
)
from exceptions import LLMError, ValidationError

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/ollama", tags=["ollama"])

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

@router.get("/health", response_model=OllamaHealthCheck)
async def check_ollama_health(
    current_user: dict = Depends(get_current_user),
    llm_service: LLMService = Depends(get_llm_service)
):
    """Check Ollama service health and status"""
    try:
        health_data = await llm_service.check_llm_health()
        ollama_status = health_data["providers"].get("ollama", {})
        
        return OllamaHealthCheck(
            status=ollama_status.get("status", "unknown"),
            connection=ollama_status.get("connection", "unknown"),
            models_available=ollama_status.get("models_available", 0),
            error=ollama_status.get("error")
        )
        
    except Exception as e:
        logger.error(f"Failed to check Ollama health: {e}")
        return OllamaHealthCheck(
            status="error",
            connection="failed",
            models_available=0,
            error=str(e)
        )

@router.get("/models/available", response_model=List[OllamaModelResponse])
async def get_available_models(
    current_user: dict = Depends(get_current_user),
    llm_service: LLMService = Depends(get_llm_service)
):
    """Get list of available Ollama models for installation"""
    try:
        # Get predefined model configurations
        available_models = [
            OllamaModelResponse(
                name="llama3.1:8b",
                size_gb=4.7,
                description="Fast 8B parameter Llama 3.1 model",
                capabilities=["general", "content_generation", "coaching"],
                installed=False,
                recommended=True
            ),
            OllamaModelResponse(
                name="llama3.1:70b",
                size_gb=40.0,
                description="High-quality 70B parameter Llama 3.1 model",
                capabilities=["general", "content_generation", "coaching", "reasoning"],
                installed=False,
                recommended=False
            ),
            OllamaModelResponse(
                name="mistral-nemo",
                size_gb=7.1,
                description="Mistral Nemo 12B model with large context",
                capabilities=["general", "content_generation"],
                installed=False,
                recommended=True
            ),
            OllamaModelResponse(
                name="codellama:34b",
                size_gb=19.0,
                description="Code-focused Llama model",
                capabilities=["coding", "general"],
                installed=False,
                recommended=False
            ),
            OllamaModelResponse(
                name="phi3:mini",
                size_gb=2.3,
                description="Lightweight Microsoft Phi-3 model",
                capabilities=["general", "mobile"],
                installed=False,
                recommended=True
            )
        ]
        
        # Check which models are actually installed
        if llm_manager and await llm_manager._check_ollama_health():
            try:
                installed_models = await llm_manager.ollama_client.list()
                installed_names = [model["name"] for model in installed_models.get("models", [])]
                
                for model in available_models:
                    if model.name in installed_names:
                        model.installed = True
                        
            except Exception as e:
                logger.warning(f"Failed to get installed models: {e}")
        
        return available_models
        
    except Exception as e:
        logger.error(f"Failed to get available models: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get available models"
        )

@router.get("/models/installed", response_model=List[OllamaModelResponse])
async def get_installed_models(
    current_user: dict = Depends(get_current_user),
    llm_service: LLMService = Depends(get_llm_service)
):
    """Get list of installed Ollama models"""
    try:
        if not llm_manager or not await llm_manager._check_ollama_health():
            return []
        
        installed_models = await llm_manager.ollama_client.list()
        model_list = []
        
        for model in installed_models.get("models", []):
            model_config = llm_manager.model_configs["ollama"].get(model["name"], {})
            
            model_list.append(OllamaModelResponse(
                name=model["name"],
                size_gb=model.get("size", 0) / (1024**3),
                description=f"Installed {model['name']} model",
                capabilities=model_config.get("capabilities", ["general"]),
                installed=True,
                recommended=model["name"] in ["llama3.1:8b", "mistral-nemo", "phi3:mini"]
            ))
        
        return model_list
        
    except Exception as e:
        logger.error(f"Failed to get installed models: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get installed models"
        )

@router.post("/models/install")
async def install_model(
    request: OllamaModelInstallRequest,
    current_user: dict = Depends(get_current_user),
    llm_service: LLMService = Depends(get_llm_service)
):
    """Install an Ollama model"""
    try:
        if not llm_manager:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="LLM Manager not available"
            )
        
        if not await llm_manager._check_ollama_health():
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Ollama service not available"
            )
        
        # Check if model is already installed
        if await llm_manager._is_ollama_model_available(request.model_name):
            return {
                "message": f"Model {request.model_name} is already installed",
                "status": "already_installed"
            }
        
        # Install the model
        success = await llm_manager._install_ollama_model(request.model_name)
        
        if success:
            return {
                "message": f"Successfully installed model {request.model_name}",
                "status": "installed"
            }
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to install model {request.model_name}"
            )
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Model installation failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Model installation failed: {str(e)}"
        )

@router.delete("/models/{model_name}")
async def remove_model(
    model_name: str,
    current_user: dict = Depends(get_current_user),
    llm_service: LLMService = Depends(get_llm_service)
):
    """Remove an installed Ollama model"""
    try:
        if not llm_manager:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="LLM Manager not available"
            )
        
        if not await llm_manager._check_ollama_health():
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Ollama service not available"
            )
        
        # Check if model exists
        if not await llm_manager._is_ollama_model_available(model_name):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Model {model_name} not found"
            )
        
        # Remove the model
        try:
            await llm_manager.ollama_client.delete(model_name)
            
            return {
                "message": f"Successfully removed model {model_name}",
                "status": "removed"
            }
            
        except Exception as e:
            logger.error(f"Failed to remove model {model_name}: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to remove model {model_name}"
            )
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Model removal failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Model removal failed: {str(e)}"
        )

@router.get("/system/info", response_model=OllamaSystemInfo)
async def get_system_info(
    current_user: dict = Depends(get_current_user),
    llm_service: LLMService = Depends(get_llm_service)
):
    """Get Ollama system information"""
    try:
        if not llm_manager or not await llm_manager._check_ollama_health():
            return OllamaSystemInfo(
                status="unavailable",
                memory_available_gb=0,
                disk_space_gb=0,
                gpu_available=False,
                recommended_models=["llama3.1:8b", "phi3:mini"]
            )
        
        # Get basic system info (simplified for now)
        system_info = OllamaSystemInfo(
            status="healthy",
            memory_available_gb=8.0,  # Would query actual system resources
            disk_space_gb=50.0,  # Would query actual disk space
            gpu_available=False,  # Would detect GPU
            recommended_models=["llama3.1:8b", "mistral-nemo", "phi3:mini"]
        )
        
        return system_info
        
    except Exception as e:
        logger.error(f"Failed to get system info: {e}")
        return OllamaSystemInfo(
            status="error",
            memory_available_gb=0,
            disk_space_gb=0,
            gpu_available=False,
            recommended_models=[]
        )

@router.post("/models/optimize")
async def optimize_model_selection(
    request: ModelOptimizationRequest,
    current_user: dict = Depends(get_current_user),
    llm_service: LLMService = Depends(get_llm_service)
):
    """Get optimized model recommendations"""
    try:
        # Get system constraints
        system_info = await get_system_info(current_user, llm_service)
        
        # Model recommendations based on goals and system
        recommendations = []
        
        if request.optimization_goal == "speed":
            recommendations = [
                {"model": "phi3:mini", "reason": "Fastest inference, lowest resource usage"},
                {"model": "llama3.1:8b", "reason": "Good balance of speed and quality"}
            ]
        elif request.optimization_goal == "quality":
            if system_info.memory_available_gb >= 32:
                recommendations = [
                    {"model": "llama3.1:70b", "reason": "Highest quality responses"},
                    {"model": "mistral-nemo", "reason": "Large context, high quality"}
                ]
            else:
                recommendations = [
                    {"model": "llama3.1:8b", "reason": "Best quality for available resources"},
                    {"model": "mistral-nemo", "reason": "Good quality with efficient resource usage"}
                ]
        elif request.optimization_goal == "cost":
            recommendations = [
                {"model": "phi3:mini", "reason": "Minimal resource usage, completely free"},
                {"model": "llama3.1:8b", "reason": "Good performance per resource cost"}
            ]
        else:  # balanced
            recommendations = [
                {"model": "llama3.1:8b", "reason": "Best overall balance of speed, quality, and resource usage"},
                {"model": "mistral-nemo", "reason": "Good for longer contexts, balanced performance"}
            ]
        
        return {
            "optimization_goal": request.optimization_goal,
            "system_constraints": {
                "memory_gb": system_info.memory_available_gb,
                "gpu_available": system_info.gpu_available
            },
            "recommendations": recommendations
        }
        
    except Exception as e:
        logger.error(f"Model optimization failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Model optimization failed"
        )