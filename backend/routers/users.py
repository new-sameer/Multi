#!/usr/bin/env python3
"""
User management router
API endpoints for user profile management and settings
"""

import logging
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from motor.motor_asyncio import AsyncIOMotorDatabase

from database import get_database
from dependencies import get_current_user
from services.user_service import UserService
from models.auth import UserResponse
from models.user import (
    UserProfileUpdate, SuccessGoals, SuccessGoalsResponse, 
    UserStats, SubscriptionUpdate
)
from exceptions import UserNotFoundError, DatabaseError, ValidationError

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/users", tags=["users"])

@router.get("/profile", response_model=UserResponse)
async def get_user_profile(
    current_user: dict = Depends(get_current_user),
    database: AsyncIOMotorDatabase = Depends(get_database)
):
    """Get current user's profile"""
    try:
        user_service = UserService(database)
        user_data = await user_service.get_user_by_id(str(current_user["_id"]))
        
        return UserResponse(**user_data)
        
    except UserNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User profile not found"
        )
    except DatabaseError as e:
        logger.error(f"Database error getting profile: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve profile"
        )
    except Exception as e:
        logger.error(f"Unexpected error getting profile: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred"
        )

@router.put("/profile", response_model=UserResponse)
async def update_user_profile(
    profile_data: UserProfileUpdate,
    current_user: dict = Depends(get_current_user),
    database: AsyncIOMotorDatabase = Depends(get_database)
):
    """Update user profile"""
    try:
        user_service = UserService(database)
        
        updated_user = await user_service.update_user_profile(
            user_id=str(current_user["_id"]),
            first_name=profile_data.first_name,
            last_name=profile_data.last_name,
            niche=profile_data.niche,
            target_audience=profile_data.target_audience
        )
        
        return UserResponse(**updated_user)
        
    except UserNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    except ValidationError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except DatabaseError as e:
        logger.error(f"Database error updating profile: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update profile"
        )
    except Exception as e:
        logger.error(f"Unexpected error updating profile: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred"
        )

@router.post("/success-goals", response_model=SuccessGoalsResponse)
async def set_success_goals(
    goals: SuccessGoals,
    current_user: dict = Depends(get_current_user),
    database: AsyncIOMotorDatabase = Depends(get_database)
):
    """Set user's success goals"""
    try:
        user_service = UserService(database)
        
        result = await user_service.set_success_goals(
            user_id=str(current_user["_id"]),
            followers_target=goals.followers_target,
            engagement_rate_target=goals.engagement_rate_target,
            revenue_target=goals.revenue_target,
            timeframe_days=goals.timeframe_days
        )
        
        return SuccessGoalsResponse(**result)
        
    except ValidationError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except UserNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    except DatabaseError as e:
        logger.error(f"Database error setting success goals: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to set success goals"
        )
    except Exception as e:
        logger.error(f"Unexpected error setting success goals: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred"
        )

@router.get("/stats", response_model=UserStats)
async def get_user_statistics(
    current_user: dict = Depends(get_current_user),
    database: AsyncIOMotorDatabase = Depends(get_database)
):
    """Get user statistics and analytics"""
    try:
        user_service = UserService(database)
        
        stats = await user_service.get_user_stats(str(current_user["_id"]))
        
        return UserStats(**stats)
        
    except UserNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    except DatabaseError as e:
        logger.error(f"Database error getting user stats: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve statistics"
        )
    except Exception as e:
        logger.error(f"Unexpected error getting user stats: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred"
        )

@router.put("/subscription", response_model=UserResponse)
async def update_subscription(
    subscription_data: SubscriptionUpdate,
    current_user: dict = Depends(get_current_user),
    database: AsyncIOMotorDatabase = Depends(get_database)
):
    """Update user subscription"""
    try:
        user_service = UserService(database)
        
        updated_user = await user_service.update_subscription(
            user_id=str(current_user["_id"]),
            subscription_tier=subscription_data.tier
        )
        
        return UserResponse(**updated_user)
        
    except ValidationError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except UserNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    except DatabaseError as e:
        logger.error(f"Database error updating subscription: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update subscription"
        )
    except Exception as e:
        logger.error(f"Unexpected error updating subscription: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred"
        )

@router.get("/preferences")
async def get_user_preferences(
    current_user: dict = Depends(get_current_user)
):
    """Get user preferences"""
    preferences = current_user.get("preferences", {})
    return {"preferences": preferences}

@router.put("/preferences")
async def update_user_preferences(
    preferences: dict,
    current_user: dict = Depends(get_current_user),
    database: AsyncIOMotorDatabase = Depends(get_database)
):
    """Update user preferences"""
    try:
        user_service = UserService(database)
        
        updated_user = await user_service.update_user_preferences(
            user_id=str(current_user["_id"]),
            preferences=preferences
        )
        
        return {"message": "Preferences updated successfully", "preferences": preferences}
        
    except UserNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    except DatabaseError as e:
        logger.error(f"Database error updating preferences: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update preferences"
        )
    except Exception as e:
        logger.error(f"Unexpected error updating preferences: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred"
        )

@router.delete("/profile")
async def delete_user_account(
    current_user: dict = Depends(get_current_user),
    database: AsyncIOMotorDatabase = Depends(get_database)
):
    """Delete user account"""
    try:
        user_service = UserService(database)
        
        success = await user_service.delete_user(str(current_user["_id"]))
        
        if success:
            return {"message": "Account deleted successfully"}
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to delete account"
            )
            
    except UserNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    except DatabaseError as e:
        logger.error(f"Database error deleting account: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete account"
        )
    except Exception as e:
        logger.error(f"Unexpected error deleting account: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred"
        )