#!/usr/bin/env python3
"""
CORS middleware configuration
Cross-Origin Resource Sharing setup for the API
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from config import get_settings

settings = get_settings()

def setup_cors(app: FastAPI) -> None:
    """
    Setup CORS middleware for the FastAPI application
    
    Args:
        app: FastAPI application instance
    """
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.CORS_ORIGINS,
        allow_credentials=True,
        allow_methods=["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS"],
        allow_headers=[
            "Accept",
            "Accept-Language",
            "Content-Language",
            "Content-Type",
            "Authorization",
            "X-Requested-With",
            "X-Request-ID",
        ],
        expose_headers=[
            "X-Request-ID",
            "X-RateLimit-Remaining",
            "X-RateLimit-Reset",
        ]
    )