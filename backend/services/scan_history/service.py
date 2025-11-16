"""
Scan History service - business logic for managing scan history.
"""
import os
import shutil
from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any
from fastapi import HTTPException, status, UploadFile
from sqlalchemy.orm import Session
from sqlalchemy import func

from models.scan_history import ScanHistory
from models.user import User
from .schemas import ScanHistoryCreate, ScanHistoryRead, ScanHistoryList, ScanHistoryStats


def save_scan(
    user_id: int,
    file: UploadFile,
    results: Dict[str, Any],
    db: Session
) -> ScanHistory:
    """
    Save a scan to history and store the PDF file.
    
    Args:
        user_id: User ID
        file: Uploaded PDF file
        results: Detection results from Document Inspector
        db: Database session
        
    Returns:
        Created ScanHistory entry
    """
    # Create user directory if it doesn't exist
    user_dir = f"uploads/scans/{user_id}"
    os.makedirs(user_dir, exist_ok=True)
    
    # Generate unique filename
    timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
    filename = f"{timestamp}_{file.filename}"
    file_path = os.path.join(user_dir, filename)
    
    try:
        # Save PDF file
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        # Count detections by category
        qr_count = 0
        signature_count = 0
        stamp_count = 0
        
        for page in results.get("pages", []):
            for annotation in page.get("annotations", []):
                category = annotation.get("category", "").lower()
                if category == "qr":
                    qr_count += 1
                elif category == "signature":
                    signature_count += 1
                elif category == "stamp":
                    stamp_count += 1
        
        # Create scan history entry
        scan_history = ScanHistory(
            user_id=user_id,
            document_name=file.filename,
            file_path=file_path,
            total_pages=results.get("total_pages", 0),
            qr_count=qr_count,
            signature_count=signature_count,
            stamp_count=stamp_count,
            results_json=results,
            processing_time=results.get("processing_time")
        )
        
        db.add(scan_history)
        db.commit()
        db.refresh(scan_history)
        
        return scan_history
        
    except Exception as e:
        # Clean up file if database insert fails
        if os.path.exists(file_path):
            os.remove(file_path)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to save scan: {str(e)}"
        )


def get_user_scans(
    user_id: int,
    skip: int = 0,
    limit: int = 50,
    db: Session
) -> List[ScanHistoryList]:
    """
    Get scan history for a user.
    
    Args:
        user_id: User ID
        skip: Number of records to skip
        limit: Maximum number of records to return
        db: Database session
        
    Returns:
        List of scan history entries (without full results)
    """
    scans = db.query(ScanHistory).filter(
        ScanHistory.user_id == user_id
    ).order_by(
        ScanHistory.scan_date.desc()
    ).offset(skip).limit(limit).all()
    
    return [ScanHistoryList.model_validate(scan) for scan in scans]


def get_scan_by_id(
    scan_id: int,
    user_id: int,
    db: Session
) -> ScanHistory:
    """
    Get a specific scan by ID.
    
    Args:
        scan_id: Scan ID
        user_id: User ID (for authorization)
        db: Database session
        
    Returns:
        ScanHistory entry with full results
        
    Raises:
        HTTPException: If scan not found or user not authorized
    """
    scan = db.query(ScanHistory).filter(
        ScanHistory.id == scan_id,
        ScanHistory.user_id == user_id
    ).first()
    
    if not scan:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Scan not found"
        )
    
    return scan


def get_scan_file_path(
    scan_id: int,
    user_id: int,
    db: Session
) -> str:
    """
    Get the file path for a scan.
    
    Args:
        scan_id: Scan ID
        user_id: User ID (for authorization)
        db: Database session
        
    Returns:
        File path to the PDF
        
    Raises:
        HTTPException: If scan not found or file doesn't exist
    """
    scan = get_scan_by_id(scan_id, user_id, db)
    
    if not os.path.exists(scan.file_path):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Scan file not found (may have been deleted)"
        )
    
    return scan.file_path


def delete_scan(
    scan_id: int,
    user_id: int,
    db: Session
) -> Dict[str, str]:
    """
    Delete a scan and its associated file.
    
    Args:
        scan_id: Scan ID
        user_id: User ID (for authorization)
        db: Database session
        
    Returns:
        Success message
        
    Raises:
        HTTPException: If scan not found
    """
    scan = get_scan_by_id(scan_id, user_id, db)
    
    # Delete file if it exists
    if os.path.exists(scan.file_path):
        try:
            os.remove(scan.file_path)
        except Exception as e:
            print(f"Warning: Failed to delete file {scan.file_path}: {e}")
    
    # Delete database record
    db.delete(scan)
    db.commit()
    
    return {"message": "Scan deleted successfully"}


def delete_expired_scans(db: Session) -> Dict[str, int]:
    """
    Delete scans that have expired (older than 90 days).
    
    Args:
        db: Database session
        
    Returns:
        Dictionary with count of deleted scans
    """
    now = datetime.utcnow()
    expired_scans = db.query(ScanHistory).filter(
        ScanHistory.expires_at < now
    ).all()
    
    deleted_count = 0
    
    for scan in expired_scans:
        # Delete file if it exists
        if os.path.exists(scan.file_path):
            try:
                os.remove(scan.file_path)
            except Exception as e:
                print(f"Warning: Failed to delete file {scan.file_path}: {e}")
        
        # Delete database record
        db.delete(scan)
        deleted_count += 1
    
    db.commit()
    
    return {"deleted_count": deleted_count}


def get_user_stats(user_id: int, db: Session) -> ScanHistoryStats:
    """
    Get statistics for a user's scan history.
    
    Args:
        user_id: User ID
        db: Database session
        
    Returns:
        Statistics about user's scans
    """
    stats = db.query(
        func.count(ScanHistory.id).label("total_scans"),
        func.sum(ScanHistory.total_pages).label("total_pages"),
        func.sum(ScanHistory.qr_count).label("total_qr"),
        func.sum(ScanHistory.signature_count).label("total_signatures"),
        func.sum(ScanHistory.stamp_count).label("total_stamps")
    ).filter(
        ScanHistory.user_id == user_id
    ).first()
    
    return ScanHistoryStats(
        total_scans=stats.total_scans or 0,
        total_pages=stats.total_pages or 0,
        total_qr=stats.total_qr or 0,
        total_signatures=stats.total_signatures or 0,
        total_stamps=stats.total_stamps or 0
    )

