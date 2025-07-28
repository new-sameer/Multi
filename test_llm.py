#!/usr/bin/env python3
"""
Test script for LLM integration - Testing Ollama and Groq
"""

import asyncio
import httpx
from motor.motor_asyncio import AsyncIOMotorClient
import sys
import os

# Add backend to path
sys.path.append('/app/backend')

from services.llm_manager import UniversalLLMManager, TaskType

async def test_llm_integration():
    """Test the LLM integration"""
    print("🚀 Testing Universal LLM Manager...")
    
    # Initialize database connection
    MONGO_URL = "mongodb://localhost:27017/socialmedia_automation"
    client = AsyncIOMotorClient(MONGO_URL)
    database = client.get_default_database()
    
    # Initialize LLM Manager
    llm_manager = UniversalLLMManager(database)
    
    # Test 1: Check available models
    print("\n📋 Getting available models...")
    try:
        models = await llm_manager.get_available_models()
        print(f"Found {len(models)} available models:")
        for model in models:
            print(f"  - {model.name} ({model.provider}) - Available: {model.available}")
    except Exception as e:
        print(f"❌ Failed to get models: {e}")
    
    # Test 2: Check LLM health
    print("\n🏥 Checking LLM provider health...")
    try:
        ollama_health = await llm_manager._check_ollama_health()
        print(f"  Ollama: {'✅ Healthy' if ollama_health else '❌ Unhealthy'}")
        
        groq_health = llm_manager.groq_client is not None
        print(f"  Groq: {'✅ Healthy' if groq_health else '❌ Unhealthy'}")
    except Exception as e:
        print(f"❌ Health check failed: {e}")
    
    # Test 3: Generate content with Groq (most likely to work)
    print("\n✨ Testing content generation with Groq...")
    try:
        response = await llm_manager.generate_content(
            prompt="Write a short, engaging Instagram post about productivity tips.",
            task_type=TaskType.CONTENT_GENERATION,
            preferred_provider=None,  # Let it choose the best
            max_tokens=200,
            temperature=0.7
        )
        
        print(f"✅ Generation successful!")
        print(f"  Provider: {response.provider}")
        print(f"  Model: {response.model}")
        print(f"  Tokens: {response.tokens_used}")
        print(f"  Time: {response.response_time:.2f}s")
        print(f"  Cost: ${response.cost:.4f}")
        print(f"  Content: {response.content[:200]}...")
        
    except Exception as e:
        print(f"❌ Content generation failed: {e}")
    
    # Test 4: Get usage statistics
    print("\n📊 Getting usage statistics...")
    try:
        stats = await llm_manager.get_usage_statistics(days=1)
        print(f"✅ Stats retrieved: {len(stats.get('providers', []))} provider(s) used")
    except Exception as e:
        print(f"❌ Stats retrieval failed: {e}")
    
    # Cleanup
    client.close()
    print("\n🎉 LLM integration test completed!")

if __name__ == "__main__":
    asyncio.run(test_llm_integration())