#!/usr/bin/env python3
"""
Main FastAPI application
Modular Social Media Automation Platform with best practices
"""

import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.responses import JSONResponse
from datetime import datetime

# Import configuration and database
from config import get_settings
from database import db_manager, health_check

# Import middleware
from middleware.cors import setup_cors
from middleware.logging import LoggingMiddleware, SecurityHeadersMiddleware
from middleware.rate_limiting import RateLimitingMiddleware

# Import error handlers
from error_handlers import setup_error_handlers

# Import routers
from routers.auth import router as auth_router
from routers.users import router as users_router
from routers.content import router as content_router
from routers.llm import router as llm_router, set_llm_manager
from routers.ollama import router as ollama_router
from routers.providers import router as providers_router

# Import services
from services.llm_manager import UniversalLLMManager

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Get settings
settings = get_settings()

# Global LLM Manager instance
llm_manager: UniversalLLMManager = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager for startup and shutdown events."""
    global llm_manager
    
    # Startup
    try:
        logger.info("Starting Social Media Automation Platform...")
        
        # Connect to database
        database = await db_manager.connect()
        logger.info("Database connected successfully")
        
        # Initialize LLM Manager
        llm_manager = UniversalLLMManager(database)
        set_llm_manager(llm_manager)
        logger.info("LLM Manager initialized successfully")
        
        logger.info("Application startup completed successfully")
        
        yield
        
    except Exception as e:
        logger.error(f"Failed to start application: {e}")
        raise
    finally:
        # Shutdown
        try:
            await db_manager.disconnect()
            logger.info("Application shutdown completed")
        except Exception as e:
            logger.error(f"Error during shutdown: {e}")

# Create FastAPI application
app = FastAPI(
    title="Social Media Automation Platform API",
    description="AI-powered social media automation with success coaching and affiliate marketing",
    version="1.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    openapi_url="/api/openapi.json",
    lifespan=lifespan
)

# Setup middleware
setup_cors(app)
app.add_middleware(LoggingMiddleware)
app.add_middleware(SecurityHeadersMiddleware)

# Add rate limiting middleware if not in development
if settings.ENVIRONMENT != "development":
    app.add_middleware(RateLimitingMiddleware)

# Setup error handlers
setup_error_handlers(app)

# Include routers
app.include_router(auth_router)
app.include_router(users_router)
app.include_router(content_router)
app.include_router(llm_router)

# Health check endpoint
@app.get("/api/health")
async def health_check_endpoint():
    """Health check endpoint for monitoring and load balancer"""
    try:
        # Check database health
        db_healthy = await health_check()
        
        # Check LLM manager health (if available)
        llm_healthy = False
        llm_status = {}
        
        if llm_manager:
            try:
                # Get comprehensive provider health
                provider_health = await llm_manager.get_provider_health_status()
                llm_status = provider_health["providers"]
                llm_healthy = provider_health["overall_status"] == "healthy"
                
            except Exception as e:
                logger.warning(f"LLM health check failed: {e}")
                llm_status = {"error": str(e)}
        
        # Determine overall health
        overall_healthy = db_healthy and (llm_healthy or settings.ENVIRONMENT == "development")
        
        response = {
            "status": "healthy" if overall_healthy else "unhealthy",
            "timestamp": datetime.utcnow().isoformat(),
            "version": "1.0.0",
            "environment": settings.ENVIRONMENT,
            "services": {
                "database": "connected" if db_healthy else "disconnected",
                "llm_manager": "available" if llm_manager else "unavailable",
                "llm_providers": llm_status
            }
        }
        
        status_code = 200 if overall_healthy else 503
        
        return JSONResponse(
            status_code=status_code,
            content=response
        )
        
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return JSONResponse(
            status_code=503,
            content={
                "status": "unhealthy",
                "timestamp": datetime.utcnow().isoformat(),
                "error": str(e)
            }
        )

# Root endpoint
@app.get("/")
async def root():
    """Root endpoint with API information"""
    return {
        "name": "Social Media Automation Platform API",
        "version": "1.0.0",
        "description": "AI-powered social media automation platform",
        "docs": "/api/docs",
        "health": "/api/health",
        "status": "running",
        "timestamp": datetime.utcnow().isoformat()
    }

# API information endpoint
@app.get("/api")
async def api_info():
    """API information and available endpoints"""
    return {
        "name": "Social Media Automation Platform API",
        "version": "1.0.0",
        "endpoints": {
            "authentication": "/api/v1/auth",
            "users": "/api/v1/users", 
            "content": "/api/v1/content",
            "llm": "/api/v1/llm",
            "health": "/api/health",
            "docs": "/api/docs"
        },
        "features": [
            "JWT Authentication",
            "User Management",
            "Content Creation & Management", 
            "AI Content Generation",
            "Universal LLM Support (Ollama + Cloud providers)",
            "Success Goals & Analytics",
            "Rate Limiting & Security"
        ],
        "timestamp": datetime.utcnow().isoformat()
    }

if __name__ == "__main__":
    import uvicorn
    
    logger.info(f"Starting server in {settings.ENVIRONMENT} mode...")
    
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8001,
        reload=settings.DEBUG,
        log_level=settings.LOG_LEVEL.lower(),
        access_log=True
    )