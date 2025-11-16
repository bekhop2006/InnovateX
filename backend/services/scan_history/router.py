"""
Scan History router - API endpoints for scan history management.
"""
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from typing import List

from database import get_db
from models.user import User
from services.auth.dependencies import get_current_user
from .service import (
    get_user_scans, get_scan_by_id, get_scan_file_path,
    delete_scan, get_user_stats
)
from .schemas import ScanHistoryRead, ScanHistoryList, ScanHistoryStats

router = APIRouter()


@router.get("/", response_model=List[ScanHistoryList])
async def get_my_scans(
    skip: int = 0,
    limit: int = 50,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get scan history for current user.
    
    - **skip**: Number of records to skip (default: 0)
    - **limit**: Maximum number of records to return (default: 50, max: 100)
    
    Requires authentication.
    Returns list of scans (without full results for performance).
    """
    if limit > 100:
        limit = 100
    
    return get_user_scans(current_user.id, db, skip, limit)


@router.get("/stats", response_model=ScanHistoryStats)
async def get_my_stats(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get scan statistics for current user.
    
    Requires authentication.
    Returns aggregated statistics about user's scans.
    """
    return get_user_stats(current_user.id, db)


@router.get("/{scan_id}", response_model=ScanHistoryRead)
async def get_scan_detail(
    scan_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get detailed information about a specific scan.
    
    - **scan_id**: ID of the scan to retrieve
    
    Requires authentication.
    Returns full scan results including all detections.
    """
    scan = get_scan_by_id(scan_id, current_user.id, db)
    return ScanHistoryRead.model_validate(scan)


@router.get("/{scan_id}/download")
async def download_scan_pdf(
    scan_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Download the original PDF file for a scan.
    
    - **scan_id**: ID of the scan
    
    Requires authentication.
    Returns the PDF file.
    """
    file_path = get_scan_file_path(scan_id, current_user.id, db)
    scan = get_scan_by_id(scan_id, current_user.id, db)
    
    return FileResponse(
        path=file_path,
        filename=scan.document_name,
        media_type="application/pdf"
    )


@router.delete("/{scan_id}")
async def delete_scan_endpoint(
    scan_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Delete a scan and its associated PDF file.
    
    - **scan_id**: ID of the scan to delete
    
    Requires authentication.
    Returns success message.
    """
    return delete_scan(scan_id, current_user.id, db)


@router.get("/health")
async def scan_history_health_check():
    """Health check for scan history service."""
    return {"status": "healthy", "service": "scan_history"}

