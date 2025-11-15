"""
Router for process_document endpoint.
"""
from fastapi import APIRouter, UploadFile, File, HTTPException

from .schemas import ProcessDocumentResponse, ProcessDocumentElement
from .image_processor import initialize_models, process_image, is_models_ready


router = APIRouter()

# Initialize models on module import
initialize_models()


@router.post("/v1/process_document", response_model=ProcessDocumentResponse)
async def process_document(
    file: UploadFile = File(..., description="Image file to process")
):
    """
    Process an image document and extract QR codes, stamps, and signatures.
    
    Args:
        file: Uploaded image file (JPEG, PNG, etc.)
        
    Returns:
        JSON with detected elements and their content
    """
    # Check if models are ready
    if not is_models_ready():
        raise HTTPException(
            status_code=503,
            detail="Models not loaded. Please ensure YOLO model is available."
        )
    
    # Validate file type (image)
    if not file.content_type or not file.content_type.startswith('image/'):
        raise HTTPException(
            status_code=400,
            detail="Only image files are supported (JPEG, PNG, etc.)"
        )
    
    try:
        # Read file content
        image_bytes = await file.read()
        
        # Process image
        result = process_image(image_bytes)
        
        # Convert to response model
        elements = [
            ProcessDocumentElement(
                type=elem["type"],
                bbox=elem["bbox"],
                content=elem["content"]
            )
            for elem in result["elements"]
        ]
        
        return ProcessDocumentResponse(
            status=result["status"],
            elements=elements
        )
    
    except ValueError as e:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid image file: {str(e)}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error processing document: {str(e)}"
        )

