"""
Script to prepare dataset for YOLOv8 training.
Converts PDF pages to images and converts annotations to YOLO format.
"""
import json
import os
import shutil
from pathlib import Path
import fitz  # PyMuPDF
from PIL import Image
import io
from typing import Dict, List, Tuple
import random


# Class mapping
CLASS_MAPPING = {
    "signature": 0,
    "stamp": 1,
    "qr": 2
}


def convert_pdf_page_to_image(pdf_path: str, page_num: int, output_path: str) -> Tuple[int, int]:
    """
    Convert a specific PDF page to an image.
    
    Args:
        pdf_path: Path to PDF file
        page_num: Page number (1-indexed)
        output_path: Output image path
        
    Returns:
        Tuple of (width, height) of the output image
    """
    doc = fitz.open(pdf_path)
    page = doc.load_page(page_num - 1)  # 0-indexed in PyMuPDF
    
    # Render at 2x resolution for better quality
    mat = fitz.Matrix(2.0, 2.0)
    pix = page.get_pixmap(matrix=mat)
    
    # Save as image
    img_bytes = pix.tobytes("png")
    image = Image.open(io.BytesIO(img_bytes)).convert("RGB")
    image.save(output_path)
    
    width, height = image.size
    doc.close()
    
    return width, height


def convert_bbox_to_yolo(bbox: Dict, page_width: int, page_height: int) -> Tuple[float, float, float, float]:
    """
    Convert bbox from absolute coordinates to YOLO format (normalized center x, center y, width, height).
    
    Args:
        bbox: Dictionary with x, y, width, height (absolute coordinates)
        page_width: Page width in pixels
        page_height: Page height in pixels
        
    Returns:
        Tuple of (x_center, y_center, width, height) in normalized coordinates [0, 1]
    """
    x = bbox["x"]
    y = bbox["y"]
    w = bbox["width"]
    h = bbox["height"]
    
    # Calculate center
    x_center = (x + w / 2) / page_width
    y_center = (y + h / 2) / page_height
    
    # Normalize width and height
    norm_width = w / page_width
    norm_height = h / page_height
    
    # Clamp values to [0, 1]
    x_center = max(0, min(1, x_center))
    y_center = max(0, min(1, y_center))
    norm_width = max(0, min(1, norm_width))
    norm_height = max(0, min(1, norm_height))
    
    return x_center, y_center, norm_width, norm_height


def process_annotations(annotations_file: str, pdf_dir: str, output_dir: str, split_ratio: float = 0.8):
    """
    Process annotations and prepare dataset for YOLO training.
    
    Args:
        annotations_file: Path to JSON file with annotations
        pdf_dir: Directory containing PDF files
        output_dir: Output directory for dataset
        split_ratio: Train/validation split ratio
    """
    # Create output directories
    train_images_dir = Path(output_dir) / "images" / "train"
    val_images_dir = Path(output_dir) / "images" / "val"
    train_labels_dir = Path(output_dir) / "labels" / "train"
    val_labels_dir = Path(output_dir) / "labels" / "val"
    
    for dir_path in [train_images_dir, val_images_dir, train_labels_dir, val_labels_dir]:
        dir_path.mkdir(parents=True, exist_ok=True)
    
    # Load annotations
    with open(annotations_file, 'r', encoding='utf-8') as f:
        annotations = json.load(f)
    
    # Collect all document-page combinations
    all_samples = []
    
    for doc_name, doc_data in annotations.items():
        for page_key, page_data in doc_data.items():
            if page_key.startswith("page_"):
                page_num = int(page_key.split("_")[1])
                all_samples.append((doc_name, page_num, page_data))
    
    # Shuffle and split
    random.seed(42)
    random.shuffle(all_samples)
    
    split_idx = int(len(all_samples) * split_ratio)
    train_samples = all_samples[:split_idx]
    val_samples = all_samples[split_idx:]
    
    print(f"Total samples: {len(all_samples)}")
    print(f"Train samples: {len(train_samples)}")
    print(f"Validation samples: {len(val_samples)}")
    
    # Process train samples
    print("\n📦 Processing training samples...")
    process_samples(train_samples, pdf_dir, train_images_dir, train_labels_dir)
    
    # Process validation samples
    print("\n📦 Processing validation samples...")
    process_samples(val_samples, pdf_dir, val_images_dir, val_labels_dir)
    
    # Create data.yaml
    create_data_yaml(output_dir)
    
    print(f"\n✅ Dataset preparation complete!")
    print(f"📁 Dataset saved to: {output_dir}")


