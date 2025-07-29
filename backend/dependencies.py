#!/usr/bin/env python3
"""
FastAPI dependencies for dependency injection
Centralized dependency management for authentication, database, etc.
"""

import jwt
from typing import Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from motor.motor_asyncio import AsyncIOMotorDatabase
from bson import ObjectId
from datetime import datetime

from config import get_settings
from database import get_database
from exceptions import AuthenticationError, UserNotFoundError

settings = get_settings()
security = HTTPBearer()

async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    database: AsyncIOMotorDatabase = Depends(get_database)
) -> dict:
    """
    Get the current authenticated user from JWT token
    
    Args:
        credentials: HTTP Bearer credentials
        database: Database connection
        
    Returns:
        dict: User document from database
        
    Raises:
        AuthenticationError: If token is invalid or user not found
    """
    token = credentials.credentials
    
    try:
        # Decode JWT token
        payload = jwt.decode(
            token, 
            settings.JWT_SECRET, 
            algorithms=[settings.JWT_ALGORITHM]
        )
        
        user_id: str = payload.get("sub")
        if user_id is None:
            raise AuthenticationError("Invalid token: missing user ID")
            
    except jwt.ExpiredSignatureError:
        raise AuthenticationError("Token has expired")
    except jwt.InvalidTokenError:
        raise AuthenticationError("Invalid token")
    
    # Get user from database
    try:
        user = await database.users.find_one({"_id": ObjectId(user_id)})
        if user is None:
            raise UserNotFoundError(user_id)
            
        # Update last active timestamp
        await database.users.update_one(
            {"_id": user["_id"]},
            {"$set": {"last_active": datetime.utcnow()}}
        )
        
        return user
        
    except Exception as e:
        if isinstance(e, (UserNotFoundError, AuthenticationError)):
            raise
        raise AuthenticationError(f"Database error: {str(e)}")

async def get_current_active_user(
    current_user: dict = Depends(get_current_user)
) -> dict:
    """
    Get current active user (can be extended to check for banned users, etc.)
    
    Args:
        current_user: Current user from get_current_user dependency
        
    Returns:
        dict: Active user document
        
    Raises:
        AuthenticationError: If user is inactive
    """
    # Add any additional checks for user status here
    # For now, just return the user as-is
    return current_user

async def get_optional_user(
    database: AsyncIOMotorDatabase = Depends(get_database),
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(HTTPBearer(auto_error=False))
) -> Optional[dict]:
    """
    Get the current user if authenticated, otherwise return None
    Useful for endpoints that work for both authenticated and anonymous users
    
    Args:
        database: Database connection
        credentials: Optional HTTP Bearer credentials
        
    Returns:
        Optional[dict]: User document if authenticated, None otherwise
    """
    if not credentials:
        return None
    
    try:
        return await get_current_user(credentials, database)
    except AuthenticationError:
        return None

async def verify_admin_user(
    current_user: dict = Depends(get_current_user)
) -> dict:
    """
    Verify that the current user has admin privileges
    
    Args:
        current_user: Current authenticated user
        
    Returns:
        dict: Admin user document
        
    Raises:
        AuthenticationError: If user is not an admin
    """
    user_role = current_user.get("role", "user")
    if user_role != "admin":
        raise AuthenticationError("Admin privileges required")
    
    return current_user

async def get_user_by_id(
    user_id: str,
    database: AsyncIOMotorDatabase = Depends(get_database)
) -> dict:
    """
    Get user by ID from database
    
    Args:
        user_id: User ID string
        database: Database connection
        
    Returns:
        dict: User document
        
    Raises:
        UserNotFoundError: If user doesn't exist
    """
    try:
        user = await database.users.find_one({"_id": ObjectId(user_id)})
        if user is None:
            raise UserNotFoundError(user_id)
        return user
    except Exception as e:
        if isinstance(e, UserNotFoundError):
            raise
        raise UserNotFoundError(user_id)

class PaginationParams:
    """Pagination parameters for list endpoints"""
    
    def __init__(
        self, 
        page: int = 1, 
        per_page: int = 20, 
        max_per_page: int = 100
    ):
        self.page = max(1, page)
        self.per_page = min(max(1, per_page), max_per_page)
        self.skip = (self.page - 1) * self.per_page
        self.limit = self.per_page

def get_pagination_params(
    page: int = 1,
    per_page: int = 20
) -> PaginationParams:
    """
    Get pagination parameters
    
    Args:
        page: Page number (1-based)
        per_page: Items per page
        
    Returns:
        PaginationParams: Pagination parameters
    """
    return PaginationParams(page=page, per_page=per_page)

# Rate limiting dependencies (placeholder for future implementation)
async def rate_limit_per_minute(
    current_user: dict = Depends(get_current_user)
) -> dict:
    """
    Rate limiting dependency - 60 requests per minute per user
    TODO: Implement actual rate limiting logic
    
    Args:
        current_user: Current authenticated user
        
    Returns:
        dict: User document
    """
    # Placeholder - implement Redis-based rate limiting
    return current_user

async def rate_limit_per_hour(
    current_user: dict = Depends(get_current_user)
) -> dict:
    """
    Rate limiting dependency - 1000 requests per hour per user
    TODO: Implement actual rate limiting logic
    
    Args:
        current_user: Current authenticated user
        
    Returns:
        dict: User document
    """
    # Placeholder - implement Redis-based rate limiting
    return current_user

# Content validation dependencies
def validate_content_ownership(
    content_id: str,
    current_user: dict = Depends(get_current_user),
    database: AsyncIOMotorDatabase = Depends(get_database)
) -> callable:
    """
    Validate that the current user owns the specified content
    
    Args:
        content_id: Content ID to validate
        current_user: Current authenticated user
        database: Database connection
        
    Returns:
        callable: Async function to validate ownership
    """
    async def validate():
        try:
            content = await database.contents.find_one({"_id": ObjectId(content_id)})
            if not content:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Content not found"
                )
            
            if content["user_id"] != str(current_user["_id"]):
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Access denied: Content belongs to another user"
                )
            
            return content
        except Exception as e:
            if isinstance(e, HTTPException):
                raise
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to validate content ownership"
            )
    
    return validate