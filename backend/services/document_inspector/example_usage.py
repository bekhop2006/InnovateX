"""
Example usage of Document Inspector service.
Shows different ways to use the detector.
"""
from pathlib import Path
from detector import DocumentDetector
from utils import pdf_to_images
import json


def example_1_basic_detection():
    """Example 1: Basic detection on a PDF document."""
    print("\n" + "="*60)
    print("Example 1: Basic Detection")
    print("="*60)
    
    # Initialize detector
    model_path = Path(__file__).parent.parent.parent.parent / "models" / "document_inspector_yolo.pt"
    
    if not model_path.exists():
        print(f"❌ Model not found at {model_path}")
        print("Please train the model first using train_model.py")
        return
    
    detector = DocumentDetector(str(model_path))
    
    # Load PDF
    pdf_path = Path(__file__).parent.parent.parent.parent / "dataset" / "pdfs" / "письмо-.pdf"
    
    if not pdf_path.exists():
        print(f"❌ PDF not found at {pdf_path}")
        return
    
    print(f"\n📄 Processing: {pdf_path.name}")
    
    # Convert PDF to images
    images = pdf_to_images(str(pdf_path))
    
    # Process each page
    all_results = []
    
    for image, page_num in images:
        print(f"\n📄 Page {page_num}:")
        
        # Detect elements
        detections = detector.detect(image, conf_threshold=0.3)
        
        print(f"  Found {len(detections)} elements:")
        for det in detections:
            print(f"    - {det['category']}: {det['confidence']:.2%}")
        
        all_results.append({
            "page": page_num,
            "detections": detections
        })
    
    return all_results


def example_2_with_visualization():
    """Example 2: Detection with visualization."""
    print("\n" + "="*60)
    print("Example 2: Detection with Visualization")
    print("="*60)
    
    # Initialize detector
    model_path = Path(__file__).parent.parent.parent.parent / "models" / "document_inspector_yolo.pt"
    
    if not model_path.exists():
        print(f"❌ Model not found at {model_path}")
        return
    
    detector = DocumentDetector(str(model_path))
    
    # Load PDF
    pdf_path = Path(__file__).parent.parent.parent.parent / "dataset" / "pdfs" / "письмо-.pdf"
    
    if not pdf_path.exists():
        print(f"❌ PDF not found at {pdf_path}")
        return
    
    print(f"\n📄 Processing: {pdf_path.name}")
    
    # Convert PDF to images
    images = pdf_to_images(str(pdf_path))
    
    # Process first page with visualization
    if images:
        image, page_num = images[0]
        
        print(f"\n📄 Visualizing page {page_num}...")
        
        # Detect and visualize
        output_path = f"example_result_page_{page_num}.png"
        result_image = detector.detect_and_visualize(
            image,
            conf_threshold=0.3,
            save_path=output_path
        )
        
        print(f"✅ Visualization saved to: {output_path}")
        
        return result_image


def example_3_batch_processing():
    """Example 3: Batch processing multiple documents."""
    print("\n" + "="*60)
    print("Example 3: Batch Processing")
    print("="*60)
    
    # Initialize detector
    model_path = Path(__file__).parent.parent.parent.parent / "models" / "document_inspector_yolo.pt"
    
    if not model_path.exists():
        print(f"❌ Model not found at {model_path}")
        return
    
    detector = DocumentDetector(str(model_path))
    
    # Find all PDFs
    pdf_dir = Path(__file__).parent.parent.parent.parent / "dataset" / "pdfs"
    
    if not pdf_dir.exists():
        print(f"❌ PDF directory not found at {pdf_dir}")
        return
    
    pdf_files = list(pdf_dir.glob("*.pdf"))[:3]  # Process first 3 PDFs
    
    print(f"\n📦 Processing {len(pdf_files)} documents...")
    
    batch_results = {}
    
    for pdf_path in pdf_files:
        print(f"\n📄 {pdf_path.name}")
        
        try:
            # Convert PDF to images
            images = pdf_to_images(str(pdf_path))
            
            doc_results = []
            
            for image, page_num in images:
                # Detect elements
                detections = detector.detect(image, conf_threshold=0.3)
                
                doc_results.append({
                    "page": page_num,
                    "num_detections": len(detections),
                    "categories": {
                        "signatures": len([d for d in detections if d["category"] == "signature"]),
                        "stamps": len([d for d in detections if d["category"] == "stamp"]),
                        "qr_codes": len([d for d in detections if d["category"] == "qr"])
                    }
                })
                
                print(f"  Page {page_num}: {len(detections)} detections")
            
            batch_results[pdf_path.name] = doc_results
        
        except Exception as e:
            print(f"  ❌ Error: {e}")
    
    # Save results to JSON
    output_file = "batch_results.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(batch_results, f, indent=2, ensure_ascii=False)
    
    print(f"\n✅ Batch results saved to: {output_file}")
    
    return batch_results


def example_4_custom_confidence():
    """Example 4: Using different confidence thresholds."""
    print("\n" + "="*60)
    print("Example 4: Custom Confidence Thresholds")
    print("="*60)
    
    # Initialize detector
    model_path = Path(__file__).parent.parent.parent.parent / "models" / "document_inspector_yolo.pt"
    
    if not model_path.exists():
        print(f"❌ Model not found at {model_path}")
        return
    
    detector = DocumentDetector(str(model_path))
    
    # Load PDF
    pdf_path = Path(__file__).parent.parent.parent.parent / "dataset" / "pdfs" / "письмо-.pdf"
    
    if not pdf_path.exists():
        print(f"❌ PDF not found at {pdf_path}")
        return
    
    # Convert PDF to images
    images = pdf_to_images(str(pdf_path))
    
    if not images:
        print("❌ No images extracted")
        return
    
    # Test different confidence thresholds
    image, page_num = images[0]
    
    thresholds = [0.1, 0.25, 0.5, 0.75]
    
    print(f"\n📄 Testing different thresholds on page {page_num}:")
    
    for threshold in thresholds:
        detections = detector.detect(image, conf_threshold=threshold)
        
        print(f"\n  Threshold {threshold:.2f}:")
        print(f"    Total detections: {len(detections)}")
        
        # Count by category
        categories = {}
        for det in detections:
            cat = det["category"]
            categories[cat] = categories.get(cat, 0) + 1
        
        for cat, count in categories.items():
            print(f"    - {cat}: {count}")


def main():
    """Run all examples."""
    print("="*60)
    print("Document Inspector - Usage Examples")
    print("="*60)
    
    # Run examples
    example_1_basic_detection()
    example_2_with_visualization()
    example_3_batch_processing()
    example_4_custom_confidence()
    
    print("\n" + "="*60)
    print("✅ All examples completed!")
    print("="*60)


if __name__ == "__main__":
    main()

