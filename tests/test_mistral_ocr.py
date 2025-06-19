#!/usr/bin/env python3
"""
Test script for Mistral OCR functionality
Use this to test OCR without running the full application
"""

import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.utils.config import Config
from src.utils.logger import setup_logging, get_logger
from src.document.ocr_handler import OCRHandler
from src.document.processor import DocumentInfo

def test_mistral_ocr():
    """Test Mistral OCR with a sample PDF"""
    
    # Setup logging
    setup_logging()
    logger = get_logger(__name__)
    
    # Check configuration
    config_errors = Config.validate_config()
    if config_errors:
        print("Configuration errors:")
        for error in config_errors:
            print(f"- {error}")
        print("\nPlease update your .env file and try again.")
        return False
    
    if not Config.MISTRAL_API_KEY:
        print("❌ MISTRAL_API_KEY not found in environment")
        print("Please add your Mistral API key to .env file:")
        print("MISTRAL_API_KEY=your_mistral_api_key_here")
        return False
    
    print("✅ Configuration validated")
    print(f"Using Mistral model: {Config.MISTRAL_MODEL}")
    
    # Initialize OCR handler
    try:
        ocr_handler = OCRHandler()
        print("✅ Mistral OCR handler initialized")
    except Exception as e:
        print(f"❌ Failed to initialize OCR handler: {e}")
        return False
    
    # Test with a sample PDF (you'll need to provide this)
    test_files = [
        Path("data/test_sample.pdf")
    ]
    
    test_file = None
    for file_path in test_files:
        if file_path.exists():
            test_file = file_path
            break
    
    if not test_file:
        print("⚠️  No test PDF found. Please create a test file:")
        print("Create a simple PDF with some text and save it as 'test_sample.pdf'")
        return False
    
    print(f"📄 Testing with file: {test_file}")
    
    # Create dummy document info
    doc_info = DocumentInfo(
        filename=test_file.name,
        page_count=1,
        file_size=test_file.stat().st_size,
        has_text=False,
        has_images=True,
        processing_method="mistral_ocr",
        metadata={}
    )
    
    # Process the document
    try:
        print("🔄 Starting OCR processing...")
        result = ocr_handler.process_with_ocr(test_file, doc_info)
        
        print("✅ OCR processing completed!")
        print(f"📊 Results:")
        print(f"   - Pages processed: {len(result.pages)}")
        print(f"   - Total text length: {len(result.text)} characters")
        print(f"   - Processing time: {result.processing_time:.2f} seconds")
        print(f"   - Images extracted: {len(result.images)}")
        
        if result.text:
            print(f"\n📝 Extracted text preview (first 500 chars):")
            print("-" * 50)
            print(result.text[:500])
            if len(result.text) > 500:
                print("...")
            print("-" * 50)
        else:
            print("⚠️  No text was extracted")
        
        return True
        
    except Exception as e:
        print(f"❌ OCR processing failed: {e}")
        logger.exception("OCR test failed")
        return False

def test_api_connection():
    """Test basic API connection to Mistral"""
    
    if not Config.MISTRAL_API_KEY:
        print("❌ MISTRAL_API_KEY not configured")
        return False
    
    try:
        import httpx
        
        client = httpx.Client(
            base_url=Config.MISTRAL_BASE_URL,
            headers={
                "Authorization": f"Bearer {Config.MISTRAL_API_KEY}",
                "Content-Type": "application/json"
            },
            timeout=10
        )
        
        # Test with a simple text-only request
        payload = {
            "model": Config.MISTRAL_MODEL,
            "messages": [
                {
                    "role": "user",
                    "content": "Hello, can you see this message?"
                }
            ],
            "max_tokens": 50
        }
        
        print("🔄 Testing API connection...")
        response = client.post("/chat/completions", json=payload)
        response.raise_for_status()
        
        result = response.json()
        client.close()
        
        if "choices" in result:
            print("✅ API connection successful!")
            print(f"📝 Response: {result['choices'][0]['message']['content']}")
            return True
        else:
            print("⚠️  Unexpected API response format")
            return False
            
    except Exception as e:
        print(f"❌ API connection failed: {e}")
        return False

def main():
    """Main test function"""
    
    print("Mistral OCR Test Suite")
    print("=" * 40)
    
    # Test 1: API Connection
    print("\n1. Testing API Connection...")
    if not test_api_connection():
        return
    
    # Test 2: OCR Processing
    print("\n2. Testing OCR Processing...")
    test_mistral_ocr()

if __name__ == "__main__":
    main()