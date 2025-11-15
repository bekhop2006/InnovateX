"""
Image processing module for document inspection.
Handles YOLO detection, QR code decoding, and OCR recognition.
"""
import os
from pathlib import Path
import numpy as np
import cv2
from typing import List, Optional, Dict, Any
from pyzbar.pyzbar import decode

# Global models
YOLO_MODEL = None
OCR_READER = None


def initialize_models():
    """Initialize global YOLO and EasyOCR models."""
    global YOLO_MODEL, OCR_READER
    
    # Initialize YOLO model
    if YOLO_MODEL is None:
        try:
            from ultralytics import YOLO
            # Get project root (3 levels up from this file)
            project_root = Path(__file__).parent.parent.parent.parent
            default_model_path = project_root / "models" / "document_inspector_yolo.pt"
            
            if default_model_path.exists():
                YOLO_MODEL = YOLO(str(default_model_path))
                print(f"✅ YOLO model loaded from {default_model_path}")
            else:
                print(f"⚠️  YOLO model not found at {default_model_path}")
        except Exception as e:
            print(f"❌ Error loading YOLO model: {str(e)}")
    
    # Initialize EasyOCR reader
    if OCR_READER is None:
        try:
            import easyocr
            # Initialize with Russian and English languages
            OCR_READER = easyocr.Reader(['ru', 'en'], gpu=False)
            print("✅ EasyOCR reader initialized")
        except Exception as e:
            print(f"❌ Error initializing EasyOCR: {str(e)}")


def process_image(image_bytes: bytes) -> Dict[str, Any]:
    """
    Process image and detect elements with content extraction.
    
    Args:
        image_bytes: Image file bytes
        
    Returns:
        Dictionary with status and elements list
    """
    # Check if models are loaded
    if YOLO_MODEL is None:
        raise RuntimeError("YOLO model not loaded. Please initialize models first.")
    
    # Decode image
    nparr = np.frombuffer(image_bytes, np.uint8)
    image_cv2 = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    
    if image_cv2 is None:
        raise ValueError("Could not decode image. Please ensure it's a valid image file.")
    
    # Run YOLO prediction
    results = YOLO_MODEL.predict(image_cv2, verbose=False)
    result = results[0]  # Get first (and only) result
    
    # Container for found elements
    found_elements = []
    
    # Iterate over all detected objects
    if result.boxes is not None and len(result.boxes.cls) > 0:
        for i in range(len(result.boxes.cls)):
            class_id = int(result.boxes.cls[i])
            class_name = YOLO_MODEL.names[class_id]  # Get class name ("qrcode", "stamp", "signature")
            
            # Get bounding box
            bbox = result.boxes.xyxy[i].cpu().numpy().astype(int)  # [x1, y1, x2, y2]
            x1, y1, x2, y2 = bbox
            
            # Crop the object from original image
            cropped_image = image_cv2[y1:y2, x1:x2]
            
            # Process based on class type
            # Normalize class name (model uses "qr", but we want "qrcode" in response)
            if class_name.lower() in ['qr', 'qrcode']:
                # Decode QR code
                try:
                    decoded_qr = decode(cropped_image)
                    if decoded_qr:
                        content = decoded_qr[0].data.decode('utf-8')
                    else:
                        content = "Error: Could not read QR"
                except Exception as e:
                    content = f"Error: {str(e)}"
                
                found_elements.append({
                    "type": "qrcode",
                    "bbox": bbox.tolist(),
                    "content": content
                })
            
            elif class_name.lower() == 'stamp':
                # Use EasyOCR for text recognition
                if OCR_READER is not None:
                    try:
                        ocr_results = OCR_READER.readtext(cropped_image, detail=0)  # detail=0 returns list of strings
                        content = " ".join(ocr_results) if ocr_results else "No text detected"
                    except Exception as e:
                        content = f"Error: {str(e)}"
                else:
                    content = "Error: OCR reader not initialized"
                
                found_elements.append({
                    "type": "stamp",
                    "bbox": bbox.tolist(),
                    "content": content
                })
            
            elif class_name == 'signature':
                # Just mark as detected
                found_elements.append({
                    "type": "signature",
                    "bbox": bbox.tolist(),
                    "content": "Detected"
                })
    
    return {
        "status": "success",
        "elements": found_elements
    }


def is_models_ready() -> bool:
    """Check if models are initialized."""
    return YOLO_MODEL is not None

