import secrets
import hashlib
import base64
import os
from urllib.parse import urlencode, quote
from dotenv import load_dotenv
from exceptions import GitHubOAuthException

load_dotenv()

# GitHub OAuth constants
GITHUB_OAUTH_AUTHORIZE_URL = "https://github.com/login/oauth/authorize"
GITHUB_OAUTH_TOKEN_URL = "https://github.com/login/oauth/access_token"
GITHUB_API_USER_URL = "https://api.github.com/user"

# Environment variables
GITHUB_CLIENT_ID = os.getenv("GITHUB_CLIENT_ID")
GITHUB_CLIENT_SECRET = os.getenv("GITHUB_CLIENT_SECRET")
GITHUB_REDIRECT_URI = os.getenv("GITHUB_REDIRECT_URI", "http://localhost:8000/auth/github/callback")

# PKCE constants
PKCE_CODE_VERIFIER_LENGTH = 128  # Between 43-128 characters
PKCE_STATE_LENGTH = 32  # Random state for CSRF protection


def generate_pkce_values() -> dict:
    """
    Generate PKCE code verifier and code challenge.
    Also generates a random state for CSRF protection.
    
    Returns:
        Dictionary with keys:
            - state: Random CSRF protection token
            - code_verifier: Random value for PKCE flow
            - code_challenge: Derived from code_verifier
    """
    # Generate random state (CSRF protection)
    state = secrets.token_urlsafe(PKCE_STATE_LENGTH)
    
    # Generate code verifier (PKCE)
    code_verifier = secrets.token_urlsafe(PKCE_CODE_VERIFIER_LENGTH)
    
    # Create code challenge from verifier
    code_challenge = create_code_challenge(code_verifier)
    
    return {
        "state": state,
        "code_verifier": code_verifier,
        "code_challenge": code_challenge
    }


def create_code_challenge(code_verifier: str) -> str:
    """
    Create a code challenge from a code verifier using S256 method.
    
    Args:
        code_verifier: The random PKCE verifier string
        
    Returns:
        Base64 URL-encoded SHA256 hash of the verifier
    """
    # Create SHA256 hash of the verifier
    digest = hashlib.sha256(code_verifier.encode()).digest()
    
    # Base64 URL-encode (no padding)
    code_challenge = base64.urlsafe_b64encode(digest).decode().rstrip("=")
    
    return code_challenge


def verify_state(stored_state: str, callback_state: str) -> bool:
    """
    Verify that the state from GitHub callback matches stored state.
    Prevents CSRF attacks.
    
    Args:
        stored_state: State generated at authorization start
        callback_state: State returned from GitHub callback
        
    Returns:
        True if states match
        
    Raises:
        GitHubOAuthException: If states don't match
    """
    if not stored_state or not callback_state:
        raise GitHubOAuthException("Missing state parameter")
    
    if stored_state != callback_state:
        raise GitHubOAuthException("State parameter mismatch - possible CSRF attack")
    
    return True


def build_github_auth_url(state: str) -> str:
    """
    Build the GitHub OAuth authorization URL.
    
    Args:
        state: CSRF protection token
        
    Returns:
        Full GitHub authorization URL for redirect
        
    Raises:
        GitHubOAuthException: If required credentials missing
    """
    if not GITHUB_CLIENT_ID:
        raise GitHubOAuthException("GitHub Client ID not configured")
    
    if not GITHUB_REDIRECT_URI:
        raise GitHubOAuthException("GitHub Redirect URI not configured")
    
    # Build query parameters for GitHub OAuth
    params = {
        "client_id": GITHUB_CLIENT_ID,
        "redirect_uri": GITHUB_REDIRECT_URI,
        "scope": "user:email read:user",
        "state": state
    }
    
    # Build full URL with proper encoding
    auth_url = f"{GITHUB_OAUTH_AUTHORIZE_URL}?{urlencode(params)}"
    
    return auth_url


def verify_code_verifier(stored_verifier: str, received_verifier: str) -> bool:
    """
    Verify that the code verifier from callback matches stored verifier.
    
    Args:
        stored_verifier: Code verifier generated at authorization start
        received_verifier: Code verifier from callback (if included)
        
    Returns:
        True if verifiers match or received_verifier is None
    """
    # GitHub doesn't send verifier in callback, but clients might
    if received_verifier is None:
        return True
    
    if stored_verifier != received_verifier:
        raise GitHubOAuthException("Code verifier mismatch")
    
    return True
