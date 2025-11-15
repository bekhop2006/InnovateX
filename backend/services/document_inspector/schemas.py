"""
Pydantic schemas for Document Inspector API.
"""
from typing import List, Optional
from pydantic import BaseModel, Field


class BoundingBox(BaseModel):
    """Bounding box coordinates."""
    x: float = Field(..., description="X coordinate (top-left)")
    y: float = Field(..., description="Y coordinate (top-left)")
    width: float = Field(..., description="Width of bounding box")
    height: float = Field(..., description="Height of bounding box")


class PageSize(BaseModel):
    """Page dimensions."""
    width: int = Field(..., description="Page width in pixels")
    height: int = Field(..., description="Page height in pixels")


class Detection(BaseModel):
    """Single detection result."""
    id: str = Field(..., description="Unique detection ID")
    category: str = Field(..., description="Detection category: signature, stamp, or qr")
    bbox: BoundingBox = Field(..., description="Bounding box coordinates")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Detection confidence score")


class PageDetection(BaseModel):
    """Detection results for a single page."""
    page_number: int = Field(..., description="Page number (1-indexed)")
    page_size: PageSize = Field(..., description="Page dimensions")
    annotations: List[Detection] = Field(default_factory=list, description="List of detections")


class DetectionResponse(BaseModel):
    """Complete detection response."""
    document_name: str = Field(..., description="Original document filename")
    total_pages: int = Field(..., description="Total number of pages processed")
    pages: List[PageDetection] = Field(..., description="Detection results per page")
    processing_time: float = Field(..., description="Total processing time in seconds")


class HealthResponse(BaseModel):
    """Health check response."""
    status: str = Field(..., description="Service status")
    model_loaded: bool = Field(..., description="Whether YOLO model is loaded")
    model_path: Optional[str] = Field(None, description="Path to loaded model")

