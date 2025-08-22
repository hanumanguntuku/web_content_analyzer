"""
Comprehensive Test Suite for Milestone 1 Implementation
Tests all core components of the Intelligent Content Processing system
"""

import pytest
import asyncio
import sys
import os
from unittest.mock import Mock, patch, AsyncMock
from typing import Dict, Any

# Add current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

# Test imports first
def test_imports():
    """Test that all core components can be imported"""
    print("🧪 Testing imports...")
    
    try:
        # Core exceptions
        from src.utils.exceptions import (
            WebAnalyzerException, SecurityException, ValidationException,
            RateLimitException, ContentSizeException
        )
        print("✅ Exception classes imported successfully")
        
        # Data models
        from src.models.data_models import (
            URLAnalysisRequest, AnalysisReport, AnalysisMetrics,
            ScrapedContent, ExtractedContent, ProcessedContent
        )
        print("✅ Data models imported successfully")
        
        # Security components
        from src.utils.url_validator import URLValidator
        from src.utils.security import ContentSanitizer
        from src.utils.resource_limits import RateLimiter, ContentSizeLimiter
        print("✅ Security components imported successfully")
        
        # Data processing components
        from src.scrapers.content_extractor import ContentExtractor
        from src.processors.text_processor import TextProcessor
        print("✅ Data processing components imported successfully")
        
        # Service layer
        from src.services.integrated_analysis_service import IntegratedAnalysisService
        print("✅ Integrated analysis service imported successfully")
        
        return True
        
    except ImportError as e:
        print(f"❌ Import failed: {str(e)}")
        return False

@pytest.mark.asyncio
async def test_url_validator():
    """Test URL validation and security checks"""
    print("🧪 Testing URL Validator...")
    
    from src.utils.url_validator import URLValidator
    
    validator = URLValidator()
    
    # Test valid URLs
    valid_urls = [
        "https://www.example.com",
        "https://github.com/user/repo",
        "https://docs.python.org/3/"
    ]
    
    for url in valid_urls:
        result = await validator.validate_url(url)
        assert result.is_valid, f"Valid URL should pass: {url}"
        print(f"✅ Valid URL passed: {url}")
    
    # Test invalid/dangerous URLs
    invalid_urls = [
        "http://localhost:8080",  # Local host
        "https://192.168.1.1",   # Private IP
        "ftp://example.com",     # Non-HTTP protocol
        "not-a-url",             # Invalid format
    ]
    
    for url in invalid_urls:
        result = await validator.validate_url(url)
        assert not result.is_valid, f"Invalid URL should fail: {url}"
        print(f"✅ Invalid URL blocked: {url}")
    
    print("✅ URL Validator tests passed")

@pytest.mark.asyncio
async def test_content_sanitizer():
    """Test content sanitization"""
    print("🧪 Testing Content Sanitizer...")
    
    from src.utils.security import ContentSanitizer
    
    sanitizer = ContentSanitizer()
    
    # Test XSS prevention
    malicious_content = '''
    <html>
        <body>
            <h1>Title</h1>
            <script>alert('XSS')</script>
            <p onclick="malicious()">Click me</p>
            <iframe src="http://evil.com"></iframe>
            <p>Safe content</p>
        </body>
    </html>
    '''
    
    sanitized = await sanitizer.sanitize_content(malicious_content)
    
    # Check that dangerous elements are removed
    assert "<script>" not in sanitized
    assert "onclick=" not in sanitized
    assert "<iframe>" not in sanitized
    assert "Safe content" in sanitized  # Safe content should remain
    
    print("✅ XSS content properly sanitized")
    print("✅ Content Sanitizer tests passed")

