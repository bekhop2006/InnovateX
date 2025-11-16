"""
Schemas for admin service.
"""
from pydantic import BaseModel
from typing import List
from datetime import datetime


class UserListItem(BaseModel):
    """Schema for user in list."""
    id: int
    name: str
    email: str
    role: str
    created_at: datetime
    total_scans: int = 0
    
    class Config:
        from_attributes = True


class SystemStats(BaseModel):
    """Schema for system statistics."""
    total_users: int
    total_admin: int
    total_regular_users: int
    total_scans: int
    total_pages_scanned: int
    total_qr_detected: int
    total_signatures_detected: int
    total_stamps_detected: int
    storage_used_mb: float

