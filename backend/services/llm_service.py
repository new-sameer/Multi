#!/usr/bin/env python3
"""
LLM service wrapper
Enhanced wrapper around the Universal LLM Manager with additional business logic
"""

import logging
from datetime import datetime
from typing import Optional, Dict, Any, List
from bson import ObjectId
from motor.motor_asyncio import AsyncIOMotorDatabase

from services.llm_manager import UniversalLLMManager, TaskType, LLMProvider, LLMResponse, ModelInfo
from exceptions import LLMError, ContentGenerationError, ValidationError
from services.content_service import ContentService

logger = logging.getLogger(__name__)

class LLMService:
    """Enhanced LLM service with business logic"""
    
    def __init__(self, database: AsyncIOMotorDatabase, llm_manager: UniversalLLMManager):
        self.database = database
        self.llm_manager = llm_manager
        self.content_service = ContentService(database)
    
    async def generate_content(
        self,
        prompt: str,
        task_type: TaskType = TaskType.GENERAL,
        preferred_provider: Optional[LLMProvider] = None,
        max_tokens: int = 1000,
        temperature: float = 0.7,
        user_id: Optional[str] = None
    ) -> LLMResponse:
        """
        Generate content using LLM with enhanced error handling
        
        Args:
            prompt: Text prompt for generation
            task_type: Type of task for model selection
            preferred_provider: Preferred LLM provider
            max_tokens: Maximum tokens to generate
            temperature: Generation temperature
            user_id: User ID for usage tracking
            
        Returns:
            LLMResponse: Generated content response
            
        Raises:
            LLMError: If generation fails
            ValidationError: If input parameters are invalid
        """
        try:
            # Validate inputs
            if not prompt.strip():
                raise ValidationError("Prompt cannot be empty")
            
            if max_tokens < 50 or max_tokens > 4000:
                raise ValidationError("max_tokens must be between 50 and 4000")
            
            if temperature < 0.0 or temperature > 2.0:
                raise ValidationError("temperature must be between 0.0 and 2.0")
            
            # Generate content using LLM manager
            response = await self.llm_manager.generate_content(
                prompt=prompt,
                task_type=task_type,
                preferred_provider=preferred_provider,
                max_tokens=max_tokens,
                temperature=temperature,
                user_id=user_id
            )
            
            # Log successful generation
            logger.info(f"Content generated successfully using {response.provider}")
            
            return response
            
        except Exception as e:
            logger.error(f"LLM content generation failed: {e}")
            if isinstance(e, ValidationError):
                raise
            raise LLMError(f"Content generation failed: {str(e)}")
    
    async def generate_social_media_content(
        self,
        platform: str,
        content_type: str,
        topic: str,
        user_id: str,
        target_audience: Optional[str] = None,
        tone: str = "professional",
        hashtag_count: int = 5,
        save_to_library: bool = True
    ) -> Dict[str, Any]:
        """
        Generate AI-powered social media content
        
        Args:
            platform: Target social media platform
            content_type: Type of content to generate
            topic: Content topic
            user_id: User ID
            target_audience: Target audience description
            tone: Content tone
            hashtag_count: Number of hashtags to generate
            save_to_library: Whether to save content to user's library
            
        Returns:
            dict: Generated content and metadata
            
        Raises:
            ContentGenerationError: If content generation fails
            ValidationError: If input parameters are invalid
        """
        try:
            # Validate platform
            valid_platforms = ["instagram", "tiktok", "linkedin", "youtube", "twitter", "facebook"]
            if platform not in valid_platforms:
                raise ValidationError(f"Invalid platform. Must be one of: {valid_platforms}")
            
            # Validate content type
            valid_content_types = ["text", "image", "video", "carousel"]
            if content_type not in valid_content_types:
                raise ValidationError(f"Invalid content type. Must be one of: {valid_content_types}")
            
            # Validate tone
            valid_tones = ["professional", "casual", "funny", "inspiring", "educational"]
            if tone not in valid_tones:
                raise ValidationError(f"Invalid tone. Must be one of: {valid_tones}")
            
            # Get user information for personalization
            user = await self.database.users.find_one({"_id": ObjectId(user_id)})
            if not user:
                raise ValidationError("User not found")
            
            user_niche = user.get("niche", "general")
            user_audience = target_audience or user.get("target_audience", "general audience")
            
            # Build comprehensive prompt
            prompt = await self._build_content_prompt(
                platform=platform,
                content_type=content_type,
                topic=topic,
                niche=user_niche,
                audience=user_audience,
                tone=tone,
                hashtag_count=hashtag_count
            )
            
            # Generate content using LLM
            response = await self.generate_content(
                prompt=prompt,
                task_type=TaskType.CONTENT_GENERATION,
                max_tokens=800,
                temperature=0.8,
                user_id=user_id
            )
            
            # Parse the generated content
            parsed_content = await self._parse_generated_content(response.content)
            
            # Save to content library if requested
            content_data = None
            if save_to_library:
                content_data = await self.content_service.create_content(
                    user_id=user_id,
                    title=f"AI Generated: {topic}",
                    content_type=content_type,
                    platform=platform,
                    text_content=parsed_content["main_content"],
                    hashtags=parsed_content["hashtags"][:hashtag_count]
                )
                
                # Add AI generation metadata
                await self.database.contents.update_one(
                    {"_id": ObjectId(content_data["id"])},
                    {"$set": {
                        "ai_generated": True,
                        "generation_metadata": {
                            "provider": response.provider,
                            "model": response.model,
                            "tokens_used": response.tokens_used,
                            "cost": response.cost,
                            "generation_time": response.response_time,
                            "prompt_topic": topic,
                            "tone": tone,
                            "target_audience": user_audience
                        }
                    }}
                )
            
            return {
                "content": content_data,
                "parsed_content": parsed_content,
                "generation_info": {
                    "provider": response.provider,
                    "model": response.model,
                    "tokens_used": response.tokens_used,
                    "cost": response.cost,
                    "response_time": response.response_time,
                    "quality_score": response.quality_score
                }
            }
            
        except (ValidationError, ContentGenerationError):
            raise
        except Exception as e:
            logger.error(f"Social media content generation failed: {e}")
            raise ContentGenerationError(f"Failed to generate social media content: {str(e)}")
    
    async def get_available_models(self) -> List[ModelInfo]:
        """
        Get list of available LLM models
        
        Returns:
            list: Available models
            
        Raises:
            LLMError: If unable to get models
        """
        try:
            return await self.llm_manager.get_available_models()
        except Exception as e:
            logger.error(f"Failed to get available models: {e}")
            raise LLMError(f"Failed to get available models: {str(e)}")
    
    async def get_usage_statistics(
        self, 
        user_id: Optional[str] = None, 
        days: int = 30
    ) -> Dict[str, Any]:
        """
        Get LLM usage statistics
        
        Args:
            user_id: User ID for user-specific stats
            days: Number of days to include
            
        Returns:
            dict: Usage statistics
            
        Raises:
            LLMError: If unable to get statistics
        """
        try:
            return await self.llm_manager.get_usage_statistics(user_id=user_id, days=days)
        except Exception as e:
            logger.error(f"Failed to get usage statistics: {e}")
            raise LLMError(f"Failed to get usage statistics: {str(e)}")
    
    async def check_llm_health(self) -> Dict[str, Any]:
        """
        Check health status of all LLM providers
        
        Returns:
            dict: Health status information
        """
        try:
            health_status = {}
            
            # Check Ollama health
            ollama_healthy = await self.llm_manager._check_ollama_health()
            health_status["ollama"] = {
                "status": "healthy" if ollama_healthy else "unhealthy",
                "provider": "ollama",
                "cost": "free",
                "priority": 1
            }
            
            # Check Groq health
            groq_healthy = self.llm_manager.groq_client is not None
            health_status["groq"] = {
                "status": "healthy" if groq_healthy else "unhealthy",
                "provider": "groq",
                "cost": "paid",
                "priority": 2
            }
            
            # Determine overall status
            overall_status = "healthy" if any(
                provider["status"] == "healthy" 
                for provider in health_status.values()
            ) else "unhealthy"
            
            return {
                "timestamp": datetime.utcnow(),
                "providers": health_status,
                "overall_status": overall_status,
                "recommendation": self._get_health_recommendation(health_status)
            }
            
        except Exception as e:
            logger.error(f"Failed to check LLM health: {e}")
            return {
                "timestamp": datetime.utcnow(),
                "providers": {},
                "overall_status": "error",
                "error": str(e)
            }
    
    async def _build_content_prompt(
        self,
        platform: str,
        content_type: str,
        topic: str,
        niche: str,
        audience: str,
        tone: str,
        hashtag_count: int
    ) -> str:
        """
        Build a comprehensive prompt for content generation
        
        Args:
            platform: Target platform
            content_type: Content type
            topic: Content topic
            niche: User's niche
            audience: Target audience
            tone: Content tone
            hashtag_count: Number of hashtags
            
        Returns:
            str: Generated prompt
        """
        # Platform-specific guidelines
        platform_guidelines = {
            "instagram": "Use visual language, keep it engaging and authentic",
            "tiktok": "Make it trendy, fun, and shareable with a hook in the first 3 seconds",
            "linkedin": "Professional tone, valuable insights, industry-relevant content",
            "youtube": "Create compelling titles and descriptions that encourage engagement",
            "twitter": "Concise and impactful, use threading for longer content",
            "facebook": "Community-focused, encourage discussion and sharing"
        }
        
        # Content type specific instructions
        content_instructions = {
            "text": "Focus on compelling copy that drives engagement",
            "image": "Create descriptive text that complements visuals",
            "video": "Write engaging scripts with clear call-to-actions",
            "carousel": "Create a series of connected content pieces"
        }
        
        prompt = f"""Create a {tone} {content_type} post for {platform} about "{topic}".

Context:
- Target Audience: {audience}
- Niche: {niche}
- Platform: {platform}
- Content Type: {content_type}
- Tone: {tone}

Platform Guidelines: {platform_guidelines.get(platform, "Follow best practices for the platform")}
Content Instructions: {content_instructions.get(content_type, "Create engaging content")}

Requirements:
- Write engaging content optimized for {platform}
- Include {hashtag_count} relevant and trending hashtags
- Target the {audience} audience specifically
- Maintain a {tone} tone throughout
- Make it suitable for {content_type} format
- Include a clear call-to-action
- Ensure content is valuable and shareable

Format your response as:
CONTENT: [Your main content here]
HASHTAGS: [List of hashtags separated by spaces]
CTA: [Call-to-action suggestion]
HOOK: [Attention-grabbing opening line]

Make it compelling, authentic, and optimized for maximum engagement on {platform}."""
        
        return prompt
    
    async def _parse_generated_content(self, raw_content: str) -> Dict[str, Any]:
        """
        Parse generated content into structured format
        
        Args:
            raw_content: Raw generated content
            
        Returns:
            dict: Parsed content components
        """
        import re
        
        parsed = {
            "main_content": "",
            "hashtags": [],
            "cta": "",
            "hook": "",
            "raw_content": raw_content
        }
        
        lines = raw_content.split('\n')
        current_section = None
        
        for line in lines:
            line = line.strip()
            
            # Check for section headers
            if line.upper().startswith("CONTENT:"):
                current_section = "content"
                content = line.replace("CONTENT:", "", 1).strip()
                if content:
                    parsed["main_content"] = content
            elif line.upper().startswith("HASHTAGS:"):
                current_section = "hashtags"
                hashtag_text = line.replace("HASHTAGS:", "", 1).strip()
                if hashtag_text:
                    parsed["hashtags"] = [tag.strip() for tag in hashtag_text.split() if tag.startswith('#')]
            elif line.upper().startswith("CTA:"):
                current_section = "cta"
                cta = line.replace("CTA:", "", 1).strip()
                if cta:
                    parsed["cta"] = cta
            elif line.upper().startswith("HOOK:"):
                current_section = "hook"
                hook = line.replace("HOOK:", "", 1).strip()
                if hook:
                    parsed["hook"] = hook
            elif line and current_section:
                # Continue adding to current section
                if current_section == "content":
                    parsed["main_content"] += " " + line
                elif current_section == "hashtags" and line.startswith('#'):
                    parsed["hashtags"].extend([tag.strip() for tag in line.split() if tag.startswith('#')])
                elif current_section == "cta":
                    parsed["cta"] += " " + line
                elif current_section == "hook":
                    parsed["hook"] += " " + line
        
        # Fallback parsing if structured format wasn't used
        if not parsed["main_content"]:
            parsed["main_content"] = raw_content
            # Extract hashtags from content
            hashtags = re.findall(r'#\w+', raw_content)
            parsed["hashtags"] = hashtags
        
        # Clean up
        parsed["main_content"] = parsed["main_content"].strip()
        parsed["cta"] = parsed["cta"].strip()
        parsed["hook"] = parsed["hook"].strip()
        
        return parsed
    
    def _get_health_recommendation(self, health_status: Dict[str, Any]) -> str:
        """
        Get health recommendation based on provider status
        
        Args:
            health_status: Health status of providers
            
        Returns:
            str: Health recommendation
        """
        healthy_providers = [
            name for name, status in health_status.items() 
            if status["status"] == "healthy"
        ]
        
        if not healthy_providers:
            return "All LLM providers are down. Please check your configuration and network connectivity."
        elif len(healthy_providers) == 1:
            return f"Only {healthy_providers[0]} is available. Consider setting up backup providers."
        else:
            return "Multiple providers are healthy. System is operating normally."