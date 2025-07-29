#!/usr/bin/env python3
"""
Error handlers for the FastAPI application
Centralized exception handling and error responses
"""

import logging
from datetime import datetime
from fastapi import Request, HTTPException
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException

from exceptions import BaseAPIException

logger = logging.getLogger(__name__)

async def base_api_exception_handler(request: Request, exc: BaseAPIException) -> JSONResponse:
    """
    Handle custom API exceptions
    
    Args:
        request: HTTP request
        exc: Custom API exception
        
    Returns:
        JSONResponse: Error response
    """
    error_response = {
        "error": exc.message,
        "status_code": exc.status_code,
        "timestamp": datetime.utcnow().isoformat(),
        "path": str(request.url)
    }
    
    # Include additional details if present
    if exc.details:
        error_response["details"] = exc.details
    
    # Include request ID if available
    if hasattr(request.state, "request_id"):
        error_response["request_id"] = request.state.request_id
    
    logger.warning(f"API Exception: {exc.message}", extra={
        "status_code": exc.status_code,
        "path": str(request.url),
        "details": exc.details
    })
    
    return JSONResponse(
        status_code=exc.status_code,
        content=error_response
    )

async def http_exception_handler(request: Request, exc: HTTPException) -> JSONResponse:
    """
    Handle FastAPI HTTP exceptions
    
    Args:
        request: HTTP request
        exc: HTTP exception
        
    Returns:
        JSONResponse: Error response
    """
    error_response = {
        "error": exc.detail,
        "status_code": exc.status_code,
        "timestamp": datetime.utcnow().isoformat(),
        "path": str(request.url)
    }
    
    # Include request ID if available
    if hasattr(request.state, "request_id"):
        error_response["request_id"] = request.state.request_id
    
    logger.warning(f"HTTP Exception: {exc.detail}", extra={
        "status_code": exc.status_code,
        "path": str(request.url)
    })
    
    return JSONResponse(
        status_code=exc.status_code,
        content=error_response,
        headers=getattr(exc, "headers", None)
    )

async def starlette_http_exception_handler(request: Request, exc: StarletteHTTPException) -> JSONResponse:
    """
    Handle Starlette HTTP exceptions
    
    Args:
        request: HTTP request
        exc: Starlette HTTP exception
        
    Returns:
        JSONResponse: Error response
    """
    error_response = {
        "error": exc.detail,
        "status_code": exc.status_code,
        "timestamp": datetime.utcnow().isoformat(),
        "path": str(request.url)
    }
    
    # Include request ID if available
    if hasattr(request.state, "request_id"):
        error_response["request_id"] = request.state.request_id
    
    logger.warning(f"Starlette HTTP Exception: {exc.detail}", extra={
        "status_code": exc.status_code,
        "path": str(request.url)
    })
    
    return JSONResponse(
        status_code=exc.status_code,
        content=error_response
    )

async def validation_exception_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
    """
    Handle Pydantic validation errors
    
    Args:
        request: HTTP request
        exc: Validation error
        
    Returns:
        JSONResponse: Error response
    """
    # Format validation errors for better user experience
    formatted_errors = []
    for error in exc.errors():
        field_path = " -> ".join(str(loc) for loc in error["loc"])
        formatted_errors.append({
            "field": field_path,
            "message": error["msg"],
            "type": error["type"]
        })
    
    error_response = {
        "error": "Validation failed",
        "status_code": 422,
        "timestamp": datetime.utcnow().isoformat(),
        "path": str(request.url),
        "validation_errors": formatted_errors
    }
    
    # Include request ID if available
    if hasattr(request.state, "request_id"):
        error_response["request_id"] = request.state.request_id
    
    logger.warning(f"Validation Error: {len(formatted_errors)} validation errors", extra={
        "path": str(request.url),
        "errors": formatted_errors
    })
    
    return JSONResponse(
        status_code=422,
        content=error_response
    )

async def general_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """
    Handle unexpected exceptions
    
    Args:
        request: HTTP request
        exc: Unexpected exception
        
    Returns:
        JSONResponse: Error response
    """
    error_response = {
        "error": "Internal server error",
        "status_code": 500,
        "timestamp": datetime.utcnow().isoformat(),
        "path": str(request.url),
        "type": type(exc).__name__
    }
    
    # Include request ID if available
    if hasattr(request.state, "request_id"):
        error_response["request_id"] = request.state.request_id
    
    # Include error details in development mode
    from config import get_settings
    settings = get_settings()
    if settings.DEBUG:
        error_response["debug_info"] = {
            "exception_type": type(exc).__name__,
            "exception_message": str(exc)
        }
    
    logger.error(f"Unhandled exception: {exc}", extra={
        "path": str(request.url),
        "exception_type": type(exc).__name__
    }, exc_info=True)
    
    return JSONResponse(
        status_code=500,
        content=error_response
    )

def setup_error_handlers(app):
    """
    Setup error handlers for the FastAPI application
    
    Args:
        app: FastAPI application instance
    """
    # Custom API exceptions
    app.add_exception_handler(BaseAPIException, base_api_exception_handler)
    
    # FastAPI HTTP exceptions
    app.add_exception_handler(HTTPException, http_exception_handler)
    
    # Starlette HTTP exceptions
    app.add_exception_handler(StarletteHTTPException, starlette_http_exception_handler)
    
    # Pydantic validation errors
    app.add_exception_handler(RequestValidationError, validation_exception_handler)
    
    # General exceptions (catch-all)
    app.add_exception_handler(Exception, general_exception_handler)
    
    logger.info("Error handlers configured successfully")