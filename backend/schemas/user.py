"""
Nexus AI - User Schemas
Pydantic models for user-related requests and responses
"""

from pydantic import BaseModel, EmailStr, Field
from datetime import datetime
from typing import Optional


class UserCreate(BaseModel):
    """Schema for user registration"""
    email: EmailStr = Field(..., example="madhur.tyagi@nexus-ai.com")
    username: str = Field(..., min_length=3, max_length=50, example="madhurtyagi")
    password: str = Field(..., min_length=6, max_length=100, example="securePassword123!")


class UserLogin(BaseModel):
    """Schema for user login"""
    email: EmailStr
    password: str


class UserResponse(BaseModel):
    """Schema for user response (excludes password)"""
    id: int = Field(..., example=123)
    email: str = Field(..., example="madhur.tyagi@nexus-ai.com")
    username: str = Field(..., example="madhurtyagi")
    is_active: bool = Field(..., example=True)
    created_at: datetime
    
    class Config:
        from_attributes = True


class Token(BaseModel):
    """Schema for JWT token response"""
    access_token: str
    token_type: str = "bearer"


class TokenData(BaseModel):
    """Schema for token payload data"""
    user_id: Optional[int] = None
