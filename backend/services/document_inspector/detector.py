"""
YOLOv8 detector for document elements (signatures, stamps, QR codes).
"""
import os
from typing import List, Optional, Dict, Any
from PIL import Image
import numpy as np


class DocumentDetector:
    """Document element detector using YOLOv8."""
    
    def __init__(self, model_path: Optional[str] = None):
        """
        Initialize detector with YOLOv8 model.
        
        Args:
            model_path: Path to trained YOLO model (.pt file)
        """
        self.model = None
        self.model_path = model_path
        self.class_names = {0: "signature", 1: "stamp", 2: "qr"}
        
        if model_path and os.path.exists(model_path):
            self.load_model(model_path)
    
    def load_model(self, model_path: str):
        """
        Load YOLOv8 model.
        
        Args:
            model_path: Path to model file
        """
        try:
            from ultralytics import YOLO
            self.model = YOLO(model_path)
            self.model_path = model_path
            print(f"✅ Model loaded successfully from {model_path}")
        except ImportError:
            raise ImportError("ultralytics package not installed. Install with: pip install ultralytics")
        except Exception as e:
            raise Exception(f"Error loading model: {str(e)}")
    
    def is_loaded(self) -> bool:
        """Check if model is loaded."""
        return self.model is not None
    
    def detect(self, image: Image.Image, conf_threshold: float = 0.25) -> List[Dict[str, Any]]:
        """
        Detect document elements in image.
        
        Args:
            image: PIL Image to process
            conf_threshold: Confidence threshold for detections
            
        Returns:
            List of detections with bbox, class, and confidence
        """
        if not self.is_loaded():
            raise RuntimeError("Model not loaded. Call load_model() first.")
        
        # Run inference
        results = self.model.predict(
            source=image,
            conf=conf_threshold,
            verbose=False
        )
        
        detections = []
        
        # Parse results
        if len(results) > 0:
            result = results[0]
            boxes = result.boxes
            
            for idx, box in enumerate(boxes):
                # Get box coordinates (xyxy format)
                xyxy = box.xyxy[0].cpu().numpy()
                x1, y1, x2, y2 = xyxy
                
                # Convert to xywh format
                x = float(x1)
                y = float(y1)
                width = float(x2 - x1)
                height = float(y2 - y1)
                
                # Get class and confidence
                cls_id = int(box.cls[0].cpu().numpy())
                confidence = float(box.conf[0].cpu().numpy())
                
                # Get class name
                category = self.class_names.get(cls_id, f"class_{cls_id}")
                
                detection = {
                    "id": f"detection_{idx + 1}",
                    "category": category,
                    "bbox": {
                        "x": x,
                        "y": y,
                        "width": width,
                        "height": height
                    },
                    "confidence": confidence
                }
                
                detections.append(detection)
        
        return detections
    
    def detect_and_visualize(
        self,
        image: Image.Image,
        conf_threshold: float = 0.25,
        save_path: Optional[str] = None
    ) -> Image.Image:
        """
        Detect elements and return image with bounding boxes drawn.
        
        Args:
            image: Input image
            conf_threshold: Confidence threshold
            save_path: Optional path to save visualization
            
        Returns:
            PIL Image with detections drawn
        """
        if not self.is_loaded():
            raise RuntimeError("Model not loaded. Call load_model() first.")
        
        # Run inference with visualization
        results = self.model.predict(
            source=image,
            conf=conf_threshold,
            verbose=False
        )
        
        # Get annotated image
        if len(results) > 0:
            result = results[0]
            annotated_image = result.plot()  # Returns numpy array in BGR
            
            # Convert BGR to RGB
            annotated_image = annotated_image[:, :, ::-1]
            
            # Convert to PIL Image
            img_pil = Image.fromarray(annotated_image)
            
            if save_path:
                img_pil.save(save_path)
            
            return img_pil
        
        return image


# Global detector instance
_detector_instance: Optional[DocumentDetector] = None


def get_detector() -> DocumentDetector:
    """Get global detector instance."""
    global _detector_instance
    
    if _detector_instance is None:
        # Try to load default model
        default_model_path = os.path.join("models", "document_inspector_yolo.pt")
        
        if os.path.exists(default_model_path):
            _detector_instance = DocumentDetector(default_model_path)
        else:
            _detector_instance = DocumentDetector()
            print(f"⚠️  Model not found at {default_model_path}. Detector created without model.")
    
    return _detector_instance

