from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import datetime


class UserAuthResponse(BaseModel):
    """
    User data returned in auth responses.
    Minimal user information for token responses.
    """
    id: str
    username: str
    email: Optional[str] = None
    avatar_url: Optional[str] = None
    role: str
    is_active: bool

    class Config:
        from_attributes = True


class TokenResponse(BaseModel):
    """
    Response after successful authentication.
    Contains tokens and user information.
    """
    status: str = "success"
    access_token: str
    refresh_token: str
    user: UserAuthResponse
    message: str = "Authentication successful"


class RefreshTokenRequest(BaseModel):
    """
    Request body for refreshing tokens.
    """
    refresh_token: str

    class Config:
        json_schema_extra = {
            "example": {
                "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
            }
        }


class RefreshTokenResponse(BaseModel):
    """
    Response after refreshing tokens.
    Returns new token pair.
    """
    status: str = "success"
    access_token: str
    refresh_token: str
    message: str = "Tokens refreshed successfully"


class GitHubAuthCallbackRequest(BaseModel):
    """
    Query parameters from GitHub OAuth callback.
    """
    code: str
    state: str


class LogoutRequest(BaseModel):
    """
    Request body for logout endpoint.
    """
    refresh_token: str

    class Config:
        json_schema_extra = {
            "example": {
                "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
            }
        }


class LogoutResponse(BaseModel):
    """
    Response after successful logout.
    """
    status: str = "success"
    message: str = "Logged out successfully"


class ErrorResponse(BaseModel):
    """
    Standard error response format.
    """
    status: str = "error"
    message: str
    code: Optional[str] = None

    class Config:
        json_schema_extra = {
            "example": {
                "status": "error",
                "message": "Invalid credentials",
                "code": "INVALID_CREDENTIALS"
            }
        }

class ExchangeRequest(BaseModel):
    code: str