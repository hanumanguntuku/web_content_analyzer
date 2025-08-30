"""
API Routes - M1-SVC-03 Implementation
Enhanced FastAPI routes with integrated analysis service
"""
from fastapi import APIRouter, HTTPException, Depends, Request, BackgroundTasks
from typing import Dict, Any, List, Optional
import logging
import time
import asyncio

from ..models.data_models import URLAnalysisRequest, AnalysisReport, ErrorResponse
from ..services.integrated_analysis_service import IntegratedAnalysisService
from ..services.scraping_service import ScrapingService
from ..utils.exceptions import (
    WebAnalyzerException,
    ValidationException,
    ValidationError,
    SecurityException,
    ScrapingException,
    ScrapingError,
    RateLimitException,
    create_error_response,
    get_user_friendly_message
)
from config.settings import settings

# Configure logging
logger = logging.getLogger(__name__)

# Create router
router = APIRouter()

# Global services
analysis_service = IntegratedAnalysisService()
scraping_service = ScrapingService()

# Dependency functions
def get_client_ip(request: Request) -> str:
    """Extract client IP address from request"""
    try:
        # Check for forwarded headers first (proxy scenarios)
        forwarded_for = request.headers.get("X-Forwarded-For")
        if forwarded_for:
            return forwarded_for.split(",")[0].strip()
        
        real_ip = request.headers.get("X-Real-IP")
        if real_ip:
            return real_ip
        
        # Fall back to direct client IP
        if request.client and request.client.host:
            return request.client.host
        else:
            return "127.0.0.1"
    except Exception as e:
        logger.warning(f"Could not extract client IP: {e}")
        return "127.0.0.1"

def validate_url_dependency(
    url: str,
    deep_analysis: bool = True,
    request: Request = None
) -> tuple[URLAnalysisRequest, str]:
    """Validate analysis request and extract client info"""
    client_ip = get_client_ip(request) if request else "127.0.0.1"
    analysis_request = URLAnalysisRequest(url=url, deep_analysis=deep_analysis)
    return analysis_request, client_ip

async def validate_analysis_request(
    request: URLAnalysisRequest,
    client_ip: str = Depends(get_client_ip)
) -> tuple[URLAnalysisRequest, str]:
    """Validate analysis request and extract client info"""
    return request, client_ip

# API Routes

@router.get("/status", response_model=Dict[str, Any])
async def get_status():
    """Get comprehensive API service status"""
    try:
        # Get service health
        health_info = await analysis_service.get_service_health()
        
        return {
            "status": "running",
            "version": settings.api_version,
            "service": "web-content-analyzer-api",
            "environment": settings.environment,
            "features": {
                "intelligent_content_extraction": True,
                "deep_text_processing": True,
                "security_validation": True,
                "ssrf_prevention": True,
                "content_sanitization": True,
                "rate_limiting": True,
                "resource_monitoring": True
            },
            "limits": {
                "max_content_size": settings.max_content_size,
                "request_timeout": settings.request_timeout,
                "max_requests_per_minute": settings.max_requests_per_minute
            },
            "timestamp": time.time()
        }
    except Exception as e:
        logger.error(f"Status endpoint error: {e}")
        return {
            "status": "error",
            "service": "web-content-analyzer-api",
            "error": str(e),
            "timestamp": time.time()
        }

@router.post("/analyze", response_model=AnalysisReport, responses={
    400: {"model": ErrorResponse, "description": "Invalid request"},
    422: {"model": ErrorResponse, "description": "Validation error"},
    500: {"model": ErrorResponse, "description": "Internal server error"}
})
async def analyze_url(
    request: URLAnalysisRequest,
    client_ip: str = Depends(get_client_ip),
    background_tasks: BackgroundTasks = BackgroundTasks()
):
    """
    Analyze a website URL and return comprehensive content analysis
    
    This endpoint performs:
    - URL validation and security checks
    - Web content scraping with anti-detection measures
    - Content extraction and cleaning
    - Structured data analysis
    - Report generation
    """
    start_time = time.time()
    url = str(request.url)
    
    logger.info(f"🔍 Starting analysis for URL: {url}")
    
    try:
        # Use the integrated analysis service for complete pipeline
        logger.info(f"🔄 Processing analysis request for {url}")
        
        # Run complete analysis pipeline
        analysis_report = await analysis_service.analyze_url(url)
        
        # Log successful completion
        processing_time = time.time() - start_time
        logger.info(f"✅ Analysis completed for {url} in {processing_time:.2f}s")
        
        # Add background task for logging
        background_tasks.add_task(log_analysis_completion, url, processing_time)
        
        return analysis_report
        
    except ValidationError as e:
        logger.error(f"❌ Validation error for {url}: {e.detail}")
        raise HTTPException(status_code=400, detail=str(e.detail))
        
    except ScrapingError as e:
        logger.error(f"❌ Scraping error for {url}: {e.detail}")
        raise HTTPException(status_code=422, detail=str(e.detail))
        
    except Exception as e:
        logger.error(f"❌ Unexpected error analyzing {url}: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500, 
            detail=f"Analysis failed: {str(e)}"
        )

@router.get("/analyze/{analysis_id}")
async def get_analysis_result(analysis_id: str):
    """Get analysis result by ID (for future async processing)"""
    # Placeholder for future implementation
    return {
        "analysis_id": analysis_id,
        "status": "not_implemented",
        "message": "Async analysis retrieval will be implemented in future milestones"
    }

@router.get("/supported-sites")
async def get_supported_sites():
    """Get list of supported/tested website types"""
    return {
        "supported_types": [
            "corporate_websites",
            "news_sites",
            "blogs",
            "e_commerce",
            "educational"
        ],
        "tested_domains": [
            "microsoft.com",
            "apple.com", 
            "bbc.com",
            "techcrunch.com",
            "medium.com",
            "dev.to",
            "coursera.org"
        ],
        "limitations": [
            "JavaScript-heavy sites require additional processing",
            "Large content (>10MB) will be truncated",
            "Rate limiting applies (60 requests/minute)"
        ]
    }

async def log_analysis_completion(url: str, processing_time: float):
    """Background task to log analysis completion"""
    logger.info(f"📊 Analysis logged - URL: {url}, Time: {processing_time:.3f}s")
