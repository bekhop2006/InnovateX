"""
FastAPI router for Document Inspector API endpoints.
"""
import os
import tempfile
from fastapi import APIRouter, UploadFile, File, HTTPException, Query
from fastapi.responses import StreamingResponse
import io

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
    conf_threshold: float = Query(0.25, ge=0.0, le=1.0, description="Confidence threshold")
):
    """
    Detect signatures, stamps, and QR codes in a PDF document.
    
    Args:
        file: Uploaded PDF file
        conf_threshold: Confidence threshold for detections (0.0-1.0)
        
    Returns:
        JSON with detection results for all pages
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
        # Process document
        result = service.process_document(tmp_path, conf_threshold=conf_threshold)
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

