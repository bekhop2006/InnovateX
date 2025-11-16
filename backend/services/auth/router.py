"""
Authentication router - API endpoints for user management.
"""
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from sqlalchemy.orm import Session
from typing import List
import os
import uuid
from PIL import Image

from database import get_db
from models.user import User
from .service import (
    create_user, login_user, get_user_by_id, get_user_by_email,
    update_user, change_password, update_avatar, delete_user
)
from .schemas import (
    UserCreate, UserLogin, UserRead, UserUpdate, 
    PasswordChange, AuthResponse, TokenResponse
)
from .jwt import create_access_token
from .dependencies import get_current_user, get_current_admin

router = APIRouter()


@router.post("/register", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
async def register(user_data: UserCreate, db: Session = Depends(get_db)):
    """
    Register a new user.
    
    - **name**: User's first name (required)
    - **surname**: User's surname (optional)
    - **email**: Valid email address (required, unique)
    - **phone**: Phone number (optional, unique)
    - **password**: Password (min 8 characters, must contain letter and digit)
    
    Returns JWT token and user data.
    """
    user = await create_user(user_data, db)
    
    # Create JWT token
    access_token = create_access_token(
        data={"user_id": user.id, "email": user.email, "role": user.role}
    )
    
    return TokenResponse(
        access_token=access_token,
        token_type="bearer",
        user=user
    )


@router.post("/login", response_model=TokenResponse)
async def login(credentials: UserLogin, db: Session = Depends(get_db)):
    """
    Login with email and password.
    
    - **email**: User's email address
    - **password**: User's password
    
    Returns JWT token and user data if credentials are valid.
    """
    user = login_user(credentials, db)
    
    # Create JWT token
    access_token = create_access_token(
        data={"user_id": user.id, "email": user.email, "role": user.role}
    )
    
    return TokenResponse(
        access_token=access_token,
        token_type="bearer",
        user=user
    )


@router.get("/users/{user_id}", response_model=UserRead)
async def get_user(user_id: int, db: Session = Depends(get_db)):
    """
    Get user by ID.
    
    - **user_id**: User ID
    
    Returns user data.
    """
    return get_user_by_id(user_id, db)


@router.get("/users/email/{email}", response_model=UserRead)
async def get_user_by_email_endpoint(email: str, db: Session = Depends(get_db)):
    """
    Get user by email.
    
    - **email**: User's email address
    
    Returns user data if found.
    """
    user = get_user_by_email(email, db)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    return user


@router.put("/users/{user_id}", response_model=UserRead)
async def update_user_profile(
    user_id: int, 
    user_data: UserUpdate, 
    db: Session = Depends(get_db)
):
    """
    Update user profile.
    
    - **user_id**: User ID
    - **name**: New name (optional)
    - **surname**: New surname (optional)
    - **phone**: New phone number (optional)
    
    Returns updated user data.
    """
    return update_user(user_id, user_data, db)


@router.post("/users/{user_id}/change-password")
async def change_user_password(
    user_id: int,
    password_data: PasswordChange,
    db: Session = Depends(get_db)
):
    """
    Change user password.
    
    - **user_id**: User ID
    - **old_password**: Current password
    - **new_password**: New password (min 8 characters)
    
    Returns success message.
    """
    return change_password(user_id, password_data, db)


@router.post("/users/{user_id}/avatar", response_model=UserRead)
async def upload_avatar(
    user_id: int,
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    """
    Upload user avatar.
    
    - **user_id**: User ID
    - **file**: Image file (JPEG, PNG)
    
    Returns updated user data with avatar URL.
    """
    # Validate file type
    allowed_types = ["image/jpeg", "image/png", "image/jpg"]
    if file.content_type not in allowed_types:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid file type. Only JPEG and PNG are allowed."
        )
    
    # Generate unique filename
    file_extension = file.filename.split(".")[-1]
    unique_filename = f"{user_id}_{uuid.uuid4().hex}.{file_extension}"
    file_path = f"uploads/avatars/{unique_filename}"
    
    # Ensure directory exists
    os.makedirs("uploads/avatars", exist_ok=True)
    
    try:
        # Read and save image
        contents = await file.read()
        
        # Validate image
        try:
            image = Image.open(file.file)
            image.verify()
        except Exception:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid image file"
            )
        
        # Reset file pointer and save
        file.file.seek(0)
        with open(file_path, "wb") as f:
            f.write(contents)
        
        # Update user avatar in database
        return update_avatar(user_id, unique_filename, db)
    
    except HTTPException:
        raise
    except Exception as e:
        # Clean up file if database update fails
        if os.path.exists(file_path):
            os.remove(file_path)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to upload avatar: {str(e)}"
        )


@router.delete("/users/{user_id}")
async def delete_user_endpoint(user_id: int, db: Session = Depends(get_db)):
    """
    Soft delete user.
    
    - **user_id**: User ID
    
    Returns success message.
    """
    return delete_user(user_id, db)


@router.get("/me", response_model=UserRead)
async def get_current_user_endpoint(current_user: User = Depends(get_current_user)):
    """
    Get current authenticated user.
    
    Requires valid JWT token in Authorization header.
    
    Returns current user data.
    """
    return UserRead.model_validate(current_user)


@router.post("/refresh", response_model=TokenResponse)
async def refresh_token(current_user: User = Depends(get_current_user)):
    """
    Refresh JWT token.
    
    Requires valid JWT token in Authorization header.
    
    Returns new JWT token with extended expiration.
    """
    # Create new JWT token
    access_token = create_access_token(
        data={"user_id": current_user.id, "email": current_user.email, "role": current_user.role.value}
    )
    
    return TokenResponse(
        access_token=access_token,
        token_type="bearer",
        user=UserRead.model_validate(current_user)
    )


@router.get("/health")
async def auth_health_check():
    """Health check for auth service."""
    return {"status": "healthy", "service": "auth"}

