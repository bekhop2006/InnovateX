"""
Utility functions for Document Inspector service.
"""
import fitz  # PyMuPDF
from PIL import Image
import io
from typing import List, Tuple
import os


def pdf_to_images(pdf_path: str) -> List[Tuple[Image.Image, int]]:
    """
    Convert PDF pages to PIL Images.
    
    Args:
        pdf_path: Path to PDF file
        
    Returns:
        List of tuples (image, page_number)
    """
    if not os.path.exists(pdf_path):
        raise FileNotFoundError(f"PDF file not found: {pdf_path}")
    
    images = []
    
    try:
        doc = fitz.open(pdf_path)
        
        for page_num in range(len(doc)):
            page = doc.load_page(page_num)
            
            # Render page to pixmap at high resolution
            mat = fitz.Matrix(2.0, 2.0)  # 2x zoom for better quality
            pix = page.get_pixmap(matrix=mat)
            
            # Convert to PIL Image
            img_bytes = pix.tobytes("png")
            image = Image.open(io.BytesIO(img_bytes)).convert("RGB")
            
            images.append((image, page_num + 1))  # 1-indexed page numbers
        
        doc.close()
        
    except Exception as e:
        raise Exception(f"Error converting PDF to images: {str(e)}")
    
    return images


def get_page_size(image: Image.Image) -> Tuple[int, int]:
    """
    Get image dimensions.
    
    Args:
        image: PIL Image
        
    Returns:
        Tuple of (width, height)
    """
    return image.size

