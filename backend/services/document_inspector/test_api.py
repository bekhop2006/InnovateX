"""
Test script for Document Inspector API.
Usage: python test_api.py
"""
import requests
import json
from pathlib import Path


BASE_URL = "http://localhost:8000/api/document-inspector"


def test_health_check():
    """Test health check endpoint."""
    print("\n" + "="*60)
    print("Testing Health Check")
    print("="*60)
    
    response = requests.get(f"{BASE_URL}/health")
    print(f"Status Code: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    
    return response.status_code == 200


def test_detect(pdf_path: str, conf_threshold: float = 0.25):
    """Test detection endpoint."""
    print("\n" + "="*60)
    print("Testing Detection Endpoint")
    print("="*60)
    
    if not Path(pdf_path).exists():
        print(f"❌ PDF file not found: {pdf_path}")
        return False
    
    print(f"📄 Document: {pdf_path}")
    print(f"🎯 Confidence threshold: {conf_threshold}")
    
    with open(pdf_path, "rb") as f:
        files = {"file": f}
        params = {"conf_threshold": conf_threshold}
        
        response = requests.post(
            f"{BASE_URL}/detect",
            files=files,
            params=params
        )
    
    print(f"\nStatus Code: {response.status_code}")
    
    if response.status_code == 200:
        result = response.json()
        print(f"\n✅ Success!")
        print(f"Document: {result['document_name']}")
        print(f"Total pages: {result['total_pages']}")
        print(f"Processing time: {result['processing_time']:.2f}s")
        
        # Print detections per page
        for page in result['pages']:
            print(f"\nPage {page['page_number']}:")
            print(f"  Size: {page['page_size']['width']}x{page['page_size']['height']}")
            print(f"  Detections: {len(page['annotations'])}")
            
            for ann in page['annotations']:
                print(f"    - {ann['category']}: {ann['confidence']:.2%} at ({ann['bbox']['x']:.1f}, {ann['bbox']['y']:.1f})")
        
        return True
    else:
        print(f"❌ Error: {response.json()}")
        return False


def test_detect_visualize(pdf_path: str, page_number: int = 1, output_path: str = "result.png"):
    """Test detection with visualization endpoint."""
    print("\n" + "="*60)
    print("Testing Detection with Visualization")
    print("="*60)
    
    if not Path(pdf_path).exists():
        print(f"❌ PDF file not found: {pdf_path}")
        return False
    
    print(f"📄 Document: {pdf_path}")
    print(f"📄 Page: {page_number}")
    
    with open(pdf_path, "rb") as f:
        files = {"file": f}
        params = {"page_number": page_number, "conf_threshold": 0.25}
        
        response = requests.post(
            f"{BASE_URL}/detect-visualize",
            files=files,
            params=params
        )
    
    print(f"\nStatus Code: {response.status_code}")
    
    if response.status_code == 200:
        # Save image
        with open(output_path, "wb") as f:
            f.write(response.content)
        
        print(f"✅ Success! Image saved to: {output_path}")
        return True
    else:
        print(f"❌ Error: {response.json()}")
        return False


def main():
    """Run all tests."""
    print("="*60)
    print("Document Inspector API Tests")
    print("="*60)
    
    # Test 1: Health check
    health_ok = test_health_check()
    
    if not health_ok:
        print("\n❌ Health check failed. Make sure the server is running and model is loaded.")
        return
    
    # Test 2: Detection (provide a test PDF path)
    project_root = Path(__file__).parent.parent.parent.parent
    test_pdf = project_root / "dataset" / "pdfs" / "письмо-.pdf"
    
    if test_pdf.exists():
        test_detect(str(test_pdf), conf_threshold=0.3)
        test_detect_visualize(str(test_pdf), page_number=1, output_path="test_result.png")
    else:
        print(f"\n⚠️  Test PDF not found at {test_pdf}")
        print("Please provide a valid PDF path to test detection.")
    
    print("\n" + "="*60)
    print("Tests Complete!")
    print("="*60)


if __name__ == "__main__":
    main()