def process_samples(samples: List[Tuple], pdf_dir: str, images_dir: Path, labels_dir: Path):
    """Process a list of samples (train or val)."""
    for idx, (doc_name, page_num, page_data) in enumerate(samples):
        try:
            # Generate unique filename
            base_name = doc_name.replace('.pdf', '').replace(' ', '_')
            sample_name = f"{base_name}_page_{page_num}"
            
            # Convert PDF page to image
            pdf_path = os.path.join(pdf_dir, doc_name)
            
            if not os.path.exists(pdf_path):
                print(f"⚠️  PDF not found: {pdf_path}")
                continue
            
            image_path = images_dir / f"{sample_name}.jpg"
            img_width, img_height = convert_pdf_page_to_image(pdf_path, page_num, str(image_path))
            
            # Get original page size from annotations
            page_size = page_data.get("page_size", {})
            orig_width = page_size.get("width", img_width)
            orig_height = page_size.get("height", img_height)
            
            # Calculate scaling factors (since we render at 2x)
            scale_x = img_width / orig_width
            scale_y = img_height / orig_height
            
            # Process annotations
            label_lines = []
            annotations_list = page_data.get("annotations", [])
            
            for ann_dict in annotations_list:
                for ann_id, ann_data in ann_dict.items():
                    category = ann_data.get("category")
                    bbox = ann_data.get("bbox")
                    
                    if category not in CLASS_MAPPING:
                        continue
                    
                    class_id = CLASS_MAPPING[category]
                    
                    # Scale bbox to match rendered image
                    scaled_bbox = {
                        "x": bbox["x"] * scale_x,
                        "y": bbox["y"] * scale_y,
                        "width": bbox["width"] * scale_x,
                        "height": bbox["height"] * scale_y
                    }
                    
                    # Convert to YOLO format
                    x_center, y_center, norm_width, norm_height = convert_bbox_to_yolo(
                        scaled_bbox, img_width, img_height
                    )
                    
                    # Create YOLO label line: class_id x_center y_center width height
                    label_line = f"{class_id} {x_center:.6f} {y_center:.6f} {norm_width:.6f} {norm_height:.6f}"
                    label_lines.append(label_line)
            
            # Save label file
            if label_lines:
                label_path = labels_dir / f"{sample_name}.txt"
                with open(label_path, 'w') as f:
                    f.write('\n'.join(label_lines))
            else:
                print(f"⚠️  No valid annotations for {sample_name}")
            
            if (idx + 1) % 10 == 0:
                print(f"  Processed {idx + 1}/{len(samples)} samples...")
        
        except Exception as e:
            print(f"❌ Error processing {doc_name} page {page_num}: {e}")
            continue


def create_data_yaml(output_dir: str):
    """Create data.yaml file for YOLO training."""
    yaml_content = f"""# Document Inspector Dataset
path: {os.path.abspath(output_dir)}  # dataset root dir
train: images/train  # train images (relative to 'path')
val: images/val  # val images (relative to 'path')

# Classes
names:
  0: signature
  1: stamp
  2: qr
"""
    
    yaml_path = Path(output_dir) / "data.yaml"
    with open(yaml_path, 'w') as f:
        f.write(yaml_content)
    
    print(f"\n📝 Created data.yaml at {yaml_path}")


def main():
    """Main execution function."""
    # Paths - try multiple locations
    script_path = Path(__file__).resolve()
    # Try to find project root
    project_root = script_path.parent.parent.parent.parent
    
    # If running in Docker, dataset is at /app/dataset
    if Path("/app/dataset").exists():
        dataset_dir = Path("/app/dataset")
    elif (project_root / "dataset").exists():
        dataset_dir = project_root / "dataset"
    else:
        # Try current working directory
        dataset_dir = Path("dataset")
        if not dataset_dir.exists():
            dataset_dir = Path.cwd() / "dataset"
    
    annotations_file = dataset_dir / "selected_annotations.json"
    pdf_dir = dataset_dir / "pdfs"
    output_dir = dataset_dir / "yolo_dataset"
    
    print("=" * 60)
    print("Document Inspector - Dataset Preparation")
    print("=" * 60)
    
    # Validate paths
    if not annotations_file.exists():
        print(f"❌ Annotations file not found: {annotations_file}")
        return
    
    if not pdf_dir.exists():
        print(f"❌ PDF directory not found: {pdf_dir}")
        return
    
    print(f"\n📂 Annotations file: {annotations_file}")
    print(f"📂 PDF directory: {pdf_dir}")
    print(f"📂 Output directory: {output_dir}")
    
    # Process annotations
    process_annotations(
        annotations_file=str(annotations_file),
        pdf_dir=str(pdf_dir),
        output_dir=str(output_dir),
        split_ratio=0.8
    )


if __name__ == "__main__":
    main()

