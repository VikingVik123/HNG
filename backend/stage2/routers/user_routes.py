from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from uuid import UUID

from db import get_db
from models.user_model import Users
from schemas.user_schemas import (
    UserResponse,
    UserListResponse,
    UserUpdateResponse,
    UserDeleteResponse,
    UserUpdateRequest,
    UserRoleUpdateRequest,
    UserActivationRequest,
)
from services.user_service import UserService
from auth.dependencies import get_current_user, require_admin

router = APIRouter(prefix="/users", tags=["users"])


@router.get("/me", response_model=UserResponse, summary="Get current user profile")
def get_current_user_profile(
    current_user: Users = Depends(get_current_user)
) -> UserResponse:
    """
    Get profile information for the currently authenticated user.
    
    Returns:
        UserResponse: Current user's profile data
    """
    return current_user


@router.get("", response_model=UserListResponse, summary="List all users")
def list_users(
    skip: int = 0,
    limit: int = 100,
    current_user: Users = Depends(require_admin),
    db: Session = Depends(get_db)
) -> UserListResponse:
    """
    Get list of all users (admin only).
    
    Query Parameters:
        skip: Number of records to skip (default: 0)
        limit: Maximum records to return (default: 100, max: 1000)
        
    Returns:
        UserListResponse: List of users with pagination
    """
    if limit > 1000:
        limit = 1000
    
    user_service = UserService(db)
    users, total = user_service.get_all_users(skip=skip, limit=limit)
    
    return UserListResponse(
        total=total,
        items=[UserResponse.from_orm(user) for user in users]
    )


@router.get("/{user_id}", response_model=UserResponse, summary="Get user by ID")
def get_user_by_id(
    user_id: UUID,
    current_user: Users = Depends(require_admin),
    db: Session = Depends(get_db)
) -> UserResponse:
    """
    Get user information by ID (admin only).
    
    Path Parameters:
        user_id: UUID of the user to retrieve
        
    Returns:
        UserResponse: User's profile data
        
    Raises:
        404: User not found
    """
    try:
        user_service = UserService(db)
        user = user_service.get_user_by_id(user_id)
        return user
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )


@router.patch("/{user_id}", response_model=UserUpdateResponse, summary="Update user profile")
def update_user(
    user_id: UUID,
    update_data: UserUpdateRequest,
    current_user: Users = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> UserUpdateResponse:
    """
    Update user profile information.
    Users can only update themselves, admins can update any user.
    
    Path Parameters:
        user_id: UUID of the user to update
        
    Request Body:
        update_data: Fields to update (username, email, avatar_url)
        
    Returns:
        UserUpdateResponse: Updated user and success message
        
    Raises:
        403: Insufficient permissions
        404: User not found
    """
    # Check permissions: only admins can update other users
    if str(user_id) != str(current_user.id) and current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only update your own profile"
        )
    
    try:
        user_service = UserService(db)
        updated_user = user_service.update_user(
            user_id=user_id,
            username=update_data.username,
            email=update_data.email,
            avatar_url=update_data.avatar_url
        )
        
        return UserUpdateResponse(
            message="User profile updated successfully",
            user=updated_user
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )


@router.patch("/{user_id}/role", response_model=UserUpdateResponse, summary="Update user role")
def update_user_role(
    user_id: UUID,
    role_data: UserRoleUpdateRequest,
    current_user: Users = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> UserUpdateResponse:
    """
    Update user role.
    Users can change their own role. Admins can change any user's role.
    
    Path Parameters:
        user_id: UUID of the user to update
        
    Request Body:
        role_data: New role ('admin' or 'analyst')
        
    Returns:
        UserUpdateResponse: Updated user and success message
        
    Raises:
        400: Invalid role value
        403: Insufficient permissions (can only change own role unless admin)
        404: User not found
    """
    # Check permissions: only admins can change other users' roles
    if str(user_id) != str(current_user.id) and current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only change your own role"
        )
    
    if role_data.role not in ["admin", "analyst"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Role must be 'admin' or 'analyst'"
        )
    
    try:
        user_service = UserService(db)
        updated_user = user_service.update_user_role(user_id, role_data.role)
        
        return UserUpdateResponse(
            message=f"User role updated to {role_data.role}",
            user=updated_user
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )


@router.patch("/{user_id}/status", response_model=UserUpdateResponse, summary="Activate/deactivate user")
def update_user_status(
    user_id: UUID,
    status_data: UserActivationRequest,
    current_user: Users = Depends(require_admin),
    db: Session = Depends(get_db)
) -> UserUpdateResponse:
    """
    Activate or deactivate a user account (admin only).
    
    Path Parameters:
        user_id: UUID of the user to update
        
    Request Body:
        status_data: is_active boolean flag
        
    Returns:
        UserUpdateResponse: Updated user and success message
        
    Raises:
        403: User not admin
        404: User not found
    """
    try:
        user_service = UserService(db)
        
        if status_data.is_active:
            updated_user = user_service.activate_user(user_id)
            action = "activated"
        else:
            updated_user = user_service.deactivate_user(user_id)
            action = "deactivated"
        
        return UserUpdateResponse(
            message=f"User {action} successfully",
            user=updated_user
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )


@router.delete("/{user_id}", response_model=UserDeleteResponse, summary="Deactivate user account")
def delete_user(
    user_id: UUID,
    current_user: Users = Depends(require_admin),
    db: Session = Depends(get_db)
) -> UserDeleteResponse:
    """
    Deactivate a user account (soft delete, admin only).
    Note: This deactivates the account rather than permanently deleting it.
    
    Path Parameters:
        user_id: UUID of the user to deactivate
        
    Returns:
        UserDeleteResponse: Deactivated user and success message
        
    Raises:
        403: User not admin
        404: User not found
    """
    try:
        user_service = UserService(db)
        deactivated_user = user_service.deactivate_user(user_id)
        
        return UserDeleteResponse(
            message="User account deactivated",
            user=deactivated_user
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
