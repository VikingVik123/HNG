from sqlalchemy.orm import Session
from uuid import UUID
from models.user_model import Users
from exceptions import UnauthorizedException


class UserService:
    """Service for user management operations"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def get_user_by_id(self, user_id: UUID) -> Users:
        """
        Get user by ID.
        
        Args:
            user_id: User UUID
            
        Returns:
            Users object
            
        Raises:
            UnauthorizedException: If user not found
        """
        user = self.db.query(Users).filter(Users.id == user_id).first()
        if not user:
            raise UnauthorizedException("User not found")
        return user
    
    def get_user_by_username(self, username: str) -> Users:
        """
        Get user by username.
        
        Args:
            username: Username string
            
        Returns:
            Users object or None
        """
        return self.db.query(Users).filter(Users.username == username).first()
    
    def get_all_users(self, skip: int = 0, limit: int = 100) -> tuple[list[Users], int]:
        """
        Get all users with pagination.
        
        Args:
            skip: Number of records to skip
            limit: Maximum records to return
            
        Returns:
            Tuple of (users list, total count)
        """
        total = self.db.query(Users).count()
        users = self.db.query(Users).offset(skip).limit(limit).all()
        return users, total
    
    def update_user(self, user_id: UUID, username: str = None, email: str = None, avatar_url: str = None) -> Users:
        """
        Update user profile information.
        
        Args:
            user_id: User UUID
            username: New username (optional)
            email: New email (optional)
            avatar_url: New avatar URL (optional)
            
        Returns:
            Updated Users object
            
        Raises:
            UnauthorizedException: If user not found
        """
        user = self.get_user_by_id(user_id)
        
        if username:
            user.username = username
        if email is not None:  # Allow setting to None
            user.email = email
        if avatar_url is not None:  # Allow setting to None
            user.avatar_url = avatar_url
        
        self.db.commit()
        self.db.refresh(user)
        return user
    
    def update_user_role(self, user_id: UUID, role: str) -> Users:
        """
        Update user role (admin only).
        
        Args:
            user_id: User UUID
            role: New role ('admin' or 'analyst')
            
        Returns:
            Updated Users object
            
        Raises:
            UnauthorizedException: If user not found
        """
        if role not in ["admin", "analyst"]:
            raise ValueError("Role must be 'admin' or 'analyst'")
        
        user = self.get_user_by_id(user_id)
        user.role = role
        self.db.commit()
        self.db.refresh(user)
        return user
    
    def deactivate_user(self, user_id: UUID) -> Users:
        """
        Deactivate user account (soft delete).
        
        Args:
            user_id: User UUID
            
        Returns:
            Updated Users object
            
        Raises:
            UnauthorizedException: If user not found
        """
        user = self.get_user_by_id(user_id)
        user.is_active = False
        self.db.commit()
        self.db.refresh(user)
        return user
    
    def activate_user(self, user_id: UUID) -> Users:
        """
        Activate user account.
        
        Args:
            user_id: User UUID
            
        Returns:
            Updated Users object
            
        Raises:
            UnauthorizedException: If user not found
        """
        user = self.get_user_by_id(user_id)
        user.is_active = True
        self.db.commit()
        self.db.refresh(user)
        return user
