"""
Authentication service - business logic for user management.
"""
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from fastapi import HTTPException, status
from passlib.context import CryptContext
from typing import Optional
import os

from models.user import User
from models.account import Account, AccountType
from .schemas import UserCreate, UserLogin, UserRead, UserUpdate, PasswordChange

# Password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    """Hash a password using bcrypt."""
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against its hash."""
    return pwd_context.verify(plain_password, hashed_password)


async def create_user(user_data: UserCreate, db: Session) -> UserRead:
    """
    Create a new user and automatically create a checking account.
    
    Args:
        user_data: User registration data
        db: Database session
        
    Returns:
        Created user data
        
    Raises:
        HTTPException: If email or phone already exists
    """
    # Check if email already exists
    existing_user = db.query(User).filter(User.email == user_data.email).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Check if phone already exists (if provided)
    if user_data.phone:
        existing_phone = db.query(User).filter(User.phone == user_data.phone).first()
        if existing_phone:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Phone number already registered"
            )
    
    try:
        # Create new user
        new_user = User(
            name=user_data.name,
            surname=user_data.surname,
            email=user_data.email,
            phone=user_data.phone,
            password_hash=hash_password(user_data.password)
        )
        
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        
        # Create default checking account for the user
        default_account = Account(
            user_id=new_user.id,
            account_type=AccountType.CHECKING.value,
            balance=0.00,
            currency="USD",
            status="active"
        )
        
        db.add(default_account)
        db.commit()
        
        return UserRead.model_validate(new_user)
    
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User with this email or phone already exists"
        )
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create user: {str(e)}"
        )


def login_user(credentials: UserLogin, db: Session) -> UserRead:
    """
    Authenticate user with email and password.
    
    Args:
        credentials: Login credentials
        db: Database session
        
    Returns:
        Authenticated user data
        
    Raises:
        HTTPException: If credentials are invalid
    """
    # Find user by email
    user = db.query(User).filter(
        User.email == credentials.email,
        User.deleted_at.is_(None)  # Ensure not soft-deleted
    ).first()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )
    
    # Verify password
    if not verify_password(credentials.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )
    
    return UserRead.model_validate(user)


def get_user_by_id(user_id: int, db: Session) -> UserRead:
    """
    Get user by ID.
    
    Args:
        user_id: User ID
        db: Database session
        
    Returns:
        User data
        
    Raises:
        HTTPException: If user not found
    """
    user = db.query(User).filter(
        User.id == user_id,
        User.deleted_at.is_(None)
    ).first()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    return UserRead.model_validate(user)


def get_user_by_email(email: str, db: Session) -> Optional[UserRead]:
    """Get user by email."""
    user = db.query(User).filter(
        User.email == email,
        User.deleted_at.is_(None)
    ).first()
    
    if not user:
        return None
    
    return UserRead.model_validate(user)


def update_user(user_id: int, user_data: UserUpdate, db: Session) -> UserRead:
    """
    Update user profile.
    
    Args:
        user_id: User ID
        user_data: Updated user data
        db: Database session
        
    Returns:
        Updated user data
        
    Raises:
        HTTPException: If user not found
    """
    user = db.query(User).filter(
        User.id == user_id,
        User.deleted_at.is_(None)
    ).first()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Update fields
    if user_data.name is not None:
        user.name = user_data.name
    if user_data.surname is not None:
        user.surname = user_data.surname
    if user_data.phone is not None:
        # Check if phone already exists
        existing_phone = db.query(User).filter(
            User.phone == user_data.phone,
            User.id != user_id
        ).first()
        if existing_phone:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Phone number already in use"
            )
        user.phone = user_data.phone
    
    try:
        db.commit()
        db.refresh(user)
        return UserRead.model_validate(user)
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update user: {str(e)}"
        )


def change_password(user_id: int, password_data: PasswordChange, db: Session) -> dict:
    """
    Change user password.
    
    Args:
        user_id: User ID
        password_data: Password change data
        db: Database session
        
    Returns:
        Success message
        
    Raises:
        HTTPException: If old password is incorrect
    """
    user = db.query(User).filter(
        User.id == user_id,
        User.deleted_at.is_(None)
    ).first()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Verify old password
    if not verify_password(password_data.old_password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Incorrect current password"
        )
    
    # Update password
    user.password_hash = hash_password(password_data.new_password)
    
    try:
        db.commit()
        return {"message": "Password changed successfully"}
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to change password: {str(e)}"
        )


def update_avatar(user_id: int, filename: str, db: Session) -> UserRead:
    """
    Update user avatar.
    
    Args:
        user_id: User ID
        filename: Avatar filename
        db: Database session
        
    Returns:
        Updated user data
        
    Raises:
        HTTPException: If user not found
    """
    user = db.query(User).filter(
        User.id == user_id,
        User.deleted_at.is_(None)
    ).first()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Delete old avatar if exists
    if user.avatar:
        old_avatar_path = f"uploads/avatars/{user.avatar}"
        if os.path.exists(old_avatar_path):
            os.remove(old_avatar_path)
    
    # Update avatar
    user.avatar = filename
    
    try:
        db.commit()
        db.refresh(user)
        return UserRead.model_validate(user)
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update avatar: {str(e)}"
        )


def delete_user(user_id: int, db: Session) -> dict:
    """
    Soft delete user.
    
    Args:
        user_id: User ID
        db: Database session
        
    Returns:
        Success message
        
    Raises:
        HTTPException: If user not found
    """
    from datetime import datetime
    
    user = db.query(User).filter(
        User.id == user_id,
        User.deleted_at.is_(None)
    ).first()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Soft delete
    user.deleted_at = datetime.utcnow()
    
    try:
        db.commit()
        return {"message": "User deleted successfully"}
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete user: {str(e)}"
        )

