"""
FastAPI router for Document Inspector API endpoints.
"""
import os
import tempfile
from typing import Optional
from fastapi import APIRouter, UploadFile, File, HTTPException, Query, Depends
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
import io

from database import get_db
from models.user import User
from services.auth.dependencies import get_current_user_optional
from services.scan_history.service import save_scan
from .service import DocumentInspectorService
from .schemas import DetectionResponse, HealthResponse


router = APIRouter()
service = DocumentInspectorService()


@router.get("/health", response_model=HealthResponse)
async def health_check():
    """
    Check if Document Inspector service is ready.
    
    Returns:
        Health status and model information
    """
    is_ready = service.is_ready()
    model_path = service.get_model_path() if is_ready else None
    
    return HealthResponse(
        status="healthy" if is_ready else "model_not_loaded",
        model_loaded=is_ready,
        model_path=model_path
    )


@router.post("/detect", response_model=DetectionResponse)
async def detect_elements(
    file: UploadFile = File(..., description="PDF document to analyze"),
    conf_threshold: float = Query(0.25, ge=0.0, le=1.0, description="Confidence threshold"),
    save_history: bool = Query(True, description="Save scan to history (requires authentication)"),
    current_user: Optional[User] = Depends(get_current_user_optional),
    db: Session = Depends(get_db)
):
    """
    Detect signatures, stamps, and QR codes in a PDF document.
    
    Args:
        file: Uploaded PDF file
        conf_threshold: Confidence threshold for detections (0.0-1.0)
        save_history: Whether to save the scan to history (requires authentication)
        
    Returns:
        JSON with detection results for all pages
        
    Note:
        If authenticated and save_history=True, the scan will be saved to user's history.
        Anonymous users can still use the service, but results won't be saved.
    """
    # If model is not loaded, we'll still process pages and return empty detections
    
    # Validate file type
    if not file.filename.lower().endswith('.pdf'):
        raise HTTPException(
            status_code=400,
            detail="Only PDF files are supported"
        )
    
    # Save uploaded file temporarily
    with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp_file:
        content = await file.read()
        tmp_file.write(content)
        tmp_path = tmp_file.name
    
    try:
        # Process document
        result = service.process_document(tmp_path, conf_threshold=conf_threshold)
        result_dict = result.model_dump()
        
        # Save to history if user is authenticated and save_history is True
        if current_user and save_history:
            # Reset file position for saving
            file.file.seek(0)
            
            try:
                save_scan(
                    user_id=current_user.id,
                    file=file,
                    results=result_dict,
                    db=db
                )
            except Exception as e:
                # Log error but don't fail the request
                print(f"Warning: Failed to save scan to history: {e}")
        
        return result
    
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error processing document: {str(e)}"
        )
    
    finally:
        # Clean up temporary file
        if os.path.exists(tmp_path):
            os.remove(tmp_path)


@router.post("/detect-visualize")
async def detect_and_visualize(
    file: UploadFile = File(..., description="PDF document to analyze"),
    conf_threshold: float = Query(0.25, ge=0.0, le=1.0, description="Confidence threshold"),
    page_number: int = Query(1, ge=1, description="Page number to visualize")
):
    """
    Detect elements and return visualization with bounding boxes.
    
    Args:
        file: Uploaded PDF file
        conf_threshold: Confidence threshold for detections
        page_number: Page number to visualize (1-indexed)
        
    Returns:
        Image with bounding boxes drawn
    """
    # Check if service is ready
    if not service.is_ready():
        raise HTTPException(
            status_code=503,
            detail="Model not loaded. Please ensure the YOLOv8 model is trained and available."
        )
    
    # Validate file type
    if not file.filename.lower().endswith('.pdf'):
        raise HTTPException(
            status_code=400,
            detail="Only PDF files are supported"
        )
    
    # Save uploaded file temporarily
    with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp_file:
        content = await file.read()
        tmp_file.write(content)
        tmp_path = tmp_file.name
    
    try:
        # Process and visualize
        result_image = service.process_and_visualize(
            tmp_path,
            conf_threshold=conf_threshold,
            page_number=page_number
        )
        
        # Convert PIL Image to bytes
        img_byte_arr = io.BytesIO()
        result_image.save(img_byte_arr, format='PNG')
        img_byte_arr.seek(0)
        
        return StreamingResponse(
            img_byte_arr,
            media_type="image/png",
            headers={"Content-Disposition": f"inline; filename=detection_result_page_{page_number}.png"}
        )
    
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error processing document: {str(e)}"
        )
    
    finally:
        # Clean up temporary file
        if os.path.exists(tmp_path):
            os.remove(tmp_path)

