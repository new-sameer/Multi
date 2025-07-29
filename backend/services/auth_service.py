#!/usr/bin/env python3
"""
Authentication service
Business logic for user authentication, JWT token management
"""

import logging
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from bson import ObjectId
from motor.motor_asyncio import AsyncIOMotorDatabase
from passlib.context import CryptContext
import jwt

from config import get_settings
from exceptions import InvalidCredentialsError, UserAlreadyExistsError, DatabaseError
from database import convert_objectid_to_str

logger = logging.getLogger(__name__)
settings = get_settings()

# Password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class AuthService:
    """Service for authentication operations"""
    
    def __init__(self, database: AsyncIOMotorDatabase):
        self.database = database
    
    def hash_password(self, password: str) -> str:
        """
        Hash a password for storing in the database
        
        Args:
            password: Plain text password
            
        Returns:
            str: Hashed password
        """
        return pwd_context.hash(password)
    
    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """
        Verify a password against its hash
        
        Args:
            plain_password: Plain text password
            hashed_password: Hashed password from database
            
        Returns:
            bool: True if password matches, False otherwise
        """
        return pwd_context.verify(plain_password, hashed_password)
    
    def create_access_token(
        self, 
        data: Dict[str, Any], 
        expires_delta: Optional[timedelta] = None
    ) -> str:
        """
        Create a JWT access token
        
        Args:
            data: Token payload data
            expires_delta: Token expiration time delta
            
        Returns:
            str: JWT access token
        """
        to_encode = data.copy()
        
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(hours=settings.JWT_EXPIRATION_HOURS)
        
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(to_encode, settings.JWT_SECRET, algorithm=settings.JWT_ALGORITHM)
        return encoded_jwt
    
    async def register_user(
        self, 
        email: str, 
        password: str, 
        first_name: str, 
        last_name: str,
        niche: Optional[str] = None,
        target_audience: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Register a new user
        
        Args:
            email: User email
            password: User password
            first_name: User first name
            last_name: User last name
            niche: User niche (optional)
            target_audience: User target audience (optional)
            
        Returns:
            dict: Created user data with access token
            
        Raises:
            UserAlreadyExistsError: If user already exists
            DatabaseError: If database operation fails
        """
        try:
            # Check if user already exists
            existing_user = await self.database.users.find_one({"email": email})
            if existing_user:
                raise UserAlreadyExistsError(email)
            
            # Create new user document
            user_dict = {
                "_id": ObjectId(),
                "email": email,
                "password_hash": self.hash_password(password),
                "first_name": first_name,
                "last_name": last_name,
                "subscription_tier": "starter",
                "success_level": "beginner",
                "niche": niche,
                "target_audience": target_audience,
                "onboarding_completed": False,
                "voice_enabled": False,
                "success_score": 0.0,
                "total_earnings": 0.0,
                "role": "user",
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow(),
                "last_active": datetime.utcnow()
            }
            
            # Insert user into database
            result = await self.database.users.insert_one(user_dict)
            
            # Convert ObjectId to string for response
            user_dict = convert_objectid_to_str(user_dict)
            
            # Create access token
            access_token = self.create_access_token(data={"sub": str(result.inserted_id)})
            
            # Create initial success journey
            await self._create_initial_success_journey(str(result.inserted_id))
            
            logger.info(f"User registered successfully: {email}")
            
            return {
                "user": user_dict,
                "access_token": access_token,
                "token_type": "bearer"
            }
            
        except UserAlreadyExistsError:
            raise
        except Exception as e:
            logger.error(f"Failed to register user {email}: {e}")
            raise DatabaseError(f"Failed to register user: {str(e)}")
    
    async def authenticate_user(self, email: str, password: str) -> Dict[str, Any]:
        """
        Authenticate user with email and password
        
        Args:
            email: User email
            password: User password
            
        Returns:
            dict: User data with access token
            
        Raises:
            InvalidCredentialsError: If credentials are invalid
            DatabaseError: If database operation fails
        """
        try:
            # Find user by email
            user = await self.database.users.find_one({"email": email})
            
            if not user or not self.verify_password(password, user["password_hash"]):
                raise InvalidCredentialsError()
            
            # Update last active timestamp
            await self.database.users.update_one(
                {"_id": user["_id"]},
                {"$set": {"last_active": datetime.utcnow()}}
            )
            
            # Convert ObjectId to string
            user = convert_objectid_to_str(user)
            
            # Create access token
            access_token = self.create_access_token(data={"sub": user["id"]})
            
            logger.info(f"User authenticated successfully: {email}")
            
            return {
                "user": user,
                "access_token": access_token,
                "token_type": "bearer"
            }
            
        except InvalidCredentialsError:
            raise
        except Exception as e:
            logger.error(f"Failed to authenticate user {email}: {e}")
            raise DatabaseError(f"Authentication failed: {str(e)}")
    
    async def change_password(
        self, 
        user_id: str, 
        current_password: str, 
        new_password: str
    ) -> bool:
        """
        Change user password
        
        Args:
            user_id: User ID
            current_password: Current password
            new_password: New password
            
        Returns:
            bool: True if password changed successfully
            
        Raises:
            InvalidCredentialsError: If current password is incorrect
            DatabaseError: If database operation fails
        """
        try:
            # Get user from database
            user = await self.database.users.find_one({"_id": ObjectId(user_id)})
            if not user:
                raise InvalidCredentialsError()
            
            # Verify current password
            if not self.verify_password(current_password, user["password_hash"]):
                raise InvalidCredentialsError()
            
            # Hash new password and update
            new_password_hash = self.hash_password(new_password)
            
            await self.database.users.update_one(
                {"_id": ObjectId(user_id)},
                {
                    "$set": {
                        "password_hash": new_password_hash,
                        "updated_at": datetime.utcnow()
                    }
                }
            )
            
            logger.info(f"Password changed for user: {user_id}")
            return True
            
        except InvalidCredentialsError:
            raise
        except Exception as e:
            logger.error(f"Failed to change password for user {user_id}: {e}")
            raise DatabaseError(f"Password change failed: {str(e)}")
    
    async def refresh_token(self, token: str) -> Dict[str, Any]:
        """
        Refresh an access token
        
        Args:
            token: Current access token
            
        Returns:
            dict: New access token data
            
        Raises:
            InvalidCredentialsError: If token is invalid
        """
        try:
            # Decode token to get user ID
            payload = jwt.decode(
                token, 
                settings.JWT_SECRET, 
                algorithms=[settings.JWT_ALGORITHM]
            )
            user_id = payload.get("sub")
            
            if not user_id:
                raise InvalidCredentialsError()
            
            # Verify user still exists
            user = await self.database.users.find_one({"_id": ObjectId(user_id)})
            if not user:
                raise InvalidCredentialsError()
            
            # Create new token
            new_token = self.create_access_token(data={"sub": user_id})
            
            return {
                "access_token": new_token,
                "token_type": "bearer"
            }
            
        except jwt.ExpiredSignatureError:
            raise InvalidCredentialsError("Token has expired")
        except jwt.InvalidTokenError:
            raise InvalidCredentialsError("Invalid token")
        except Exception as e:
            logger.error(f"Failed to refresh token: {e}")
            raise InvalidCredentialsError("Token refresh failed")
    
    async def _create_initial_success_journey(self, user_id: str) -> None:
        """
        Create initial success journey for a new user
        
        Args:
            user_id: User ID
        """
        try:
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
            
            await self.database.success_journeys.insert_one(journey_dict)
            logger.info(f"Created initial success journey for user {user_id}")
            
        except Exception as e:
            logger.error(f"Failed to create success journey for user {user_id}: {e}")
            # Don't raise error here as it shouldn't block registration