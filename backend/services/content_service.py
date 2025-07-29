#!/usr/bin/env python3
"""
Content service
Business logic for content creation, management, and analytics
"""

import logging
import re
from datetime import datetime
from typing import Optional, Dict, Any, List, Tuple
from bson import ObjectId
from motor.motor_asyncio import AsyncIOMotorDatabase

from exceptions import ContentNotFoundError, DatabaseError, ValidationError, AuthorizationError
from database import convert_objectid_to_str

logger = logging.getLogger(__name__)

class ContentService:
    """Service for content management operations"""
    
    def __init__(self, database: AsyncIOMotorDatabase):
        self.database = database
    
    async def create_content(
        self,
        user_id: str,
        title: str,
        content_type: str,
        platform: str,
        text_content: str,
        hashtags: List[str] = None,
        scheduled_for: Optional[datetime] = None
    ) -> Dict[str, Any]:
        """
        Create new content
        
        Args:
            user_id: User ID
            title: Content title
            content_type: Type of content
            platform: Target platform
            text_content: Content text
            hashtags: List of hashtags
            scheduled_for: Scheduled publish time
            
        Returns:
            dict: Created content data
            
        Raises:
            ValidationError: If content data is invalid
            DatabaseError: If database operation fails
        """
        try:
            # Validate and process hashtags
            processed_hashtags = self._process_hashtags(hashtags or [])
            
            # Calculate initial scores (placeholder - would use AI in production)
            quality_score = await self._calculate_quality_score(text_content, platform)
            viral_potential = await self._calculate_viral_potential(text_content, processed_hashtags)
            
            content_dict = {
                "_id": ObjectId(),
                "user_id": user_id,
                "title": title.strip(),
                "content_type": content_type,
                "platform": platform,
                "text_content": text_content.strip(),
                "hashtags": processed_hashtags,
                "status": "draft",
                "quality_score": quality_score,
                "viral_potential": viral_potential,
                "scheduled_for": scheduled_for,
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow(),
                "performance_metrics": {},
                "ai_generated": False
            }
            
            # Insert content into database
            result = await self.database.contents.insert_one(content_dict)
            
            # Convert ObjectId to string
            content_dict = convert_objectid_to_str(content_dict)
            
            logger.info(f"Content created: {content_dict['id']} for user: {user_id}")
            return content_dict
            
        except Exception as e:
            logger.error(f"Failed to create content for user {user_id}: {e}")
            raise DatabaseError(f"Failed to create content: {str(e)}")
    
    async def get_content_by_id(self, content_id: str, user_id: str) -> Dict[str, Any]:
        """
        Get content by ID
        
        Args:
            content_id: Content ID
            user_id: User ID (for ownership validation)
            
        Returns:
            dict: Content data
            
        Raises:
            ContentNotFoundError: If content doesn't exist
            AuthorizationError: If user doesn't own the content
        """
        try:
            content = await self.database.contents.find_one({"_id": ObjectId(content_id)})
            
            if not content:
                raise ContentNotFoundError(content_id)
            
            # Verify ownership
            if content["user_id"] != user_id:
                raise AuthorizationError("Access denied: Content belongs to another user")
            
            return convert_objectid_to_str(content)
            
        except (ContentNotFoundError, AuthorizationError):
            raise
        except Exception as e:
            logger.error(f"Failed to get content {content_id}: {e}")
            raise DatabaseError(f"Failed to retrieve content: {str(e)}")
    
    async def update_content(
        self,
        content_id: str,
        user_id: str,
        title: Optional[str] = None,
        text_content: Optional[str] = None,
        hashtags: Optional[List[str]] = None,
        scheduled_for: Optional[datetime] = None
    ) -> Dict[str, Any]:
        """
        Update existing content
        
        Args:
            content_id: Content ID
            user_id: User ID
            title: Updated title
            text_content: Updated text content
            hashtags: Updated hashtags
            scheduled_for: Updated schedule time
            
        Returns:
            dict: Updated content data
            
        Raises:
            ContentNotFoundError: If content doesn't exist
            AuthorizationError: If user doesn't own the content
            DatabaseError: If database operation fails
        """
        try:
            # First verify content exists and user owns it
            await self.get_content_by_id(content_id, user_id)
            
            # Build update data
            update_data = {"updated_at": datetime.utcnow()}
            
            if title is not None:
                update_data["title"] = title.strip()
            
            if text_content is not None:
                update_data["text_content"] = text_content.strip()
                # Recalculate quality score when content changes
                update_data["quality_score"] = await self._calculate_quality_score(
                    text_content.strip(), 
                    None  # We'd need to get the platform from existing content
                )
            
            if hashtags is not None:
                processed_hashtags = self._process_hashtags(hashtags)
                update_data["hashtags"] = processed_hashtags
                # Recalculate viral potential when hashtags change
                if text_content:
                    update_data["viral_potential"] = await self._calculate_viral_potential(
                        text_content.strip(), processed_hashtags
                    )
            
            if scheduled_for is not None:
                update_data["scheduled_for"] = scheduled_for
            
            # Update content
            await self.database.contents.update_one(
                {"_id": ObjectId(content_id)},
                {"$set": update_data}
            )
            
            # Get updated content
            updated_content = await self.database.contents.find_one({"_id": ObjectId(content_id)})
            
            logger.info(f"Content updated: {content_id}")
            return convert_objectid_to_str(updated_content)
            
        except (ContentNotFoundError, AuthorizationError):
            raise
        except Exception as e:
            logger.error(f"Failed to update content {content_id}: {e}")
            raise DatabaseError(f"Failed to update content: {str(e)}")
    
    async def delete_content(self, content_id: str, user_id: str) -> bool:
        """
        Delete content
        
        Args:
            content_id: Content ID
            user_id: User ID
            
        Returns:
            bool: True if deleted successfully
            
        Raises:
            ContentNotFoundError: If content doesn't exist
            AuthorizationError: If user doesn't own the content
            DatabaseError: If database operation fails
        """
        try:
            # First verify content exists and user owns it
            await self.get_content_by_id(content_id, user_id)
            
            # Delete content
            result = await self.database.contents.delete_one({"_id": ObjectId(content_id)})
            
            if result.deleted_count == 0:
                raise ContentNotFoundError(content_id)
            
            logger.info(f"Content deleted: {content_id}")
            return True
            
        except (ContentNotFoundError, AuthorizationError):
            raise
        except Exception as e:
            logger.error(f"Failed to delete content {content_id}: {e}")
            raise DatabaseError(f"Failed to delete content: {str(e)}")
    
    async def list_user_content(
        self,
        user_id: str,
        platform: Optional[str] = None,
        status: Optional[str] = None,
        content_type: Optional[str] = None,
        search_query: Optional[str] = None,
        page: int = 1,
        per_page: int = 20
    ) -> Tuple[List[Dict[str, Any]], int]:
        """
        List user's content with filtering and pagination
        
        Args:
            user_id: User ID
            platform: Filter by platform
            status: Filter by status
            content_type: Filter by content type
            search_query: Search query
            page: Page number
            per_page: Items per page
            
        Returns:
            tuple: (content_list, total_count)
            
        Raises:
            DatabaseError: If database operation fails
        """
        try:
            # Build filter query
            filter_query = {"user_id": user_id}
            
            if platform:
                filter_query["platform"] = platform
            if status:
                filter_query["status"] = status
            if content_type:
                filter_query["content_type"] = content_type
            if search_query:
                filter_query["$or"] = [
                    {"title": {"$regex": search_query, "$options": "i"}},
                    {"text_content": {"$regex": search_query, "$options": "i"}}
                ]
            
            # Calculate pagination
            skip = (page - 1) * per_page
            
            # Get total count
            total_count = await self.database.contents.count_documents(filter_query)
            
            # Get content with pagination
            content_cursor = self.database.contents.find(filter_query).sort("created_at", -1).skip(skip).limit(per_page)
            contents = await content_cursor.to_list(length=per_page)
            
            # Convert ObjectIds to strings
            content_list = []
            for content in contents:
                content_list.append(convert_objectid_to_str(content))
            
            return content_list, total_count
            
        except Exception as e:
            logger.error(f"Failed to list content for user {user_id}: {e}")
            raise DatabaseError(f"Failed to list content: {str(e)}")
    
    async def update_content_status(
        self,
        content_id: str,
        user_id: str,
        status: str
    ) -> Dict[str, Any]:
        """
        Update content status
        
        Args:
            content_id: Content ID
            user_id: User ID
            status: New status
            
        Returns:
            dict: Updated content data
            
        Raises:
            ContentNotFoundError: If content doesn't exist
            AuthorizationError: If user doesn't own the content
            ValidationError: If status is invalid
            DatabaseError: If database operation fails
        """
        try:
            valid_statuses = ["draft", "scheduled", "published", "archived"]
            if status not in valid_statuses:
                raise ValidationError(f"Invalid status. Must be one of: {valid_statuses}")
            
            # Verify content exists and user owns it
            await self.get_content_by_id(content_id, user_id)
            
            update_data = {
                "status": status,
                "updated_at": datetime.utcnow()
            }
            
            # Set published_at if status is published
            if status == "published":
                update_data["published_at"] = datetime.utcnow()
            
            # Update content
            await self.database.contents.update_one(
                {"_id": ObjectId(content_id)},
                {"$set": update_data}
            )
            
            # Get updated content
            updated_content = await self.database.contents.find_one({"_id": ObjectId(content_id)})
            
            logger.info(f"Content status updated to {status}: {content_id}")
            return convert_objectid_to_str(updated_content)
            
        except (ContentNotFoundError, AuthorizationError, ValidationError):
            raise
        except Exception as e:
            logger.error(f"Failed to update content status {content_id}: {e}")
            raise DatabaseError(f"Failed to update content status: {str(e)}")
    
    async def get_content_analytics(self, user_id: str) -> Dict[str, Any]:
        """
        Get content analytics for user
        
        Args:
            user_id: User ID
            
        Returns:
            dict: Content analytics data
            
        Raises:
            DatabaseError: If database operation fails
        """
        try:
            # Aggregate content statistics
            pipeline = [
                {"$match": {"user_id": user_id}},
                {"$group": {
                    "_id": None,
                    "total_content": {"$sum": 1},
                    "published_content": {
                        "$sum": {"$cond": [{"$eq": ["$status", "published"]}, 1, 0]}
                    },
                    "draft_content": {
                        "$sum": {"$cond": [{"$eq": ["$status", "draft"]}, 1, 0]}
                    },
                    "scheduled_content": {
                        "$sum": {"$cond": [{"$eq": ["$status", "scheduled"]}, 1, 0]}
                    },
                    "avg_quality_score": {"$avg": "$quality_score"},
                    "avg_viral_potential": {"$avg": "$viral_potential"}
                }}
            ]
            
            result = await self.database.contents.aggregate(pipeline).to_list(length=1)
            
            if result:
                stats = result[0]
                return {
                    "total_content": stats["total_content"],
                    "published_content": stats["published_content"],
                    "draft_content": stats["draft_content"],
                    "scheduled_content": stats["scheduled_content"],
                    "avg_quality_score": round(stats["avg_quality_score"] or 0.0, 2),
                    "avg_viral_potential": round(stats["avg_viral_potential"] or 0.0, 2)
                }
            else:
                return {
                    "total_content": 0,
                    "published_content": 0,
                    "draft_content": 0,
                    "scheduled_content": 0,
                    "avg_quality_score": 0.0,
                    "avg_viral_potential": 0.0
                }
                
        except Exception as e:
            logger.error(f"Failed to get content analytics for user {user_id}: {e}")
            raise DatabaseError(f"Failed to get content analytics: {str(e)}")
    
    def _process_hashtags(self, hashtags: List[str]) -> List[str]:
        """
        Process and validate hashtags
        
        Args:
            hashtags: Raw hashtags list
            
        Returns:
            list: Processed hashtags
        """
        if not hashtags:
            return []
        
        processed = []
        for tag in hashtags[:30]:  # Limit to 30 hashtags
            if not tag or not tag.strip():
                continue
            
            # Clean the hashtag
            tag = tag.strip()
            
            # Add # prefix if missing
            if not tag.startswith('#'):
                tag = f"#{tag}"
            
            # Remove spaces and special characters except underscores
            tag = re.sub(r'[^\w#]', '', tag)
            
            # Skip if too short or just #
            if len(tag) <= 1:
                continue
            
            processed.append(tag)
        
        # Remove duplicates while preserving order
        seen = set()
        unique_hashtags = []
        for tag in processed:
            if tag.lower() not in seen:
                seen.add(tag.lower())
                unique_hashtags.append(tag)
        
        return unique_hashtags
    
    async def _calculate_quality_score(self, text_content: str, platform: str) -> float:
        """
        Calculate content quality score
        This is a simplified implementation - would use AI analysis in production
        
        Args:
            text_content: Content text
            platform: Target platform
            
        Returns:
            float: Quality score between 0 and 1
        """
        score = 0.5  # Base score
        
        # Length scoring
        content_length = len(text_content)
        if 100 <= content_length <= 500:
            score += 0.2
        elif content_length > 500:
            score += 0.1
        
        # Check for engagement elements
        if any(word in text_content.lower() for word in ['?', 'how', 'why', 'what', 'when']):
            score += 0.1
        
        # Check for call-to-action words
        cta_words = ['learn', 'discover', 'share', 'comment', 'follow', 'subscribe']
        if any(word in text_content.lower() for word in cta_words):
            score += 0.1
        
        # Platform-specific adjustments
        if platform == 'linkedin' and content_length > 200:
            score += 0.1
        elif platform == 'twitter' and content_length <= 280:
            score += 0.1
        
        return min(max(score, 0.0), 1.0)
    
    async def _calculate_viral_potential(self, text_content: str, hashtags: List[str]) -> float:
        """
        Calculate viral potential score
        This is a simplified implementation - would use AI analysis in production
        
        Args:
            text_content: Content text
            hashtags: List of hashtags
            
        Returns:
            float: Viral potential score between 0 and 1
        """
        score = 0.3  # Base score
        
        # Hashtag scoring
        hashtag_count = len(hashtags)
        if 3 <= hashtag_count <= 10:
            score += 0.2
        elif hashtag_count > 10:
            score += 0.1
        
        # Trending keywords (simplified)
        trending_keywords = ['ai', 'viral', 'trending', 'breaking', 'exclusive', 'secret']
        if any(keyword in text_content.lower() for keyword in trending_keywords):
            score += 0.2
        
        # Emotional words
        emotional_words = ['amazing', 'incredible', 'shocking', 'unbelievable', 'mind-blowing']
        if any(word in text_content.lower() for word in emotional_words):
            score += 0.1
        
        # Question format
        if '?' in text_content:
            score += 0.1
        
        # Numbers and lists
        if any(char.isdigit() for char in text_content):
            score += 0.1
        
        return min(max(score, 0.0), 1.0)