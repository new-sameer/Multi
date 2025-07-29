#!/usr/bin/env python3
"""
Content management router
API endpoints for content creation, management, and analytics
"""

import logging
from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException, status, Query
from motor.motor_asyncio import AsyncIOMotorDatabase

from database import get_database
from dependencies import get_current_user, get_pagination_params, PaginationParams
from services.content_service import ContentService
from models.content import (
    ContentCreate, ContentResponse, ContentUpdate, ContentFilter,
    ContentList, ContentAnalytics, BulkContentOperation
)
from exceptions import (
    ContentNotFoundError, AuthorizationError, DatabaseError, ValidationError
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/content", tags=["content"])

@router.post("/create", response_model=ContentResponse, status_code=status.HTTP_201_CREATED)
async def create_content(
    content_data: ContentCreate,
    current_user: dict = Depends(get_current_user),
    database: AsyncIOMotorDatabase = Depends(get_database)
):
    """Create new content"""
    try:
        content_service = ContentService(database)
        
        created_content = await content_service.create_content(
            user_id=str(current_user["_id"]),
            title=content_data.title,
            content_type=content_data.content_type,
            platform=content_data.platform,
            text_content=content_data.text_content,
            hashtags=content_data.hashtags,
            scheduled_for=content_data.scheduled_for
        )
        
        return ContentResponse(**created_content)
        
    except ValidationError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except DatabaseError as e:
        logger.error(f"Database error creating content: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create content"
        )
    except Exception as e:
        logger.error(f"Unexpected error creating content: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred"
        )

@router.get("/list")
async def list_user_content(
    platform: Optional[str] = Query(None, regex="^(instagram|tiktok|linkedin|youtube|twitter|facebook)$"),
    status_filter: Optional[str] = Query(None, alias="status", regex="^(draft|scheduled|published|archived)$"),
    content_type: Optional[str] = Query(None, regex="^(text|image|video|carousel)$"),
    search: Optional[str] = Query(None, max_length=100),
    pagination: PaginationParams = Depends(get_pagination_params),
    current_user: dict = Depends(get_current_user),
    database: AsyncIOMotorDatabase = Depends(get_database)
):
    """List user's content with filtering and pagination"""
    try:
        content_service = ContentService(database)
        
        content_list, total_count = await content_service.list_user_content(
            user_id=str(current_user["_id"]),
            platform=platform,
            status=status_filter,
            content_type=content_type,
            search_query=search,
            page=pagination.page,
            per_page=pagination.per_page
        )
        
        # Convert to response models
        content_responses = [ContentResponse(**content) for content in content_list]
        
        return {
            "items": content_responses,
            "total": total_count,
            "page": pagination.page,
            "per_page": pagination.per_page,
            "has_next": (pagination.page * pagination.per_page) < total_count,
            "has_prev": pagination.page > 1
        }
        
    except DatabaseError as e:
        logger.error(f"Database error listing content: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve content"
        )
    except Exception as e:
        logger.error(f"Unexpected error listing content: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred"
        )

@router.get("/{content_id}", response_model=ContentResponse)
async def get_content(
    content_id: str,
    current_user: dict = Depends(get_current_user),
    database: AsyncIOMotorDatabase = Depends(get_database)
):
    """Get content by ID"""
    try:
        content_service = ContentService(database)
        
        content = await content_service.get_content_by_id(
            content_id=content_id,
            user_id=str(current_user["_id"])
        )
        
        return ContentResponse(**content)
        
    except ContentNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Content not found"
        )
    except AuthorizationError as e:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(e)
        )
    except DatabaseError as e:
        logger.error(f"Database error getting content: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve content"
        )
    except Exception as e:
        logger.error(f"Unexpected error getting content: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred"
        )

@router.put("/{content_id}", response_model=ContentResponse)
async def update_content(
    content_id: str,
    content_data: ContentUpdate,
    current_user: dict = Depends(get_current_user),
    database: AsyncIOMotorDatabase = Depends(get_database)
):
    """Update existing content"""
    try:
        content_service = ContentService(database)
        
        updated_content = await content_service.update_content(
            content_id=content_id,
            user_id=str(current_user["_id"]),
            title=content_data.title,
            text_content=content_data.text_content,
            hashtags=content_data.hashtags,
            scheduled_for=content_data.scheduled_for
        )
        
        return ContentResponse(**updated_content)
        
    except ContentNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Content not found"
        )
    except AuthorizationError as e:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(e)
        )
    except ValidationError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except DatabaseError as e:
        logger.error(f"Database error updating content: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update content"
        )
    except Exception as e:
        logger.error(f"Unexpected error updating content: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred"
        )

