"""
Script to train YOLOv8 model for document element detection.
"""
import os
from pathlib import Path
from ultralytics import YOLO
import torch


def train_yolo_model(
    data_yaml: str,
    model_name: str = "yolov8n.pt",
    epochs: int = 100,
    imgsz: int = 640,
    batch: int = 16,
    output_dir: str = "runs/train"
):
    """
    Train YOLOv8 model on document inspector dataset.
    
    Args:
        data_yaml: Path to data.yaml file
        model_name: Pre-trained YOLO model to use (yolov8n.pt, yolov8s.pt, etc.)
        epochs: Number of training epochs
        imgsz: Input image size
        batch: Batch size
        output_dir: Output directory for training results
    """
    print("=" * 60)
    print("Document Inspector - Model Training")
    print("=" * 60)
    
    # Check if CUDA is available
    device = 'cuda' if torch.cuda.is_available() else 'cpu'
    print(f"\n🖥️  Using device: {device}")
    
    if device == 'cuda':
        print(f"   GPU: {torch.cuda.get_device_name(0)}")
        print(f"   CUDA Version: {torch.version.cuda}")
    
    # Validate data.yaml
    if not os.path.exists(data_yaml):
        raise FileNotFoundError(f"data.yaml not found: {data_yaml}")
    
    print(f"\n📂 Dataset config: {data_yaml}")
    print(f"🤖 Base model: {model_name}")
    print(f"📊 Training parameters:")
    print(f"   - Epochs: {epochs}")
    print(f"   - Image size: {imgsz}")
    print(f"   - Batch size: {batch}")
    print(f"   - Device: {device}")
    
    # Load pre-trained model
    print(f"\n📥 Loading pre-trained model: {model_name}...")
    model = YOLO(model_name)
    
    # Train the model
    print("\n🚀 Starting training...\n")
    
    results = model.train(
        data=data_yaml,
        epochs=epochs,
        imgsz=imgsz,
        batch=batch,
        device=device,
        project=output_dir,
        name="document_inspector",
        exist_ok=True,
        patience=20,  # Early stopping patience
        save=True,
        save_period=10,  # Save checkpoint every 10 epochs
        plots=True,  # Generate training plots
        verbose=True,
        # Data augmentation
        hsv_h=0.015,
        hsv_s=0.7,
        hsv_v=0.4,
        degrees=0.0,  # No rotation for documents
        translate=0.1,
        scale=0.5,
        shear=0.0,  # No shearing for documents
        perspective=0.0,  # No perspective for documents
        flipud=0.0,  # No vertical flip for documents
        fliplr=0.0,  # No horizontal flip (text direction matters)
        mosaic=1.0,
        mixup=0.0
    )
    
    print("\n✅ Training complete!")
    print(f"\n📊 Training results saved to: {output_dir}/document_inspector")
    
    # Validate the model
    print("\n🔍 Running validation...")
    metrics = model.val()
    
    print(f"\n📈 Validation Metrics:")
    print(f"   - mAP50: {metrics.box.map50:.4f}")
    print(f"   - mAP50-95: {metrics.box.map:.4f}")
    
    # Save the best model to models directory
    project_root = Path(__file__).parent.parent.parent.parent
    models_dir = project_root / "models"
    models_dir.mkdir(exist_ok=True)
    
    best_model_path = Path(output_dir) / "document_inspector" / "weights" / "best.pt"
    output_model_path = models_dir / "document_inspector_yolo.pt"
    
    if best_model_path.exists():
        # Copy best model
        import shutil
        shutil.copy(best_model_path, output_model_path)
        print(f"\n💾 Best model saved to: {output_model_path}")
    else:
        print(f"\n⚠️  Best model not found at {best_model_path}")
    
    return results