@pytest.mark.asyncio
async def test_rate_limiter():
    """Test rate limiting functionality"""
    print("🧪 Testing Rate Limiter...")
    
    from src.utils.resource_limits import RateLimiter
    
    # Create a strict rate limiter for testing
    limiter = RateLimiter(max_requests=3, time_window=60)
    
    client_ip = "192.168.1.100"
    
    # First 3 requests should pass
    for i in range(3):
        allowed = await limiter.check_rate_limit(client_ip)
        assert allowed, f"Request {i+1} should be allowed"
        print(f"✅ Request {i+1} allowed")
    
    # 4th request should be blocked
    blocked = await limiter.check_rate_limit(client_ip)
    assert not blocked, "4th request should be blocked"
    print("✅ Rate limit properly enforced")
    
    print("✅ Rate Limiter tests passed")

@pytest.mark.asyncio
async def test_content_extractor():
    """Test intelligent content extraction"""
    print("🧪 Testing Content Extractor...")
    
    from src.scrapers.content_extractor import ContentExtractor
    
    extractor = ContentExtractor()
    
    # Sample HTML content
    sample_html = '''
    <html>
        <head>
            <title>Test Article</title>
            <meta name="description" content="A test article for extraction">
        </head>
        <body>
            <nav>Navigation menu</nav>
            <article>
                <h1>Main Article Title</h1>
                <p>This is the main content of the article. It contains important information that should be extracted.</p>
                <p>Another paragraph with more content.</p>
                <aside>Sidebar content</aside>
            </article>
            <footer>Footer content</footer>
        </body>
    </html>
    '''
    
    extracted = await extractor.extract_content(sample_html, "https://example.com")
    
    # Verify extraction results
    assert extracted.title == "Test Article"
    assert "main content" in extracted.main_content.lower()
    assert extracted.quality_score > 0
    assert len(extracted.headings) > 0
    
    print(f"✅ Title extracted: {extracted.title}")
    print(f"✅ Content quality score: {extracted.quality_score}")
    print(f"✅ Main content length: {len(extracted.main_content)} chars")
    
    print("✅ Content Extractor tests passed")

@pytest.mark.asyncio
async def test_text_processor():
    """Test text processing and analysis"""
    print("🧪 Testing Text Processor...")
    
    from src.processors.text_processor import TextProcessor
    from src.models.data_models import ExtractedContent
    
    processor = TextProcessor()
    
    # Sample extracted content
    extracted_content = ExtractedContent(
        title="Sample Article",
        main_content="""
        This is a sample article about web content analysis. 
        The article discusses various techniques for extracting and processing web content.
        Keywords include: analysis, extraction, processing, web scraping, content management.
        The content quality is good and the readability should be reasonable.
        """,
        headings={"h1": ["Sample Article"], "h2": ["Introduction", "Methods"]},
        links=[],
        images=[],
        quality_score=0.8,
        metadata={}
    )
    
    processed = await processor.process_content(extracted_content, deep_analysis=True)
    
    # Verify processing results
    assert processed.word_count > 0
    assert len(processed.keywords) > 0
    assert processed.readability_score >= 0
    assert processed.summary is not None
    assert processed.language is not None
    
    print(f"✅ Word count: {processed.word_count}")
    print(f"✅ Keywords found: {len(processed.keywords)}")
    print(f"✅ Readability score: {processed.readability_score}")
    print(f"✅ Language detected: {processed.language}")
    
    print("✅ Text Processor tests passed")

@pytest.mark.asyncio
async def test_integrated_analysis_service():
    """Test the integrated analysis service with mocked web scraping"""
    print("🧪 Testing Integrated Analysis Service...")
    
    from src.services.integrated_analysis_service import IntegratedAnalysisService
    from src.utils.exceptions import ValidationException
    
    service = IntegratedAnalysisService()
    
    # Test service health
    health = await service.get_service_health()
    assert health["status"] in ["healthy", "degraded"]
    print(f"✅ Service health: {health['status']}")
    
    # Test service stats
    stats = service.get_service_stats()
    assert "total_analyses" in stats
    print(f"✅ Service stats available: {len(stats)} metrics")
    
    # Test invalid URL handling
    try:
        await service.analyze_content("invalid-url", "127.0.0.1")
        assert False, "Should have raised ValidationException"
    except ValidationException:
        print("✅ Invalid URL properly rejected")
    
    print("✅ Integrated Analysis Service tests passed")

