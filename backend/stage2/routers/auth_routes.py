from fastapi import APIRouter, Depends, HTTPException, status, Query
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
from datetime import datetime, timezone
import os

from db import get_db
from schemas.auth_schema import (
    TokenResponse,
    RefreshTokenRequest,
    RefreshTokenResponse,
    LogoutRequest,
    LogoutResponse,
    GitHubAuthCallbackRequest,
    UserAuthResponse,
    ExchangeRequest
)
from services.auth_sevice import AuthService
from auth.oauth import generate_pkce_values, verify_state, build_github_auth_url
from auth.dependencies import get_current_user
from auth.permissions import ANALYST
from models.user_model import Users
from exceptions import (
    GitHubOAuthException,
    UnauthorizedException,
    InvalidTokenException,
)

router = APIRouter(prefix="/auth", tags=["auth"])

# Temporary in-memory storage for PKCE values
# In production, use Redis or database
PKCE_SESSIONS = {}


def serialize_user(user: Users) -> UserAuthResponse:
    """Convert Users model to UserAuthResponse schema."""
    return UserAuthResponse(
        id=str(user.id),
        username=user.username,
        email=user.email,
        avatar_url=user.avatar_url,
        role=user.role,
        is_active=user.is_active
    )


@router.get("/github")
def github_oauth_redirect():
    """
    Initiate GitHub OAuth flow.
    Generates PKCE values, stores them, and redirects to GitHub authorization URL.
    
    Returns:
        RedirectResponse to GitHub authorization URL
    """
    # Generate PKCE values
    pkce_values = generate_pkce_values()
    
    # Store PKCE values in session (in-memory for now)
    # In production, use Redis with TTL or database
    state = pkce_values["state"]
    PKCE_SESSIONS[state] = {
        "code_verifier": pkce_values["code_verifier"],
        "code_challenge": pkce_values["code_challenge"],
        "created_at": datetime.now(timezone.utc)
    }
    
    # Build GitHub auth URL
    try:
        auth_url = build_github_auth_url(state)
    except GitHubOAuthException as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"status": "error", "message": e.message}
        )
    
    # Redirect to GitHub
    return RedirectResponse(url=auth_url)


@router.get("/github/callback")
def github_oauth_callback(
    code: str = Query(..., description="Authorization code from GitHub"),
    state: str = Query(..., description="State parameter for CSRF protection"),
    db: Session = Depends(get_db)
):
    """
    Handle GitHub OAuth callback.
    Exchanges code for token, fetches user info, creates/updates user, issues tokens.
    
    Args:
        code: Authorization code from GitHub
        state: State parameter from GitHub (CSRF protection)
        db: Database session
        
    Returns:
        TokenResponse with access_token, refresh_token, and user info
    """
    # Verify state
    if state not in PKCE_SESSIONS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"status": "error", "message": "Invalid state parameter"}
        )
    
    pkce_session = PKCE_SESSIONS[state]
    code_verifier = pkce_session.get("code_verifier")
    
    # Clean up session
    del PKCE_SESSIONS[state]
    
    try:
        auth_service = AuthService(db)
        
        # Exchange code for GitHub access token
        github_token = auth_service.get_github_access_token(code, code_verifier)
        
        # Fetch user info from GitHub
        github_user_data = auth_service.get_github_user_info(github_token)
        
        # Create or update user
        user, is_new = auth_service.create_or_update_user(github_user_data)
        
        # Issue tokens
        tokens = auth_service.issue_tokens(str(user.id))
        
        # Build response
        return TokenResponse(
            status="success",
            access_token=tokens["access_token"],
            refresh_token=tokens["refresh_token"],
            user=serialize_user(user),
            message="GitHub authentication successful"
        )
        
    except GitHubOAuthException as e:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail={"status": "error", "message": e.message}
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"status": "error", "message": "Authentication failed"}
        )


@router.post("/refresh", response_model=RefreshTokenResponse)
def refresh_tokens(
    request: RefreshTokenRequest,
    db: Session = Depends(get_db)
):
    """
    Refresh access and refresh tokens.
    Old refresh token is immediately revoked.
    
    Args:
        request: Contains old refresh_token
        db: Database session
        
    Returns:
        RefreshTokenResponse with new token pair
    """
    try:
        auth_service = AuthService(db)
        
        # Validate and refresh
        tokens = auth_service.refresh_token_pair(request.refresh_token)
        
        return RefreshTokenResponse(
            status="success",
            access_token=tokens["access_token"],
            refresh_token=tokens["refresh_token"],
            message="Tokens refreshed successfully"
        )
        
    except UnauthorizedException as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={"status": "error", "message": e.message}
        )
    except InvalidTokenException as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={"status": "error", "message": e.message}
        )


@router.post("/logout", response_model=LogoutResponse)
def logout(
    request: LogoutRequest,
    current_user: Users = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Logout user by revoking refresh token.
    
    Args:
        request: Contains refresh_token to revoke
        current_user: Currently authenticated user (ensures auth)
        db: Database session
        
    Returns:
        LogoutResponse with success message
    """
    try:
        auth_service = AuthService(db)
        auth_service.revoke_token(request.refresh_token)
        
        return LogoutResponse(
            status="success",
            message="Logged out successfully"
        )
        
    except Exception as e:
        # Still return success even if revocation fails
        # (token will expire anyway)
        return LogoutResponse(
            status="success",
            message="Logged out successfully"
        )


@router.get("/me")
def get_current_user_info(current_user: Users = Depends(get_current_user)):
    """
    Get current authenticated user's information.
    Requires valid access token.
    
    Args:
        current_user: Current authenticated user
        
    Returns:
        UserAuthResponse with user details
    """
    return serialize_user(current_user)

@router.post("/github/exchange")
def github_exchange(payload: ExchangeRequest, db: Session = Depends(get_db)):
    auth_service = AuthService(db)

    github_token = auth_service.get_github_access_token(payload.code, payload.code_verifier)
    github_user = auth_service.get_github_user_info(github_token)

    user, _ = auth_service.create_or_update_user(github_user)

    tokens = auth_service.issue_tokens(str(user.id))

    return {
        "access_token": tokens["access_token"],
        "refresh_token": tokens["refresh_token"],
        "user": serialize_user(user)
    }