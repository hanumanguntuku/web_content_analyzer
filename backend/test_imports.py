"""
Simple test to verify FastAPI application structure
"""
import sys
import os

# Add current directory to Python path
sys.path.insert(0, os.path.dirname(__file__))

try:
    print("Testing imports...")
    
    # Test config import
    from config.settings import settings
    print("✅ Config settings imported successfully")
    
    # Test exceptions
    from src.utils.exceptions import WebAnalyzerException
    print("✅ Custom exceptions imported successfully")
    
    # Test models 
    from src.models.data_models import URLAnalysisRequest
    print("✅ Data models imported successfully")
    
    
    # Test services
    from src.services.scraping_service import ScrapingService
    print("✅ Services imported successfully")
    
    # Test routes
    from src.api.routes import router
    print("✅ API routes imported successfully")
    
    # Test main app
    import main
    print("✅ Main FastAPI app imported successfully")
    
    print("\n🎉 All imports successful! FastAPI backend foundation is ready.")
    
except ImportError as e:
    print(f"❌ Import error: {e}")
    sys.exit(1)
except Exception as e:
    print(f"❌ Unexpected error: {e}")
    sys.exit(1)
