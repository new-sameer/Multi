#!/usr/bin/env python3
"""
Authentication router
API endpoints for user authentication and JWT token management
"""

import logging
from fastapi import APIRouter, Depends, HTTPException, status
from motor.motor_asyncio import AsyncIOMotorDatabase

from database import get_database
from services.auth_service import AuthService
from models.auth import UserCreate, UserLogin, TokenResponse, PasswordChange
from exceptions import UserAlreadyExistsError, InvalidCredentialsError, DatabaseError

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/auth", tags=["authentication"])

@router.post("/register", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
async def register_user(
    user_data: UserCreate,
    database: AsyncIOMotorDatabase = Depends(get_database)
):
    """Register a new user"""
    try:
        auth_service = AuthService(database)
        
        result = await auth_service.register_user(
            email=user_data.email,
            password=user_data.password,
            first_name=user_data.first_name,
            last_name=user_data.last_name,
            niche=user_data.niche,
            target_audience=user_data.target_audience
        )
        
        return TokenResponse(
            access_token=result["access_token"],
            token_type=result["token_type"],
            user=result["user"]
        )
        
    except UserAlreadyExistsError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except DatabaseError as e:
        logger.error(f"Database error during registration: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Registration failed. Please try again."
        )
    except Exception as e:
        logger.error(f"Unexpected error during registration: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred"
        )

@router.post("/login", response_model=TokenResponse)
async def login_user(
    user_credentials: UserLogin,
    database: AsyncIOMotorDatabase = Depends(get_database)
):
    """Login a user"""
    try:
        auth_service = AuthService(database)
        
        result = await auth_service.authenticate_user(
            email=user_credentials.email,
            password=user_credentials.password
        )
        
        return TokenResponse(
            access_token=result["access_token"],
            token_type=result["token_type"],
            user=result["user"]
        )
        
    except InvalidCredentialsError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e),
            headers={"WWW-Authenticate": "Bearer"}
        )
    except DatabaseError as e:
        logger.error(f"Database error during login: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Login failed. Please try again."
        )
    except Exception as e:
        logger.error(f"Unexpected error during login: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred"
        )

@router.post("/change-password")
async def change_password(
    password_data: PasswordChange,
    current_user: dict = Depends(get_current_user),
    database: AsyncIOMotorDatabase = Depends(get_database)
):
    """Change user password"""
    try:
        auth_service = AuthService(database)
        
        success = await auth_service.change_password(
            user_id=str(current_user["_id"]),
            current_password=password_data.current_password,
            new_password=password_data.new_password
        )
        
        if success:
            return {"message": "Password changed successfully"}
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to change password"
            )
            
    except InvalidCredentialsError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Current password is incorrect"
        )
    except DatabaseError as e:
        logger.error(f"Database error during password change: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Password change failed. Please try again."
        )
    except Exception as e:
        logger.error(f"Unexpected error during password change: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred"
        )

@router.post("/refresh", response_model=TokenResponse)
async def refresh_token(
    current_user: dict = Depends(get_current_user),
    database: AsyncIOMotorDatabase = Depends(get_database)
):
    """Refresh access token"""
    try:
        auth_service = AuthService(database)
        
        # Create new token for current user
        new_token = auth_service.create_access_token(data={"sub": str(current_user["_id"])})
        
        return TokenResponse(
            access_token=new_token,
            token_type="bearer",
            user=current_user
        )
        
    except Exception as e:
        logger.error(f"Unexpected error during token refresh: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Token refresh failed"
        )

@router.post("/logout")
async def logout_user(current_user: dict = Depends(get_current_user)):
    """Logout user (client-side token removal)"""
    # In a JWT-based system, logout is typically handled client-side
    # by removing the token. For enhanced security, you could implement
    # a token blacklist stored in Redis.
    return {"message": "Logged out successfully"}

# Import dependencies at the end to avoid circular imports
from dependencies import get_current_user