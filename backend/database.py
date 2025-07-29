#!/usr/bin/env python3
"""
Database connection and utilities for MongoDB
Centralized database management with connection pooling and error handling
"""

import logging
from typing import Optional
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from pymongo.errors import ServerSelectionTimeoutError, ConnectionFailure
from config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()

class DatabaseManager:
    """Database connection manager with connection pooling"""
    
    def __init__(self):
        self.client: Optional[AsyncIOMotorClient] = None
        self.database: Optional[AsyncIOMotorDatabase] = None
    
    async def connect(self) -> AsyncIOMotorDatabase:
        """Connect to MongoDB and return database instance"""
        try:
            self.client = AsyncIOMotorClient(
                settings.MONGO_URL,
                maxPoolSize=settings.CONNECTION_POOL_SIZE,
                serverSelectionTimeoutMS=settings.DATABASE_TIMEOUT * 1000,
                retryWrites=True
            )
            
            # Test the connection
            await self.client.admin.command('ping')
            
            self.database = self.client.get_default_database()
            logger.info("Successfully connected to MongoDB")
            
            # Create indexes for better performance
            await self._create_indexes()
            
            return self.database
            
        except (ServerSelectionTimeoutError, ConnectionFailure) as e:
            logger.error(f"Failed to connect to MongoDB: {e}")
            raise
        except Exception as e:
            logger.error(f"Unexpected database connection error: {e}")
            raise
    
    async def disconnect(self):
        """Close database connection"""
        if self.client:
            self.client.close()
            logger.info("MongoDB connection closed")
    
    async def _create_indexes(self):
        """Create database indexes for better performance"""
        try:
            if not self.database:
                return
            
            # User collection indexes
            await self.database.users.create_index("email", unique=True)
            await self.database.users.create_index("created_at")
            await self.database.users.create_index("subscription_tier")
            await self.database.users.create_index("success_level")
            
            # Content collection indexes
            await self.database.contents.create_index([("user_id", 1), ("created_at", -1)])
            await self.database.contents.create_index("platform")
            await self.database.contents.create_index("status")
            await self.database.contents.create_index("content_type")
            await self.database.contents.create_index([("user_id", 1), ("platform", 1)])
            
            # Success journeys indexes
            await self.database.success_journeys.create_index("user_id", unique=True)
            await self.database.success_journeys.create_index("current_phase")
            await self.database.success_journeys.create_index("progress_score")
            
            # LLM usage logs indexes
            await self.database.llm_usage_logs.create_index([("user_id", 1), ("timestamp", -1)])
            await self.database.llm_usage_logs.create_index("provider")
            await self.database.llm_usage_logs.create_index("task_type")
            await self.database.llm_usage_logs.create_index([("timestamp", -1)])
            
            # Performance indexes
            await self.database.llm_usage_logs.create_index([("provider", 1), ("timestamp", -1)])
            await self.database.contents.create_index([("user_id", 1), ("quality_score", -1)])
            
            logger.info("Database indexes created successfully")
            
        except Exception as e:
            logger.error(f"Failed to create database indexes: {e}")

# Global database manager instance
db_manager = DatabaseManager()

async def get_database() -> AsyncIOMotorDatabase:
    """Get database instance"""
    if db_manager.database is None:
        await db_manager.connect()
    return db_manager.database

def convert_objectid_to_str(doc: dict) -> dict:
    """Convert MongoDB ObjectId to string for JSON serialization"""
    if doc and "_id" in doc:
        doc["id"] = str(doc["_id"])
        del doc["_id"]
    return doc

async def health_check() -> bool:
    """Check database health"""
    try:
        database = await get_database()
        await database.command("ping")
        return True
    except Exception as e:
        logger.error(f"Database health check failed: {e}")
        return False