def evaluate_model(model_path: str, data_yaml: str):
    """
    Evaluate trained model on validation set.
    
    Args:
        model_path: Path to trained model
        data_yaml: Path to data.yaml file
    """
    print("=" * 60)
    print("Document Inspector - Model Evaluation")
    print("=" * 60)
    
    if not os.path.exists(model_path):
        raise FileNotFoundError(f"Model not found: {model_path}")
    
    print(f"\n📂 Model: {model_path}")
    print(f"📂 Dataset: {data_yaml}")
    
    # Load model
    model = YOLO(model_path)
    
    # Validate
    print("\n🔍 Running evaluation...")
    metrics = model.val(data=data_yaml)
    
    print(f"\n📈 Evaluation Results:")
    print(f"   - Precision: {metrics.box.mp:.4f}")
    print(f"   - Recall: {metrics.box.mr:.4f}")
    print(f"   - mAP50: {metrics.box.map50:.4f}")
    print(f"   - mAP50-95: {metrics.box.map:.4f}")
    
    # Per-class metrics
    print(f"\n📊 Per-Class Metrics:")
    class_names = ["signature", "stamp", "qr"]
    
    for i, class_name in enumerate(class_names):
        if i < len(metrics.box.maps):
            print(f"   - {class_name}: mAP50-95 = {metrics.box.maps[i]:.4f}")
    
    return metrics


def test_inference(model_path: str, test_image: str, output_dir: str = "runs/detect"):
    """
    Test model inference on a sample image.
    
    Args:
        model_path: Path to trained model
        test_image: Path to test image
        output_dir: Output directory for results
    """
    print("=" * 60)
    print("Document Inspector - Test Inference")
    print("=" * 60)
    
    if not os.path.exists(model_path):
        raise FileNotFoundError(f"Model not found: {model_path}")
    
    if not os.path.exists(test_image):
        raise FileNotFoundError(f"Test image not found: {test_image}")
    
    print(f"\n📂 Model: {model_path}")
    print(f"📂 Test image: {test_image}")
    
    # Load model
    model = YOLO(model_path)
    
    # Run inference
    print("\n🔍 Running inference...")
    results = model.predict(
        source=test_image,
        save=True,
        project=output_dir,
        name="test",
        exist_ok=True,
        conf=0.25
    )
    
    print(f"\n✅ Results saved to: {output_dir}/test")
    
    # Print detections
    if len(results) > 0:
        result = results[0]
        print(f"\n📊 Detected {len(result.boxes)} objects:")
        
        for box in result.boxes:
            cls_id = int(box.cls[0])
            conf = float(box.conf[0])
            class_names = ["signature", "stamp", "qr"]
            class_name = class_names[cls_id] if cls_id < len(class_names) else f"class_{cls_id}"
            print(f"   - {class_name}: {conf:.2%}")


def main():
    """Main execution function."""
    # Paths
    project_root = Path(__file__).parent.parent.parent.parent
    dataset_dir = project_root / "dataset" / "yolo_dataset"
    data_yaml = dataset_dir / "data.yaml"
    
    # Check if dataset is prepared
    if not data_yaml.exists():
        print("❌ Dataset not prepared!")
        print("Please run prepare_dataset.py first to prepare the dataset.")
        print(f"\nExpected data.yaml at: {data_yaml}")
        return
    
    # Training parameters
    MODEL_NAME = "yolov8n.pt"  # Options: yolov8n.pt, yolov8s.pt, yolov8m.pt, yolov8l.pt, yolov8x.pt
    EPOCHS = 100
    IMGSZ = 640
    BATCH = 16  # Adjust based on your GPU memory
    
    # Train model
    train_yolo_model(
        data_yaml=str(data_yaml),
        model_name=MODEL_NAME,
        epochs=EPOCHS,
        imgsz=IMGSZ,
        batch=BATCH
    )
    
    # Evaluate trained model
    models_dir = project_root / "models"
    trained_model_path = models_dir / "document_inspector_yolo.pt"
    
    if trained_model_path.exists():
        print("\n" + "=" * 60)
        evaluate_model(str(trained_model_path), str(data_yaml))


if __name__ == "__main__":
    main()

