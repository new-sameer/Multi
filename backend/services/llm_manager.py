#!/usr/bin/env python3
"""
Universal LLM Manager - Phase 2 Implementation
Handles Ollama (local) and Groq (cloud) integrations with intelligent fallback
"""

import os
import asyncio
import logging
from datetime import datetime, timedelta
from typing import Optional, Dict, List, Any, Union
from enum import Enum
from dataclasses import dataclass
import json

import httpx
import ollama
from groq import AsyncGroq
from motor.motor_asyncio import AsyncIOMotorDatabase
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

logger = logging.getLogger(__name__)

class LLMProvider(str, Enum):
    OLLAMA = "ollama"
    GROQ = "groq"

class TaskType(str, Enum):
    CONTENT_GENERATION = "content_generation"
    SUCCESS_COACHING = "success_coaching"
    CONTENT_ADAPTATION = "content_adaptation"
    GENERAL = "general"

@dataclass
class LLMResponse:
    content: str
    provider: str
    model: str
    tokens_used: int
    response_time: float
    cost: float
    quality_score: Optional[float] = None

@dataclass
class ModelInfo:
    name: str
    provider: str
    available: bool
    size_gb: Optional[float] = None
    context_length: Optional[int] = None
    capabilities: List[str] = None

class UniversalLLMManager:
    """Universal LLM Manager supporting Ollama (local) and Groq (cloud) providers"""
    
    def __init__(self, database: AsyncIOMotorDatabase):
        self.database = database
        
        # Initialize providers
        self.groq_client = None
        self.ollama_client = None
        
        # Configuration
        self.groq_api_key = os.environ.get("GROQ_API_KEY")
        self.ollama_base_url = os.environ.get("OLLAMA_BASE_URL", "http://localhost:11434")
        
        # Initialize clients
        self._initialize_clients()
        
        # Model configurations
        self.model_configs = {
            "ollama": {
                "llama3.1:8b": {
                    "context_length": 8192,
                    "capabilities": ["general", "content_generation", "coaching"],
                    "quality_score": 0.8,
                    "speed_score": 0.9
                },
                "llama3.1:70b": {
                    "context_length": 8192,
                    "capabilities": ["general", "content_generation", "coaching", "reasoning"],
                    "quality_score": 0.95,
                    "speed_score": 0.6
                },
                "mistral-nemo": {
                    "context_length": 128000,
                    "capabilities": ["general", "content_generation"],
                    "quality_score": 0.85,
                    "speed_score": 0.8
                }
            },
            "groq": {
                "llama3-8b-8192": {
                    "context_length": 8192,
                    "capabilities": ["general", "content_generation", "coaching"],
                    "cost_per_token": 0.00000005,
                    "quality_score": 0.8,
                    "speed_score": 0.95
                },
                "llama3-70b-8192": {
                    "context_length": 8192,
                    "capabilities": ["general", "content_generation", "coaching", "reasoning"],
                    "cost_per_token": 0.00000059,
                    "quality_score": 0.95,
                    "speed_score": 0.9
                },
                "mixtral-8x7b-32768": {
                    "context_length": 32768,
                    "capabilities": ["general", "content_generation", "reasoning"],
                    "cost_per_token": 0.00000024,
                    "quality_score": 0.9,
                    "speed_score": 0.92
                }
            }
        }
    
    def _initialize_clients(self):
        """Initialize LLM provider clients"""
        try:
            # Initialize Groq client
            if self.groq_api_key:
                self.groq_client = AsyncGroq(api_key=self.groq_api_key)
                logger.info("Groq client initialized successfully")
            else:
                logger.warning("Groq API key not found")
            
            # Initialize Ollama client
            try:
                self.ollama_client = ollama.AsyncClient(host=self.ollama_base_url)
                logger.info("Ollama client initialized successfully")
            except Exception as e:
                logger.warning(f"Failed to initialize Ollama client: {e}")
                
        except Exception as e:
            logger.error(f"Failed to initialize LLM clients: {e}")
    
    async def generate_content(
        self,
        prompt: str,
        task_type: TaskType = TaskType.GENERAL,
        preferred_provider: Optional[LLMProvider] = None,
        max_tokens: int = 1000,
        temperature: float = 0.7,
        user_id: Optional[str] = None
    ) -> LLMResponse:
        """Generate content with intelligent provider selection and fallback"""
        
        start_time = datetime.now()
        
        # Select optimal model
        selected_provider, selected_model = await self._select_optimal_model(
            task_type=task_type,
            preferred_provider=preferred_provider,
            prompt_length=len(prompt)
        )
        
        try:
            # Generate content based on provider
            if selected_provider == LLMProvider.OLLAMA:
                response = await self._generate_with_ollama(
                    prompt=prompt,
                    model=selected_model,
                    max_tokens=max_tokens,
                    temperature=temperature
                )
            elif selected_provider == LLMProvider.GROQ:
                response = await self._generate_with_groq(
                    prompt=prompt,
                    model=selected_model,
                    max_tokens=max_tokens,
                    temperature=temperature
                )
            else:
                raise ValueError(f"Unsupported provider: {selected_provider}")
            
            # Calculate metrics
            response_time = (datetime.now() - start_time).total_seconds()
            
            llm_response = LLMResponse(
                content=response["content"],
                provider=selected_provider.value,
                model=selected_model,
                tokens_used=response.get("tokens_used", 0),
                response_time=response_time,
                cost=response.get("cost", 0.0)
            )
            
            # Log usage
            await self._log_usage(
                user_id=user_id,
                provider=selected_provider.value,
                model=selected_model,
                task_type=task_type.value,
                tokens_used=llm_response.tokens_used,
                cost=llm_response.cost,
                response_time=response_time
            )
            
            return llm_response
            
        except Exception as e:
            logger.error(f"Failed to generate content with {selected_provider}: {e}")
            
            # Try fallback
            if selected_provider == LLMProvider.OLLAMA:
                logger.info("Falling back to Groq")
                return await self._fallback_to_groq(
                    prompt=prompt,
                    task_type=task_type,
                    max_tokens=max_tokens,
                    temperature=temperature,
                    user_id=user_id,
                    start_time=start_time
                )
            else:
                raise Exception(f"Content generation failed: {e}")
    
    async def _generate_with_ollama(
        self,
        prompt: str,
        model: str,
        max_tokens: int,
        temperature: float
    ) -> Dict[str, Any]:
        """Generate content using Ollama"""
        
        if not self.ollama_client:
            raise Exception("Ollama client not available")
        
        # Check if model is available
        if not await self._is_ollama_model_available(model):
            logger.info(f"Installing Ollama model: {model}")
            await self._install_ollama_model(model)
        
        try:
            response = await self.ollama_client.generate(
                model=model,
                prompt=prompt,
                options={
                    "num_predict": max_tokens,
                    "temperature": temperature,
                    "top_p": 0.9,
                    "stop": ["<|end|>", "<|endoftext|>"]
                }
            )
            
            return {
                "content": response["response"],
                "tokens_used": len(response["response"].split()) * 1.3,  # Approximate
                "cost": 0.0  # Free for local models
            }
            
        except Exception as e:
            logger.error(f"Ollama generation failed: {e}")
            raise
    
    async def _generate_with_groq(
        self,
        prompt: str,
        model: str,
        max_tokens: int,
        temperature: float
    ) -> Dict[str, Any]:
        """Generate content using Groq"""
        
        if not self.groq_client:
            raise Exception("Groq client not available")
        
        try:
            completion = await self.groq_client.chat.completions.create(
                messages=[
                    {"role": "user", "content": prompt}
                ],
                model=model,
                max_tokens=max_tokens,
                temperature=temperature,
                top_p=0.9
            )
            
            content = completion.choices[0].message.content
            tokens_used = completion.usage.total_tokens
            
            # Calculate cost
            model_config = self.model_configs["groq"].get(model, {})
            cost_per_token = model_config.get("cost_per_token", 0.0)
            cost = tokens_used * cost_per_token
            
            return {
                "content": content,
                "tokens_used": tokens_used,
                "cost": cost
            }
            
        except Exception as e:
            logger.error(f"Groq generation failed: {e}")
            raise
    
    async def _fallback_to_groq(
        self,
        prompt: str,
        task_type: TaskType,
        max_tokens: int,
        temperature: float,
        user_id: Optional[str],
        start_time: datetime
    ) -> LLMResponse:
        """Fallback to Groq when Ollama fails"""
        
        try:
            # Select best Groq model for task
            _, groq_model = await self._select_optimal_model(
                task_type=task_type,
                preferred_provider=LLMProvider.GROQ,
                prompt_length=len(prompt)
            )
            
            response = await self._generate_with_groq(
                prompt=prompt,
                model=groq_model,
                max_tokens=max_tokens,
                temperature=temperature
            )
            
            response_time = (datetime.now() - start_time).total_seconds()
            
            llm_response = LLMResponse(
                content=response["content"],
                provider=LLMProvider.GROQ.value,
                model=groq_model,
                tokens_used=response["tokens_used"],
                response_time=response_time,
                cost=response["cost"]
            )
            
            # Log fallback usage
            await self._log_usage(
                user_id=user_id,
                provider=LLMProvider.GROQ.value,
                model=groq_model,
                task_type=task_type.value,
                tokens_used=llm_response.tokens_used,
                cost=llm_response.cost,
                response_time=response_time,
                is_fallback=True
            )
            
            return llm_response
            
        except Exception as e:
            logger.error(f"Groq fallback also failed: {e}")
            raise Exception(f"All LLM providers failed: {e}")
    
    async def _select_optimal_model(
        self,
        task_type: TaskType,
        preferred_provider: Optional[LLMProvider],
        prompt_length: int
    ) -> tuple[LLMProvider, str]:
        """Select optimal model based on task type, availability, and performance"""
        
        # If preferred provider is specified, try to use it
        if preferred_provider:
            model = await self._get_best_model_for_provider(preferred_provider, task_type)
            if model:
                return preferred_provider, model
        
        # Check Ollama availability first (free)
        ollama_available = await self._check_ollama_health()
        if ollama_available:
            model = await self._get_best_model_for_provider(LLMProvider.OLLAMA, task_type)
            if model:
                return LLMProvider.OLLAMA, model
        
        # Fallback to Groq
        if self.groq_client:
            model = await self._get_best_model_for_provider(LLMProvider.GROQ, task_type)
            if model:
                return LLMProvider.GROQ, model
        
        # Default fallback
        return LLMProvider.GROQ, "llama3-8b-8192"
    
    async def _get_best_model_for_provider(
        self,
        provider: LLMProvider,
        task_type: TaskType
    ) -> Optional[str]:
        """Get the best model for a specific provider and task type"""
        
        provider_models = self.model_configs.get(provider.value, {})
        
        # Filter models by task capability
        suitable_models = []
        for model_name, config in provider_models.items():
            capabilities = config.get("capabilities", [])
            if task_type.value in capabilities or "general" in capabilities:
                suitable_models.append((model_name, config))
        
        if not suitable_models:
            return None
        
        # Sort by quality score (descending)
        suitable_models.sort(key=lambda x: x[1].get("quality_score", 0), reverse=True)
        
        # Return the best model
        return suitable_models[0][0]
    
    async def _check_ollama_health(self) -> bool:
        """Check if Ollama service is healthy"""
        if not self.ollama_client:
            return False
        
        try:
            # Try to list models to check connectivity
            await self.ollama_client.list()
            return True
        except Exception as e:
            logger.warning(f"Ollama health check failed: {e}")
            return False
    
    async def _is_ollama_model_available(self, model: str) -> bool:
        """Check if a specific Ollama model is available"""
        try:
            models = await self.ollama_client.list()
            model_names = [m["name"] for m in models.get("models", [])]
            return model in model_names
        except Exception:
            return False
    
    async def _install_ollama_model(self, model: str) -> bool:
        """Install an Ollama model"""
        try:
            await self.ollama_client.pull(model)
            logger.info(f"Successfully installed Ollama model: {model}")
            return True
        except Exception as e:
            logger.error(f"Failed to install Ollama model {model}: {e}")
            return False
    
    async def _log_usage(
        self,
        user_id: Optional[str],
        provider: str,
        model: str,
        task_type: str,
        tokens_used: int,
        cost: float,
        response_time: float,
        is_fallback: bool = False
    ):
        """Log LLM usage for analytics and billing"""
        
        usage_log = {
            "user_id": user_id,
            "provider": provider,
            "model": model,
            "task_type": task_type,
            "tokens_used": tokens_used,
            "cost": cost,
            "response_time": response_time,
            "is_fallback": is_fallback,
            "timestamp": datetime.utcnow()
        }
        
        try:
            await self.database.llm_usage_logs.insert_one(usage_log)
        except Exception as e:
            logger.error(f"Failed to log LLM usage: {e}")
    
    async def get_available_models(self) -> List[ModelInfo]:
        """Get list of available models across all providers"""
        
        models = []
        
        # Get Ollama models
        if await self._check_ollama_health():
            try:
                ollama_models = await self.ollama_client.list()
                for model in ollama_models.get("models", []):
                    model_config = self.model_configs["ollama"].get(model["name"], {})
                    models.append(ModelInfo(
                        name=model["name"],
                        provider="ollama",
                        available=True,
                        size_gb=model.get("size", 0) / (1024**3),
                        context_length=model_config.get("context_length"),
                        capabilities=model_config.get("capabilities", [])
                    ))
            except Exception as e:
                logger.error(f"Failed to get Ollama models: {e}")
        
        # Get Groq models (they're always available if we have API key)
        if self.groq_client:
            for model_name, config in self.model_configs["groq"].items():
                models.append(ModelInfo(
                    name=model_name,
                    provider="groq",
                    available=True,
                    context_length=config.get("context_length"),
                    capabilities=config.get("capabilities", [])
                ))
        
        return models
    
    async def get_usage_statistics(self, user_id: Optional[str] = None, days: int = 30) -> Dict[str, Any]:
        """Get LLM usage statistics"""
        
        # Build query
        query = {"timestamp": {"$gte": datetime.utcnow() - timedelta(days=days)}}
        if user_id:
            query["user_id"] = user_id
        
        try:
            # Aggregate usage data
            pipeline = [
                {"$match": query},
                {"$group": {
                    "_id": "$provider",
                    "total_tokens": {"$sum": "$tokens_used"},
                    "total_cost": {"$sum": "$cost"},
                    "total_requests": {"$sum": 1},
                    "avg_response_time": {"$avg": "$response_time"},
                    "fallback_count": {"$sum": {"$cond": ["$is_fallback", 1, 0]}}
                }}
            ]
            
            results = await self.database.llm_usage_logs.aggregate(pipeline).to_list(length=None)
            
            return {
                "period_days": days,
                "user_id": user_id,
                "providers": results,
                "generated_at": datetime.utcnow()
            }
            
        except Exception as e:
            logger.error(f"Failed to get usage statistics: {e}")
            return {"error": str(e)}