@router.delete("/{content_id}")
async def delete_content(
    content_id: str,
    current_user: dict = Depends(get_current_user),
    database: AsyncIOMotorDatabase = Depends(get_database)
):
    """Delete content"""
    try:
        content_service = ContentService(database)
        
        success = await content_service.delete_content(
            content_id=content_id,
            user_id=str(current_user["_id"])
        )
        
        if success:
            return {"message": "Content deleted successfully"}
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to delete content"
            )
            
    except ContentNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Content not found"
        )
    except AuthorizationError as e:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(e)
        )
    except DatabaseError as e:
        logger.error(f"Database error deleting content: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete content"
        )
    except Exception as e:
        logger.error(f"Unexpected error deleting content: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred"
        )

@router.patch("/{content_id}/status", response_model=ContentResponse)
async def update_content_status(
    content_id: str,
    new_status: str = Query(..., regex="^(draft|scheduled|published|archived)$"),
    current_user: dict = Depends(get_current_user),
    database: AsyncIOMotorDatabase = Depends(get_database)
):
    """Update content status"""
    try:
        content_service = ContentService(database)
        
        updated_content = await content_service.update_content_status(
            content_id=content_id,
            user_id=str(current_user["_id"]),
            status=new_status
        )
        
        return ContentResponse(**updated_content)
        
    except ContentNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Content not found"
        )
    except AuthorizationError as e:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(e)
        )
    except ValidationError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except DatabaseError as e:
        logger.error(f"Database error updating content status: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update content status"
        )
    except Exception as e:
        logger.error(f"Unexpected error updating content status: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred"
        )

@router.get("/analytics/overview", response_model=ContentAnalytics)
async def get_content_analytics(
    current_user: dict = Depends(get_current_user),
    database: AsyncIOMotorDatabase = Depends(get_database)
):
    """Get content analytics overview"""
    try:
        content_service = ContentService(database)
        
        analytics = await content_service.get_content_analytics(
            user_id=str(current_user["_id"])
        )
        
        return ContentAnalytics(**analytics)
        
    except DatabaseError as e:
        logger.error(f"Database error getting analytics: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve analytics"
        )
    except Exception as e:
        logger.error(f"Unexpected error getting analytics: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred"
        )

@router.post("/bulk-operation")
async def bulk_content_operation(
    operation_data: BulkContentOperation,
    current_user: dict = Depends(get_current_user),
    database: AsyncIOMotorDatabase = Depends(get_database)
):
    """Perform bulk operation on multiple content items"""
    try:
        content_service = ContentService(database)
        results = []
        errors = []
        
        for content_id in operation_data.content_ids:
            try:
                if operation_data.operation == "delete":
                    await content_service.delete_content(
                        content_id=content_id,
                        user_id=str(current_user["_id"])
                    )
                    results.append({"content_id": content_id, "status": "success"})
                    
                elif operation_data.operation in ["publish", "archive", "schedule"]:
                    status_map = {
                        "publish": "published",
                        "archive": "archived", 
                        "schedule": "scheduled"
                    }
                    
                    await content_service.update_content_status(
                        content_id=content_id,
                        user_id=str(current_user["_id"]),
                        status=status_map[operation_data.operation]
                    )
                    results.append({"content_id": content_id, "status": "success"})
                    
            except (ContentNotFoundError, AuthorizationError) as e:
                errors.append({"content_id": content_id, "error": str(e)})
            except Exception as e:
                errors.append({"content_id": content_id, "error": "Operation failed"})
        
        return {
            "message": f"Bulk {operation_data.operation} operation completed",
            "successful": len(results),
            "failed": len(errors),
            "results": results,
            "errors": errors
        }
        
    except ValidationError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Unexpected error in bulk operation: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Bulk operation failed"
        )