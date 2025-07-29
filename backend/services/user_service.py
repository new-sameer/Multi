#!/usr/bin/env python3
"""
User service
Business logic for user management, profiles, success goals
"""

import logging
from datetime import datetime
from typing import Optional, Dict, Any, List
from bson import ObjectId
from motor.motor_asyncio import AsyncIOMotorDatabase

from exceptions import UserNotFoundError, DatabaseError, ValidationError
from database import convert_objectid_to_str

logger = logging.getLogger(__name__)

class UserService:
    """Service for user management operations"""
    
    def __init__(self, database: AsyncIOMotorDatabase):
        self.database = database
    
    async def get_user_by_id(self, user_id: str) -> Dict[str, Any]:
        """
        Get user by ID
        
        Args:
            user_id: User ID
            
        Returns:
            dict: User data
            
        Raises:
            UserNotFoundError: If user doesn't exist
        """
        try:
            user = await self.database.users.find_one({"_id": ObjectId(user_id)})
            if not user:
                raise UserNotFoundError(user_id)
            
            return convert_objectid_to_str(user)
            
        except UserNotFoundError:
            raise
        except Exception as e:
            logger.error(f"Failed to get user {user_id}: {e}")
            raise DatabaseError(f"Failed to retrieve user: {str(e)}")
    
    async def update_user_profile(
        self,
        user_id: str,
        first_name: Optional[str] = None,
        last_name: Optional[str] = None,
        niche: Optional[str] = None,
        target_audience: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Update user profile information
        
        Args:
            user_id: User ID
            first_name: Updated first name
            last_name: Updated last name
            niche: Updated niche
            target_audience: Updated target audience
            
        Returns:
            dict: Updated user data
            
        Raises:
            UserNotFoundError: If user doesn't exist
            DatabaseError: If database operation fails
        """
        try:
            # Build update data
            update_data = {"updated_at": datetime.utcnow()}
            
            if first_name is not None:
                update_data["first_name"] = first_name
            if last_name is not None:
                update_data["last_name"] = last_name
            if niche is not None:
                update_data["niche"] = niche
            if target_audience is not None:
                update_data["target_audience"] = target_audience
            
            # Update user in database
            result = await self.database.users.update_one(
                {"_id": ObjectId(user_id)},
                {"$set": update_data}
            )
            
            if result.matched_count == 0:
                raise UserNotFoundError(user_id)
            
            # Get updated user
            updated_user = await self.database.users.find_one({"_id": ObjectId(user_id)})
            
            logger.info(f"User profile updated: {user_id}")
            return convert_objectid_to_str(updated_user)
            
        except UserNotFoundError:
            raise
        except Exception as e:
            logger.error(f"Failed to update user profile {user_id}: {e}")
            raise DatabaseError(f"Failed to update profile: {str(e)}")
    
    async def set_success_goals(
        self,
        user_id: str,
        followers_target: int,
        engagement_rate_target: float,
        revenue_target: float,
        timeframe_days: int
    ) -> Dict[str, Any]:
        """
        Set user success goals
        
        Args:
            user_id: User ID
            followers_target: Target number of followers
            engagement_rate_target: Target engagement rate
            revenue_target: Target revenue amount
            timeframe_days: Timeframe in days
            
        Returns:
            dict: Success goals response
            
        Raises:
            UserNotFoundError: If user doesn't exist
            ValidationError: If goals are invalid
            DatabaseError: If database operation fails
        """
        try:
            # Validate goals
            if followers_target < 100:
                raise ValidationError("Followers target must be at least 100")
            if not (0.01 <= engagement_rate_target <= 1.0):
                raise ValidationError("Engagement rate must be between 0.01 and 1.0")
            if revenue_target < 0:
                raise ValidationError("Revenue target cannot be negative")
            if not (30 <= timeframe_days <= 365):
                raise ValidationError("Timeframe must be between 30 and 365 days")
            
            goals_dict = {
                "followers_target": followers_target,
                "engagement_rate_target": engagement_rate_target,
                "revenue_target": revenue_target,
                "timeframe_days": timeframe_days,
                "set_at": datetime.utcnow()
            }
            
            # Update or create success journey
            journey = await self.database.success_journeys.find_one({"user_id": user_id})
            
            if journey:
                await self.database.success_journeys.update_one(
                    {"user_id": user_id},
                    {"$set": {
                        "success_goals": goals_dict,
                        "updated_at": datetime.utcnow()
                    }}
                )
            else:
                # Create new success journey if it doesn't exist
                await self._create_success_journey(user_id, goals_dict)
            
            # Mark onboarding as completed
            await self.database.users.update_one(
                {"_id": ObjectId(user_id)},
                {"$set": {
                    "onboarding_completed": True,
                    "updated_at": datetime.utcnow()
                }}
            )
            
            logger.info(f"Success goals set for user: {user_id}")
            return {
                "message": "Success goals set successfully",
                "goals": goals_dict
            }
            
        except (ValidationError, UserNotFoundError):
            raise
        except Exception as e:
            logger.error(f"Failed to set success goals for user {user_id}: {e}")
            raise DatabaseError(f"Failed to set success goals: {str(e)}")
    
    async def get_user_stats(self, user_id: str) -> Dict[str, Any]:
        """
        Get user statistics and analytics
        
        Args:
            user_id: User ID
            
        Returns:
            dict: User statistics
            
        Raises:
            UserNotFoundError: If user doesn't exist
            DatabaseError: If database operation fails
        """
        try:
            # Verify user exists
            user = await self.database.users.find_one({"_id": ObjectId(user_id)})
            if not user:
                raise UserNotFoundError(user_id)
            
            # Get content statistics
            content_stats = await self.database.contents.aggregate([
                {"$match": {"user_id": user_id}},
                {"$group": {
                    "_id": None,
                    "total_content": {"$sum": 1},
                    "published_content": {
                        "$sum": {"$cond": [{"$eq": ["$status", "published"]}, 1, 0]}
                    },
                    "avg_quality_score": {"$avg": "$quality_score"},
                    "avg_viral_potential": {"$avg": "$viral_potential"}
                }}
            ]).to_list(length=1)
            
            if content_stats:
                stats = content_stats[0]
            else:
                stats = {
                    "total_content": 0,
                    "published_content": 0,
                    "avg_quality_score": 0.0,
                    "avg_viral_potential": 0.0
                }
            
            # Get success journey data
            journey = await self.database.success_journeys.find_one({"user_id": user_id})
            
            # Calculate days since registration
            days_since_registration = (datetime.utcnow() - user["created_at"]).days
            
            return {
                "total_content_created": stats["total_content"],
                "total_posts_published": stats["published_content"],
                "avg_quality_score": round(stats["avg_quality_score"] or 0.0, 2),
                "avg_viral_potential": round(stats["avg_viral_potential"] or 0.0, 2),
                "success_score": user.get("success_score", 0.0),
                "total_earnings": user.get("total_earnings", 0.0),
                "days_since_registration": days_since_registration,
                "current_phase": journey.get("current_phase", "onboarding") if journey else "onboarding",
                "milestones_completed": len(journey.get("milestones_completed", [])) if journey else 0,
                "progress_score": journey.get("progress_score", 0.0) if journey else 0.0
            }
            
        except UserNotFoundError:
            raise
        except Exception as e:
            logger.error(f"Failed to get user stats {user_id}: {e}")
            raise DatabaseError(f"Failed to get user statistics: {str(e)}")
    
    async def update_user_preferences(
        self,
        user_id: str,
        preferences: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Update user preferences
        
        Args:
            user_id: User ID
            preferences: Preferences to update
            
        Returns:
            dict: Updated user data
            
        Raises:
            UserNotFoundError: If user doesn't exist
            DatabaseError: If database operation fails
        """
        try:
            # Build update data
            update_data = {
                "preferences": preferences,
                "updated_at": datetime.utcnow()
            }
            
            # Update user preferences
            result = await self.database.users.update_one(
                {"_id": ObjectId(user_id)},
                {"$set": update_data}
            )
            
            if result.matched_count == 0:
                raise UserNotFoundError(user_id)
            
            # Get updated user
            updated_user = await self.database.users.find_one({"_id": ObjectId(user_id)})
            
            logger.info(f"User preferences updated: {user_id}")
            return convert_objectid_to_str(updated_user)
            
        except UserNotFoundError:
            raise
        except Exception as e:
            logger.error(f"Failed to update user preferences {user_id}: {e}")
            raise DatabaseError(f"Failed to update preferences: {str(e)}")
    
    async def update_subscription(
        self,
        user_id: str,
        subscription_tier: str
    ) -> Dict[str, Any]:
        """
        Update user subscription tier
        
        Args:
            user_id: User ID
            subscription_tier: New subscription tier
            
        Returns:
            dict: Updated user data
            
        Raises:
            UserNotFoundError: If user doesn't exist
            ValidationError: If subscription tier is invalid
            DatabaseError: If database operation fails
        """
        try:
            valid_tiers = ["starter", "professional", "enterprise"]
            if subscription_tier not in valid_tiers:
                raise ValidationError(f"Invalid subscription tier. Must be one of: {valid_tiers}")
            
            # Update subscription
            result = await self.database.users.update_one(
                {"_id": ObjectId(user_id)},
                {"$set": {
                    "subscription_tier": subscription_tier,
                    "updated_at": datetime.utcnow()
                }}
            )
            
            if result.matched_count == 0:
                raise UserNotFoundError(user_id)
            
            # Get updated user
            updated_user = await self.database.users.find_one({"_id": ObjectId(user_id)})
            
            logger.info(f"User subscription updated to {subscription_tier}: {user_id}")
            return convert_objectid_to_str(updated_user)
            
        except (UserNotFoundError, ValidationError):
            raise
        except Exception as e:
            logger.error(f"Failed to update subscription for user {user_id}: {e}")
            raise DatabaseError(f"Failed to update subscription: {str(e)}")
    
    async def delete_user(self, user_id: str) -> bool:
        """
        Delete user account and associated data
        
        Args:
            user_id: User ID
            
        Returns:
            bool: True if deleted successfully
            
        Raises:
            UserNotFoundError: If user doesn't exist
            DatabaseError: If database operation fails
        """
        try:
            # Delete user and associated data in order
            user_result = await self.database.users.delete_one({"_id": ObjectId(user_id)})
            
            if user_result.deleted_count == 0:
                raise UserNotFoundError(user_id)
            
            # Delete associated data
            await self.database.contents.delete_many({"user_id": user_id})
            await self.database.success_journeys.delete_many({"user_id": user_id})
            await self.database.llm_usage_logs.delete_many({"user_id": user_id})
            
            logger.info(f"User account deleted: {user_id}")
            return True
            
        except UserNotFoundError:
            raise
        except Exception as e:
            logger.error(f"Failed to delete user {user_id}: {e}")
            raise DatabaseError(f"Failed to delete user account: {str(e)}")
    
    async def _create_success_journey(self, user_id: str, goals: Optional[Dict[str, Any]] = None) -> None:
        """
        Create success journey for user
        
        Args:
            user_id: User ID
            goals: Optional success goals
        """
        journey_dict = {
            "_id": ObjectId(),
            "user_id": user_id,
            "current_phase": "onboarding",
            "milestones_completed": [],
            "daily_actions": [],
            "blockers_identified": [],
            "coach_sessions": 0,
            "progress_score": 0.0,
            "success_probability": 0.5,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }
        
        if goals:
            journey_dict["success_goals"] = goals
        
        await self.database.success_journeys.insert_one(journey_dict)