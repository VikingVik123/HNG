from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import datetime
from uuid import UUID


# Request schemas
class UserUpdateRequest(BaseModel):
    """Schema for updating user profile information"""
    username: Optional[str] = Field(None, min_length=1, max_length=255)
    email: Optional[str] = Field(None, min_length=1, max_length=255)
    avatar_url: Optional[str] = Field(None, max_length=500)
    
    class Config:
        from_attributes = True


class UserRoleUpdateRequest(BaseModel):
    """Schema for updating user role (admin only)"""
    role: str = Field(..., description="New role: 'admin' or 'analyst'")
    
    class Config:
        from_attributes = True


class UserActivationRequest(BaseModel):
    """Schema for activating/deactivating user"""
    is_active: bool = Field(..., description="Whether user should be active")
    
    class Config:
        from_attributes = True


# Response schemas
class UserResponse(BaseModel):
    """Schema for user response"""
    id: UUID
    github_id: str
    username: str
    email: Optional[str]
    avatar_url: Optional[str]
    role: str
    is_active: bool
    last_login_at: datetime
    created_at: Optional[datetime]
    
    class Config:
        from_attributes = True


class UserListResponse(BaseModel):
    """Schema for list of users"""
    total: int
    items: list[UserResponse]


class UserUpdateResponse(BaseModel):
    """Schema for update response"""
    message: str
    user: UserResponse


class UserDeleteResponse(BaseModel):
    """Schema for deactivation response"""
    message: str
    user: UserResponse


class LoginResponse(BaseModel):
    """Schema for login response"""
    message: str
    access_token: str