"""
Admin service - business logic for admin operations.
"""
import os
from typing import List
from sqlalchemy.orm import Session
from sqlalchemy import func
from fastapi import HTTPException, status

from models.user import User, UserRole
from models.scan_history import ScanHistory
from .schemas import UserListItem, SystemStats


def get_all_users(skip: int, limit: int, db: Session) -> List[UserListItem]:
    """
    Get all users with their scan counts.
    
    Args:
        skip: Number of records to skip
        limit: Maximum number of records to return
        db: Database session
        
    Returns:
        List of users with scan statistics
    """
    users = db.query(
        User.id,
        User.name,
        User.email,
        User.role,
        User.created_at,
        func.count(ScanHistory.id).label("total_scans")
    ).outerjoin(
        ScanHistory, User.id == ScanHistory.user_id
    ).filter(
        User.deleted_at.is_(None)
    ).group_by(
        User.id
    ).order_by(
        User.created_at.desc()
    ).offset(skip).limit(limit).all()
    
    return [
        UserListItem(
            id=user.id,
            name=user.name,
            email=user.email,
            role=user.role.value,
            created_at=user.created_at,
            total_scans=user.total_scans or 0
        )
        for user in users
    ]


def get_user_scans_admin(user_id: int, skip: int, limit: int, db: Session) -> List:
    """
    Get scans for a specific user (admin view).
    
    Args:
        user_id: User ID
        skip: Number of records to skip
        limit: Maximum number of records to return
        db: Database session
        
    Returns:
        List of scan history entries
    """
    from services.scan_history.service import get_user_scans
    return get_user_scans(user_id, skip, limit, db)


def get_system_stats(db: Session) -> SystemStats:
    """
    Get system-wide statistics.
    
    Args:
        db: Database session
        
    Returns:
        System statistics
    """
    # User statistics
    total_users = db.query(func.count(User.id)).filter(
        User.deleted_at.is_(None)
    ).scalar()
    
    total_admin = db.query(func.count(User.id)).filter(
        User.deleted_at.is_(None),
        User.role == UserRole.admin
    ).scalar()
    
    total_regular_users = total_users - total_admin
    
    # Scan statistics
    scan_stats = db.query(
        func.count(ScanHistory.id).label("total_scans"),
        func.sum(ScanHistory.total_pages).label("total_pages"),
        func.sum(ScanHistory.qr_count).label("total_qr"),
        func.sum(ScanHistory.signature_count).label("total_signatures"),
        func.sum(ScanHistory.stamp_count).label("total_stamps")
    ).first()
    
    # Calculate storage used
    storage_used_mb = calculate_storage_used()
    
    return SystemStats(
        total_users=total_users or 0,
        total_admin=total_admin or 0,
        total_regular_users=total_regular_users or 0,
        total_scans=scan_stats.total_scans or 0,
        total_pages_scanned=scan_stats.total_pages or 0,
        total_qr_detected=scan_stats.total_qr or 0,
        total_signatures_detected=scan_stats.total_signatures or 0,
        total_stamps_detected=scan_stats.total_stamps or 0,
        storage_used_mb=storage_used_mb
    )


def calculate_storage_used() -> float:
    """
    Calculate total storage used by scanned PDFs.
    
    Returns:
        Storage used in MB
    """
    total_size = 0
    scans_dir = "uploads/scans"
    
    if os.path.exists(scans_dir):
        for root, dirs, files in os.walk(scans_dir):
            for file in files:
                file_path = os.path.join(root, file)
                if os.path.exists(file_path):
                    total_size += os.path.getsize(file_path)
    
    # Convert bytes to MB
    return round(total_size / (1024 * 1024), 2)


def delete_user_admin(user_id: int, db: Session) -> dict:
    """
    Delete a user (soft delete).
    
    Args:
        user_id: User ID
        db: Database session
        
    Returns:
        Success message
        
    Raises:
        HTTPException: If user not found or is an admin
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
    
    # Prevent deleting admin users
    if user.role == UserRole.admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Cannot delete admin users"
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

