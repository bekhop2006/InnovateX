"""
Schemas for scan history service.
"""
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from datetime import datetime


class ScanHistoryCreate(BaseModel):
    """Schema for creating a scan history entry."""
    document_name: str
    file_path: str
    total_pages: int
    qr_count: int = 0
    signature_count: int = 0
    stamp_count: int = 0
    results_json: Dict[str, Any]
    processing_time: Optional[float] = None


class ScanHistoryRead(BaseModel):
    """Schema for reading scan history."""
    id: int
    user_id: int
    document_name: str
    file_path: str
    scan_date: datetime
    expires_at: datetime
    total_pages: int
    qr_count: int
    signature_count: int
    stamp_count: int
    results_json: Dict[str, Any]
    processing_time: Optional[float]
    
    class Config:
        from_attributes = True


class ScanHistoryList(BaseModel):
    """Schema for scan history list (without full results)."""
    id: int
    user_id: int
    document_name: str
    scan_date: datetime
    expires_at: datetime
    total_pages: int
    qr_count: int
    signature_count: int
    stamp_count: int
    processing_time: Optional[float]
    
    class Config:
        from_attributes = True


class ScanHistoryStats(BaseModel):
    """Schema for scan history statistics."""
    total_scans: int
    total_pages: int
    total_qr: int
    total_signatures: int
    total_stamps: int

