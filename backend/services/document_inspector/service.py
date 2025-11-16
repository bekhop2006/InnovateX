"""
Business logic for Document Inspector service.
"""
import os
import time
from typing import List
from PIL import Image

from .detector import get_detector
from .utils import pdf_to_images, get_page_size
from .schemas import DetectionResponse, PageDetection, PageSize, Detection


class DocumentInspectorService:
    """Service for detecting document elements."""
    
    def __init__(self):
        self.detector = get_detector()
    
    def process_document(
        self,
        pdf_path: str,
        conf_threshold: float = 0.25
    ) -> DetectionResponse:
        """
        Process a PDF document and detect signatures, stamps, and QR codes.
        
        Args:
            pdf_path: Path to PDF file
            conf_threshold: Confidence threshold for detections
            
        Returns:
            DetectionResponse with all detections
        """
        start_time = time.time()
        
        # Get document name
        document_name = os.path.basename(pdf_path)
        
        # Convert PDF to images
        page_images = pdf_to_images(pdf_path)
        
        # Process each page
        pages_results = []
        
        for image, page_num in page_images:
            # Get page size
            width, height = get_page_size(image)
            page_size = PageSize(width=width, height=height)
            
            # Detect elements (fallback to empty detections if model not loaded)
            if self.is_ready():
                detections = self.detector.detect(image, conf_threshold=conf_threshold)
            else:
                detections = []
            
            # Convert to Detection models
            detection_objects = [
                Detection(
                    id=det["id"],
                    category=det["category"],
                    bbox=det["bbox"],
                    confidence=det["confidence"]
                )
                for det in detections
            ]
            
            # Create page detection
            page_detection = PageDetection(
                page_number=page_num,
                page_size=page_size,
                annotations=detection_objects
            )
            
            pages_results.append(page_detection)
        
        # Calculate processing time
        processing_time = time.time() - start_time
        
        # Create response
        response = DetectionResponse(
            document_name=document_name,
            total_pages=len(page_images),
            pages=pages_results,
            processing_time=processing_time
        )
        
        return response
    
    def process_and_visualize(
        self,
        pdf_path: str,
        conf_threshold: float = 0.25,
        page_number: int = 1
    ) -> Image.Image:
        """
        Process a PDF page and return visualization with bounding boxes.
        
        Args:
            pdf_path: Path to PDF file
            conf_threshold: Confidence threshold
            page_number: Page number to visualize (1-indexed)
            
        Returns:
            PIL Image with detections visualized
        """
        # Convert PDF to images
        page_images = pdf_to_images(pdf_path)
        
        # Find requested page
        for image, page_num in page_images:
            if page_num == page_number:
                # Detect and visualize
                return self.detector.detect_and_visualize(
                    image,
                    conf_threshold=conf_threshold
                )
        
        raise ValueError(f"Page {page_number} not found in document")
    
    def is_ready(self) -> bool:
        """Check if service is ready (model loaded)."""
        return self.detector.is_loaded()
    
    def get_model_path(self) -> str:
        """Get path to loaded model."""
        return self.detector.model_path or "No model loaded"

