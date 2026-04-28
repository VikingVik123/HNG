from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from typing import Optional

from db import get_db
from models.user_model import Users
from auth.tokens import TOKEN_TYPE_ACCESS
from auth.permissions import is_admin, is_analyst
from services.auth_sevice import AuthService
from exceptions import (
    UnauthorizedException,
    ForbiddenException,
    InvalidTokenException,
    UserNotActiveException,
)

# HTTPBearer security scheme for Swagger/OpenAPI documentation
security = HTTPBearer(
    scheme_name="Bearer",
    description="JWT access token"
)


def get_token(credentials: HTTPAuthorizationCredentials = Depends(security)) -> str:
    """
    Extract JWT token from Authorization header using HTTPBearer.
    FastAPI + Swagger will automatically handle this correctly.
    
    Args:
        credentials: HTTPAuthorizationCredentials from Authorization header
        
    Returns:
        JWT token string
    """
    return credentials.credentials


def get_current_user(
    token: str = Depends(get_token),
    db: Session = Depends(get_db)
) -> Users:
    """
    FastAPI dependency to get current authenticated user.
    Validates access token and returns user object.
    
    Args:
        token: JWT access token from Authorization header
        db: Database session
        
    Returns:
        Users object for authenticated user
        
    Raises:
        HTTPException: If token invalid/expired or user inactive
    """
    try:
        auth_service = AuthService(db)
        user_id = auth_service.validate_access_token(token)
        user = auth_service.get_user_by_id(user_id)
        return user
        
    except UnauthorizedException as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=e.message,
            headers={"WWW-Authenticate": "Bearer"}
        )
    except InvalidTokenException as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=e.message,
            headers={"WWW-Authenticate": "Bearer"}
        )
    except UserNotActiveException as e:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=e.message
        )


def require_admin(current_user: Users = Depends(get_current_user)) -> Users:
    """
    FastAPI dependency to require admin role.
    Use with Depends() in route handlers that require admin access.
    
    Args:
        current_user: Current authenticated user
        
    Returns:
        Users object if user is admin
        
    Raises:
        HTTPException: If user is not admin
    """
    if not is_admin(current_user.role):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    return current_user


def require_analyst(current_user: Users = Depends(get_current_user)) -> Users:
    """
    FastAPI dependency to require analyst role.
    Use with Depends() in route handlers that require analyst access.
    Note: Analysts can only perform read operations.
    
    Args:
        current_user: Current authenticated user
        
    Returns:
        Users object if user is analyst or admin
        
    Raises:
        HTTPException: If user is not analyst or admin
    """
    if not is_analyst(current_user.role) and not is_admin(current_user.role):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Analyst access required"
        )
    return current_user


def require_active_user(current_user: Users = Depends(get_current_user)) -> Users:
    """
    FastAPI dependency to ensure user is active.
    This is already checked in get_current_user, but can be used
    explicitly for clarity and separate 403 vs 401 responses.
    
    Args:
        current_user: Current authenticated user
        
    Returns:
        Users object if user is active
        
    Raises:
        HTTPException: If user is inactive
    """
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is inactive"
        )
    return current_user
