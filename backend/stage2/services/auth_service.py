import httpx
import hashlib
import os
from datetime import datetime, timezone
from dotenv import load_dotenv
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from uuid import UUID

from db import get_db
from models.user_model import Users
from models.auth_model import Token
from auth.tokens import encode_token, extract_user_id, TOKEN_TYPE_ACCESS, TOKEN_TYPE_REFRESH
from auth.permissions import ANALYST
from exceptions import (
    GitHubOAuthException,
    UnauthorizedException,
    InvalidTokenException,
    UserNotActiveException,
)

load_dotenv()

# GitHub OAuth endpoints
GITHUB_OAUTH_TOKEN_URL = "https://github.com/login/oauth/access_token"
GITHUB_API_USER_URL = "https://api.github.com/user"

# Environment variables
GITHUB_CLIENT_ID = os.getenv("GITHUB_CLIENT_ID")
GITHUB_CLIENT_SECRET = os.getenv("GITHUB_CLIENT_SECRET")


class AuthService:
    """
    Service to manage authentication and authorization.
    Handles token operations, GitHub OAuth flow, and user management.
    """
    def __init__(self, db: Session):
        self.db = db

    def issue_tokens(self, user_id: str) -> dict:
        """
        Generate access and refresh tokens for a user.
        Stores refresh token hash in database for revocation tracking.
        
        Args:
            user_id: UUID of the user
            
        Returns:
            Dictionary with:
                - access_token: JWT access token string
                - refresh_token: JWT refresh token string
        """
        # Generate tokens
        access_token = encode_token(user_id, TOKEN_TYPE_ACCESS)
        refresh_token = encode_token(user_id, TOKEN_TYPE_REFRESH)
        
        # Hash the refresh token for storage
        token_hash = hashlib.sha256(refresh_token.encode()).hexdigest()
        
        # Extract expiry from token
        from auth.tokens import get_token_expiry_timestamp
        expires_at = get_token_expiry_timestamp(refresh_token)
        
        # Store token hash in database
        token_record = Token(
            user_id=UUID(user_id),
            token_hash=token_hash,
            expires_at=expires_at,
            is_revoked=False
        )
        self.db.add(token_record)
        self.db.commit()
        
        return {
            "access_token": access_token,
            "refresh_token": refresh_token
        }

    def validate_access_token(self, token: str) -> str:
        """
        Validate access token and extract user_id.
        
        Args:
            token: JWT access token string
            
        Returns:
            user_id from token
            
        Raises:
            UnauthorizedException: If token expired
            InvalidTokenException: If token invalid/malformed
        """
        try:
            user_id = extract_user_id(token, TOKEN_TYPE_ACCESS)
            return user_id
        except (UnauthorizedException, InvalidTokenException):
            raise

    def refresh_token_pair(self, refresh_token: str) -> dict:
        """
        Validate refresh token and issue new token pair.
        Marks old token as revoked.
        
        Args:
            refresh_token: JWT refresh token string
            
        Returns:
            Dictionary with new access_token and refresh_token
            
        Raises:
            UnauthorizedException: If token expired or invalid
            InvalidTokenException: If token malformed
        """
        # Decode and extract user_id
        try:
            user_id = extract_user_id(refresh_token, TOKEN_TYPE_REFRESH)
        except (UnauthorizedException, InvalidTokenException):
            raise
        
        # Hash the token to find in database
        token_hash = hashlib.sha256(refresh_token.encode()).hexdigest()
        
        # Find token record
        token_record = self.db.query(Token).filter(
            Token.token_hash == token_hash
        ).first()
        
        if not token_record:
            raise InvalidTokenException("Token not found in database")
        
        if token_record.is_revoked:
            raise UnauthorizedException("Token has been revoked")
        
        # Mark old token as revoked
        token_record.is_revoked = True
        self.db.commit()
        
        # Issue new token pair
        new_tokens = self.issue_tokens(user_id)
        return new_tokens

    def revoke_token(self, refresh_token: str) -> bool:
        """
        Mark a refresh token as revoked (logout).
        
        Args:
            refresh_token: JWT refresh token string
            
        Returns:
            True if revoked successfully
        """
        # Hash the token
        token_hash = hashlib.sha256(refresh_token.encode()).hexdigest()
        
        # Find and revoke
        token_record = self.db.query(Token).filter(
            Token.token_hash == token_hash
        ).first()
        
        if token_record:
            token_record.is_revoked = True
            self.db.commit()
            return True
        
        return False

    def get_github_access_token(self, code: str, code_verifier: str = None) -> str:
        """
        Exchange GitHub authorization code for access token.
        
        Args:
            code: Authorization code from GitHub callback
            code_verifier: PKCE code verifier (optional, GitHub doesn't require it)
            
        Returns:
            GitHub access token string
            
        Raises:
            GitHubOAuthException: If GitHub API fails
        """
        if not GITHUB_CLIENT_ID or not GITHUB_CLIENT_SECRET:
            raise GitHubOAuthException("GitHub credentials not configured")
        
        # Prepare request body
        data = {
            "client_id": GITHUB_CLIENT_ID,
            "client_secret": GITHUB_CLIENT_SECRET,
            "code": code,
        }
        
        if code_verifier:
            data["code_verifier"] = code_verifier
        
        # Request headers
        headers = {"Accept": "application/json"}
        
        try:
            response = httpx.post(GITHUB_OAUTH_TOKEN_URL, data=data, headers=headers)
            response.raise_for_status()
            
            result = response.json()
            
            if "error" in result:
                raise GitHubOAuthException(f"GitHub error: {result.get('error_description', result['error'])}")
            
            access_token = result.get("access_token")
            if not access_token:
                raise GitHubOAuthException("No access token in GitHub response")
            
            return access_token
            
        except httpx.HTTPError as e:
            raise GitHubOAuthException(f"GitHub API error: {str(e)}")

    def get_github_user_info(self, github_access_token: str) -> dict:
        """
        Fetch user information from GitHub API.
        
        Args:
            github_access_token: GitHub OAuth access token
            
        Returns:
            Dictionary with:
                - github_id: User's GitHub ID
                - username: User's GitHub login
                - email: User's email (may be None if private)
                - avatar_url: User's avatar URL
                
        Raises:
            GitHubOAuthException: If GitHub API fails
        """
        headers = {
            "Authorization": f"Bearer {github_access_token}",
            "Accept": "application/vnd.github.v3+json"
        }
        
        try:
            response = httpx.get(GITHUB_API_USER_URL, headers=headers)
            response.raise_for_status()
            
            user_data = response.json()
            
            return {
                "github_id": str(user_data.get("id")),
                "username": user_data.get("login"),
                "email": user_data.get("email"),
                "avatar_url": user_data.get("avatar_url")
            }
            
        except httpx.HTTPError as e:
            raise GitHubOAuthException(f"Failed to fetch user info: {str(e)}")

    def create_or_update_user(self, github_data: dict) -> tuple:
        """
        Create new user or update existing user.
        
        Args:
            github_data: Dictionary with github_id, username, email, avatar_url
            
        Returns:
            Tuple of (user_object, is_new_user)
            - is_new_user: True if newly created, False if updated
            
        Raises:
            GitHubOAuthException: If user creation fails
        """
        github_id = github_data.get("github_id")
        
        # Try to find existing user
        existing_user = self.db.query(Users).filter(
            Users.github_id == github_id
        ).first()
        
        if existing_user:
            # Update last login
            existing_user.last_login_at = datetime.now(timezone.utc)
            self.db.commit()
            return (existing_user, False)
        
        # Create new user
        try:
            new_user = Users(
                github_id=github_id,
                username=github_data.get("username"),
                email=github_data.get("email"),
                avatar_url=github_data.get("avatar_url"),
                role=ANALYST,  # Default role
                is_active=True,
                last_login_at=datetime.now(timezone.utc),
                created_at=datetime.now(timezone.utc)
            )
            self.db.add(new_user)
            self.db.commit()
            self.db.refresh(new_user)
            return (new_user, True)
            
        except IntegrityError as e:
            self.db.rollback()
            raise GitHubOAuthException(f"Failed to create user: {str(e)}")
        except Exception as e:
            self.db.rollback()
            raise GitHubOAuthException(f"Unexpected error creating user: {str(e)}")

    def get_user_by_id(self, user_id: str) -> Users:
        """
        Fetch user by ID.
        
        Args:
            user_id: UUID of user
            
        Returns:
            Users object
            
        Raises:
            UnauthorizedException: If user not found or inactive
        """
        try:
            user = self.db.query(Users).filter(Users.id == UUID(user_id)).first()
            
            if not user:
                raise UnauthorizedException("User not found")
            
            if not user.is_active:
                raise UserNotActiveException()
            
            return user
            
        except ValueError:
            raise UnauthorizedException("Invalid user ID format")
