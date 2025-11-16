"""
Admin router - API endpoints for admin operations.
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from database import get_db
from models.user import User
from services.auth.dependencies import get_current_admin
from services.scan_history.schemas import ScanHistoryList
from .service import (
    get_all_users, get_user_scans_admin, get_system_stats, delete_user_admin
)
from .schemas import UserListItem, SystemStats

router = APIRouter()


@router.get("/users", response_model=List[UserListItem])
async def get_all_users_endpoint(
    skip: int = 0,
    limit: int = 50,
    current_admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """
    Get all users (admin only).
    
    - **skip**: Number of records to skip (default: 0)
    - **limit**: Maximum number of records to return (default: 50, max: 100)
    
    Requires admin authentication.
    Returns list of all users with their scan counts.
    """
    if limit > 100:
        limit = 100
    
    return get_all_users(skip, limit, db)


@router.get("/users/{user_id}/scans", response_model=List[ScanHistoryList])
async def get_user_scans_endpoint(
    user_id: int,
    skip: int = 0,
    limit: int = 50,
    current_admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """
    Get scan history for a specific user (admin only).
    
    - **user_id**: User ID
    - **skip**: Number of records to skip (default: 0)
    - **limit**: Maximum number of records to return (default: 50, max: 100)
    
    Requires admin authentication.
    Returns list of scans for the specified user.
    """
    if limit > 100:
        limit = 100
    
    return get_user_scans_admin(user_id, skip, limit, db)


@router.get("/stats", response_model=SystemStats)
async def get_system_stats_endpoint(
    current_admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """
    Get system-wide statistics (admin only).
    
    Requires admin authentication.
    Returns aggregated statistics about the entire system.
    """
    return get_system_stats(db)


@router.delete("/users/{user_id}")
async def delete_user_endpoint(
    user_id: int,
    current_admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """
    Delete a user (admin only).
    
    - **user_id**: User ID to delete
    
    Requires admin authentication.
    Soft deletes the user (cannot delete admin users).
    """
    return delete_user_admin(user_id, db)


@router.get("/health")
async def admin_health_check():
    """Health check for admin service."""
    return {"status": "healthy", "service": "admin"}

