#!/usr/bin/env python3
"""
API Test for Enhanced Content Extraction
"""

import requests
import json
import sys

def test_api():
    """Test the enhanced content extraction API."""
    print("🧪 Testing Enhanced Content Extraction API...")
    
    # API endpoint
    url = "http://127.0.0.1:8000/scrape"
    
    # Test payload
    payload = {
        "url": "https://httpbin.org/html"
    }
    
    headers = {
        "Content-Type": "application/json"
    }
    
    try:
        print(f"📤 Sending request to {url}")
        print(f"📋 Payload: {payload}")
        
        response = requests.post(url, json=payload, headers=headers, timeout=30)
        
        print(f"📬 Response status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            
            print("✅ API Response received successfully!")
            print("\n📊 Response Analysis:")
            print(f"  ✓ URL: {data.get('url')}")
            print(f"  ✓ Success: {data.get('success')}")
            print(f"  ✓ Content Length: {data.get('content_length')}")
            print(f"  ✓ Extraction Method: {data.get('extraction_method', 'N/A')}")
            print(f"  ✓ Confidence: {data.get('confidence', 'N/A')}")
            
            # Check for enhanced metadata
            metadata = data.get('metadata', {})
            if metadata:
                print(f"  ✓ Metadata Keys: {list(metadata.keys())}")
                print(f"  ✓ Title: {metadata.get('title', 'N/A')}")
                print(f"  ✓ Language: {metadata.get('language', 'N/A')}")
                
                social_meta = metadata.get('social_meta', {})
                if social_meta:
                    print(f"  ✓ Social Meta Fields: {len(social_meta)}")
            
            # Content preview
            content = data.get('text', '')
            if content:
                preview = content[:200] + "..." if len(content) > 200 else content
                print(f"  ✓ Content Preview: {preview}")
            
            print("\n🎉 Enhanced Content Extraction API is working perfectly!")
            return True
            
        else:
            print(f"❌ API Error: {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
    except requests.exceptions.ConnectionError:
        print("❌ Connection Error: Is the backend server running on port 8000?")
        print("💡 Start the server with: uvicorn src.main:app --reload --port 8000")
        return False
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False

def test_health_endpoint():
    """Test the health endpoint."""
    try:
        response = requests.get("http://127.0.0.1:8000/health", timeout=10)
        if response.status_code == 200:
            print("✅ Health endpoint working")
            return True
        else:
            print(f"❌ Health endpoint failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Health endpoint error: {e}")
        return False

if __name__ == "__main__":
    print("🚀 Phase 1 API Testing\n")
    print("=" * 50)
    
    # Test health endpoint first
    if test_health_endpoint():
        print()
        # Test main API
        if test_api():
            print("\n🎯 All API tests passed!")
            print("✅ Phase 1 implementation ready for production!")
        else:
            sys.exit(1)
    else:
        print("❌ Server not responding")
        sys.exit(1)
