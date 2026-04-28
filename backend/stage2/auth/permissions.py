# Role constants
ADMIN = "admin"
ANALYST = "analyst"

# Active roles
ACTIVE_ROLES = [ADMIN, ANALYST]


def is_admin(user_role: str) -> bool:
    """
    Check if user role is admin.
    
    Args:
        user_role: The user's role string
        
    Returns:
        True if user is admin, False otherwise
    """
    return user_role == ADMIN


def is_analyst(user_role: str) -> bool:
    """
    Check if user role is analyst.
    
    Args:
        user_role: The user's role string
        
    Returns:
        True if user is analyst, False otherwise
    """
    return user_role == ANALYST


def is_active_role(user_role: str) -> bool:
    """
    Check if user role is a valid active role.
    
    Args:
        user_role: The user's role string
        
    Returns:
        True if role is in ACTIVE_ROLES, False otherwise
    """
    return user_role in ACTIVE_ROLES