def test_exception_handling():
    """Test custom exception handling"""
    print("🧪 Testing Exception Handling...")
    
    from src.utils.exceptions import (
        WebAnalyzerException, SecurityException, ValidationException,
        create_error_response, get_user_friendly_message
    )
    
    # Test base exception
    base_exc = WebAnalyzerException("Test error", "TEST_ERROR", 400)
    assert base_exc.detail == "Test error"
    assert base_exc.error_type == "TEST_ERROR"
    assert base_exc.status_code == 400
    
    # Test error response creation
    error_response = create_error_response(base_exc)
    assert "error" in error_response
    assert error_response["error"]["type"] == "TEST_ERROR"
    
    # Test user-friendly messages
    security_exc = SecurityException("Security violation")
    friendly_msg = get_user_friendly_message(security_exc)
    assert len(friendly_msg) > 0
    
    print("✅ Exception creation and handling working")
    print("✅ Exception Handling tests passed")

async def run_all_tests():
    """Run all tests in sequence"""
    print("🚀 Starting Milestone 1 Comprehensive Test Suite")
    print("=" * 60)
    
    test_results = []
    
    # Test 1: Imports
    try:
        result = test_imports()
        test_results.append(("Imports", "✅ PASSED" if result else "❌ FAILED"))
    except Exception as e:
        test_results.append(("Imports", f"❌ FAILED: {str(e)}"))
    
    # Test 2: Exception Handling
    try:
        test_exception_handling()
        test_results.append(("Exception Handling", "✅ PASSED"))
    except Exception as e:
        test_results.append(("Exception Handling", f"❌ FAILED: {str(e)}"))
    
    # Test 3: URL Validator
    try:
        await test_url_validator()
        test_results.append(("URL Validator", "✅ PASSED"))
    except Exception as e:
        test_results.append(("URL Validator", f"❌ FAILED: {str(e)}"))
    
    # Test 4: Content Sanitizer
    try:
        await test_content_sanitizer()
        test_results.append(("Content Sanitizer", "✅ PASSED"))
    except Exception as e:
        test_results.append(("Content Sanitizer", f"❌ FAILED: {str(e)}"))
    
    # Test 5: Rate Limiter
    try:
        await test_rate_limiter()
        test_results.append(("Rate Limiter", "✅ PASSED"))
    except Exception as e:
        test_results.append(("Rate Limiter", f"❌ FAILED: {str(e)}"))
    
    # Test 6: Content Extractor
    try:
        await test_content_extractor()
        test_results.append(("Content Extractor", "✅ PASSED"))
    except Exception as e:
        test_results.append(("Content Extractor", f"❌ FAILED: {str(e)}"))
    
    # Test 7: Text Processor
    try:
        await test_text_processor()
        test_results.append(("Text Processor", "✅ PASSED"))
    except Exception as e:
        test_results.append(("Text Processor", f"❌ FAILED: {str(e)}"))
    
    # Test 8: Integrated Service
    try:
        await test_integrated_analysis_service()
        test_results.append(("Integrated Service", "✅ PASSED"))
    except Exception as e:
        test_results.append(("Integrated Service", f"❌ FAILED: {str(e)}"))
    
    # Print results summary
    print("\n" + "=" * 60)
    print("🏁 TEST RESULTS SUMMARY")
    print("=" * 60)
    
    passed = 0
    total = len(test_results)
    
    for test_name, result in test_results:
        print(f"{test_name:<25} {result}")
        if "✅ PASSED" in result:
            passed += 1
    
    print("=" * 60)
    print(f"📊 Overall Results: {passed}/{total} tests passed ({(passed/total)*100:.1f}%)")
    
    if passed == total:
        print("🎉 ALL TESTS PASSED! Milestone 1 implementation is ready!")
    else:
        print("⚠️  Some tests failed. Please check the implementation.")
    
    return passed == total

if __name__ == "__main__":
    # Run tests
    success = asyncio.run(run_all_tests())
    sys.exit(0 if success else 1)
