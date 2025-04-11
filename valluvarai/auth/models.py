"""
Authentication models for ValluvarAI.
"""

from datetime import datetime
from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field, EmailStr


class UserPreferences(BaseModel):
    """User preferences model."""
    
    default_language: str = "both"
    default_image_style: str = "photorealistic"
    default_time_period: str = "modern"
    enable_image_generation: bool = True
    enable_video_generation: bool = False
    enable_audio_generation: bool = True
    favorite_kurals: List[int] = []
    favorite_themes: List[str] = []
    ui_theme: str = "light"
    
    class Config:
        """Pydantic config."""
        
        schema_extra = {
            "example": {
                "default_language": "both",
                "default_image_style": "photorealistic",
                "default_time_period": "modern",
                "enable_image_generation": True,
                "enable_video_generation": False,
                "enable_audio_generation": True,
                "favorite_kurals": [1, 155, 391],
                "favorite_themes": ["forgiveness", "love", "learning"],
                "ui_theme": "light"
            }
        }


class User(BaseModel):
    """User model."""
    
    id: str
    username: str
    email: EmailStr
    full_name: Optional[str] = None
    disabled: bool = False
    is_admin: bool = False
    created_at: datetime = Field(default_factory=datetime.now)
    last_login: Optional[datetime] = None
    preferences: UserPreferences = Field(default_factory=UserPreferences)
    usage_stats: Dict[str, Any] = Field(default_factory=dict)
    
    class Config:
        """Pydantic config."""
        
        schema_extra = {
            "example": {
                "id": "user123",
                "username": "valluvar_fan",
                "email": "user@example.com",
                "full_name": "Tamil Literature Enthusiast",
                "disabled": False,
                "is_admin": False,
                "created_at": "2023-01-01T00:00:00",
                "last_login": "2023-01-02T00:00:00",
                "preferences": {
                    "default_language": "both",
                    "default_image_style": "photorealistic",
                    "default_time_period": "modern",
                    "enable_image_generation": True,
                    "enable_video_generation": False,
                    "enable_audio_generation": True,
                    "favorite_kurals": [1, 155, 391],
                    "favorite_themes": ["forgiveness", "love", "learning"],
                    "ui_theme": "light"
                },
                "usage_stats": {
                    "searches": 10,
                    "stories_generated": 5,
                    "images_generated": 15,
                    "videos_generated": 2
                }
            }
        }


class Token(BaseModel):
    """Token model."""
    
    access_token: str
    token_type: str
    expires_at: datetime
    
    class Config:
        """Pydantic config."""
        
        schema_extra = {
            "example": {
                "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                "token_type": "bearer",
                "expires_at": "2023-01-02T00:00:00"
            }
        }


class TokenData(BaseModel):
    """Token data model."""
    
    username: str
    exp: datetime
    
    class Config:
        """Pydantic config."""
        
        schema_extra = {
            "example": {
                "username": "valluvar_fan",
                "exp": "2023-01-02T00:00:00"
            }
        }


class UserCreate(BaseModel):
    """User creation model."""
    
    username: str
    email: EmailStr
    password: str
    full_name: Optional[str] = None
    
    class Config:
        """Pydantic config."""
        
        schema_extra = {
            "example": {
                "username": "valluvar_fan",
                "email": "user@example.com",
                "password": "securepassword123",
                "full_name": "Tamil Literature Enthusiast"
            }
        }


class UserUpdate(BaseModel):
    """User update model."""
    
    email: Optional[EmailStr] = None
    full_name: Optional[str] = None
    password: Optional[str] = None
    preferences: Optional[UserPreferences] = None
    
    class Config:
        """Pydantic config."""
        
        schema_extra = {
            "example": {
                "email": "newemail@example.com",
                "full_name": "Updated Name",
                "password": "newsecurepassword123",
                "preferences": {
                    "default_language": "tamil",
                    "ui_theme": "dark"
                }
            }
        }


class UserInDB(User):
    """User model with hashed password for database storage."""
    
    hashed_password: str
    
    class Config:
        """Pydantic config."""
        
        schema_extra = {
            "example": {
                "id": "user123",
                "username": "valluvar_fan",
                "email": "user@example.com",
                "full_name": "Tamil Literature Enthusiast",
                "disabled": False,
                "is_admin": False,
                "created_at": "2023-01-01T00:00:00",
                "last_login": "2023-01-02T00:00:00",
                "hashed_password": "$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW",
                "preferences": {
                    "default_language": "both",
                    "default_image_style": "photorealistic",
                    "default_time_period": "modern",
                    "enable_image_generation": True,
                    "enable_video_generation": False,
                    "enable_audio_generation": True,
                    "favorite_kurals": [1, 155, 391],
                    "favorite_themes": ["forgiveness", "love", "learning"],
                    "ui_theme": "light"
                },
                "usage_stats": {
                    "searches": 10,
                    "stories_generated": 5,
                    "images_generated": 15,
                    "videos_generated": 2
                }
            }
        }
