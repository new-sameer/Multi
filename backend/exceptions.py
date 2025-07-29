#!/usr/bin/env python3
"""
Custom exception classes for the Social Media Automation Platform
Centralized error handling and custom exceptions
"""

from typing import Any, Dict, Optional
from fastapi import HTTPException, status

class BaseAPIException(HTTPException):
    """Base exception class for API errors"""
    
    def __init__(
        self, 
        status_code: int, 
        message: str, 
        details: Optional[Dict[str, Any]] = None
    ):
        self.message = message
        self.details = details or {}
        super().__init__(status_code=status_code, detail=message)

class AuthenticationError(BaseAPIException):
    """Authentication related errors"""
    
    def __init__(self, message: str = "Authentication failed", details: Optional[Dict[str, Any]] = None):
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            message=message,
            details=details
        )

class AuthorizationError(BaseAPIException):
    """Authorization related errors"""
    
    def __init__(self, message: str = "Access denied", details: Optional[Dict[str, Any]] = None):
        super().__init__(
            status_code=status.HTTP_403_FORBIDDEN,
            message=message,
            details=details
        )

class ValidationError(BaseAPIException):
    """Input validation errors"""
    
    def __init__(self, message: str = "Validation failed", details: Optional[Dict[str, Any]] = None):
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            message=message,
            details=details
        )

class NotFoundError(BaseAPIException):
    """Resource not found errors"""
    
    def __init__(self, message: str = "Resource not found", details: Optional[Dict[str, Any]] = None):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            message=message,
            details=details
        )

class ConflictError(BaseAPIException):
    """Resource conflict errors"""
    
    def __init__(self, message: str = "Resource conflict", details: Optional[Dict[str, Any]] = None):
        super().__init__(
            status_code=status.HTTP_409_CONFLICT,
            message=message,
            details=details
        )

class ServiceUnavailableError(BaseAPIException):
    """Service unavailable errors"""
    
    def __init__(self, message: str = "Service temporarily unavailable", details: Optional[Dict[str, Any]] = None):
        super().__init__(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            message=message,
            details=details
        )

class RateLimitError(BaseAPIException):
    """Rate limiting errors"""
    
    def __init__(self, message: str = "Rate limit exceeded", details: Optional[Dict[str, Any]] = None):
        super().__init__(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            message=message,
            details=details
        )

class DatabaseError(BaseAPIException):
    """Database operation errors"""
    
    def __init__(self, message: str = "Database operation failed", details: Optional[Dict[str, Any]] = None):
        super().__init__(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            message=message,
            details=details
        )

class LLMError(BaseAPIException):
    """LLM service errors"""
    
    def __init__(self, message: str = "LLM service error", details: Optional[Dict[str, Any]] = None):
        super().__init__(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            message=message,
            details=details
        )

class ContentGenerationError(LLMError):
    """Content generation specific errors"""
    
    def __init__(self, message: str = "Content generation failed", details: Optional[Dict[str, Any]] = None):
        super().__init__(message=message, details=details)

class UserNotFoundError(NotFoundError):
    """User not found error"""
    
    def __init__(self, user_id: str = None):
        message = f"User {user_id} not found" if user_id else "User not found"
        super().__init__(message=message)

class ContentNotFoundError(NotFoundError):
    """Content not found error"""
    
    def __init__(self, content_id: str = None):
        message = f"Content {content_id} not found" if content_id else "Content not found"
        super().__init__(message=message)

class InvalidCredentialsError(AuthenticationError):
    """Invalid credentials error"""
    
    def __init__(self):
        super().__init__(message="Incorrect email or password")

class TokenExpiredError(AuthenticationError):
    """Token expired error"""
    
    def __init__(self):
        super().__init__(message="Token has expired")

class UserAlreadyExistsError(ConflictError):
    """User already exists error"""
    
    def __init__(self, email: str):
        super().__init__(message=f"User with email {email} already exists")