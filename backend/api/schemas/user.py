"""
Pydantic schemas for User-related operations
"""
from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import datetime
from uuid import UUID


class UserBase(BaseModel):
    """Base user schema"""
    email: EmailStr
    username: str = Field(..., min_length=3, max_length=100)


class UserCreate(UserBase):
    """User creation schema"""
    password: str = Field(..., min_length=8)


class UserLogin(BaseModel):
    """User login schema"""
    username: str
    password: str


class UserResponse(UserBase):
    """User response schema"""
    id: UUID
    is_active: bool
    is_premium: bool
    created_at: datetime

    class Config:
        from_attributes = True


class Token(BaseModel):
    """JWT token schema"""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class TokenPayload(BaseModel):
    """JWT token payload"""
    sub: str  # User ID
    exp: int  # Expiration timestamp
