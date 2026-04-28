import jwt
import os
from datetime import datetime, timedelta, timezone
from typing import Dict, Any, Optional
from dotenv import load_dotenv
from exceptions import InvalidTokenException, UnauthorizedException

load_dotenv()

# Token constants
TOKEN_TYPE_ACCESS = "access"
TOKEN_TYPE_REFRESH = "refresh"

# Environment variables
SECRET_KEY = os.getenv("JWT_SECRET_KEY")
ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRY_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRY_MINUTES", 3))
REFRESH_TOKEN_EXPIRY_MINUTES = int(os.getenv("REFRESH_TOKEN_EXPIRY_MINUTES", 5))


def encode_token(
    user_id: str,
    token_type: str = TOKEN_TYPE_ACCESS,
    expiry_minutes: Optional[int] = None
) -> str:
    """
    Encode a JWT token with user_id and token type.
    
    Args:
        user_id: UUID of the user
        token_type: "access" or "refresh"
        expiry_minutes: Override default expiry time
        
    Returns:
        Encoded JWT token string
    """
    if not SECRET_KEY:
        raise ValueError("JWT_SECRET_KEY not set in environment")
    
    # Determine expiry time
    if expiry_minutes is None:
        if token_type == TOKEN_TYPE_ACCESS:
            expiry_minutes = ACCESS_TOKEN_EXPIRY_MINUTES
        else:
            expiry_minutes = REFRESH_TOKEN_EXPIRY_MINUTES
    
    # Create expiry timestamp
    now = datetime.now(timezone.utc)
    expiry = now + timedelta(minutes=expiry_minutes)
    
    # Payload
    payload = {
        "user_id": str(user_id),
        "token_type": token_type,
        "exp": expiry,
        "iat": now
    }
    
    # Encode JWT
    token = jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)
    return token


def decode_token(token: str, token_type: str = TOKEN_TYPE_ACCESS) -> Dict[str, Any]:
    """
    Decode and validate a JWT token.
    
    Args:
        token: JWT token string to decode
        token_type: Expected token type ("access" or "refresh")
        
    Returns:
        Decoded payload dictionary
        
    Raises:
        InvalidTokenException: If token is malformed
        UnauthorizedException: If token is expired or invalid
    """
    if not SECRET_KEY:
        raise ValueError("JWT_SECRET_KEY not set in environment")
    
    try:
        # Decode the token
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    except jwt.ExpiredSignatureError:
        raise UnauthorizedException("Token has expired")
    except jwt.InvalidTokenError as e:
        raise InvalidTokenException(f"Invalid token: {str(e)}")
    
    # Verify token type matches expected type
    stored_token_type = payload.get("token_type")
    if stored_token_type != token_type:
        raise InvalidTokenException(
            f"Invalid token type. Expected {token_type}, got {stored_token_type}"
        )
    
    return payload


def extract_user_id(token: str, token_type: str = TOKEN_TYPE_ACCESS) -> str:
    """
    Extract user_id from a decoded token.
    
    Args:
        token: JWT token string
        token_type: Expected token type
        
    Returns:
        user_id from the token payload
        
    Raises:
        InvalidTokenException: If user_id not in token
        (and exceptions from decode_token)
    """
    payload = decode_token(token, token_type)
    
    user_id = payload.get("user_id")
    if not user_id:
        raise InvalidTokenException("Token missing user_id claim")
    
    return user_id


def get_token_expiry_timestamp(token: str) -> datetime:
    """
    Get the expiry timestamp from a token without validating it.
    Useful for checking token age for refresh logic.
    
    Args:
        token: JWT token string
        
    Returns:
        Expiry datetime in UTC
    """
    try:
        # Decode without verification to just inspect claims
        payload = jwt.decode(token, options={"verify_signature": False})
        exp_timestamp = payload.get("exp")
        
        if not exp_timestamp:
            raise InvalidTokenException("Token missing exp claim")
        
        return datetime.fromtimestamp(exp_timestamp, tz=timezone.utc)
    except jwt.DecodeError as e:
        raise InvalidTokenException(f"Cannot decode token: {str(e)}")
