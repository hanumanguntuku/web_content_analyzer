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
from ..utils.exceptions import (
    WebAnalyzerException,
    ValidationException,
    SecurityException,
    RateLimitException,
    create_error_response,
    get_user_friendly_message
)
from config.settings import settings

# Configure logging
logger = logging.getLogger(__name__)

# Create router
router = APIRouter()

# Global integrated analysis service
analysis_service = IntegratedAnalysisService(
    rate_limit_requests=getattr(settings, 'rate_limit_requests', 100),
    rate_limit_window=getattr(settings, 'rate_limit_window', 3600),
    max_content_size=getattr(settings, 'max_content_size', 10 * 1024 * 1024),
    request_timeout=getattr(settings, 'request_timeout', 30)
)

# Dependency functions
def get_client_ip(request: Request) -> str:
    """Extract client IP address from request"""
    # Check for forwarded headers first (proxy scenarios)
    forwarded_for = request.headers.get("X-Forwarded-For")
    if forwarded_for:
        return forwarded_for.split(",")[0].strip()
    
    real_ip = request.headers.get("X-Real-IP")
    if real_ip:
        return real_ip
    
    # Fall back to direct client IP
    return request.client.host if request.client else "127.0.0.1"

async def validate_analysis_request(
    request: URLAnalysisRequest,
    client_ip: str = Depends(get_client_ip)
) -> tuple[URLAnalysisRequest, str]:
    """Validate analysis request and extract client info"""
    return request, client_ip

# Background task functions
async def log_analysis_completion(url: str, processing_time: float, success: bool = True):
    """Background task to log analysis completion"""
    status = "SUCCESS" if success else "FAILED"
    logger.info(f"📊 Analysis {status}: {url} completed in {processing_time:.3f}s")

# API Routes

@router.get("/status", response_model=Dict[str, Any])
async def get_status():
    """Get comprehensive API service status"""
    try:
        # Get service health
        health_info = await analysis_service.get_service_health()
        
        return {
            "status": "running",
            "version": getattr(settings, 'api_version', '1.0.0'),
            "service": "web-content-analyzer-api",
            "environment": getattr(settings, 'environment', 'development'),
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
                "max_content_size": getattr(settings, 'max_content_size', 10 * 1024 * 1024),
                "request_timeout": getattr(settings, 'request_timeout', 120),
                "rate_limit_requests": getattr(settings, 'rate_limit_requests', 100)
            },
            "health": health_info,
            "timestamp": time.time()
        }
        
    except Exception as e:
        logger.error(f"Status check failed: {str(e)}")
        return {
            "status": "degraded",
            "error": str(e),
            "timestamp": time.time()
        }

@router.post("/analyze", response_model=AnalysisReport, responses={
    400: {"model": ErrorResponse, "description": "Invalid request"},
    403: {"model": ErrorResponse, "description": "Security validation failed"},
    429: {"model": ErrorResponse, "description": "Rate limit exceeded"},
    422: {"model": ErrorResponse, "description": "Processing error"},
    500: {"model": ErrorResponse, "description": "Internal server error"}
})
async def analyze_url(
    request: URLAnalysisRequest,
    client_ip: str = Depends(get_client_ip),
    background_tasks: BackgroundTasks = BackgroundTasks()
):
    """
    Perform comprehensive web content analysis
    
    This endpoint provides complete analysis including:
    - URL validation and security checks (SSRF prevention)
    - Intelligent web content scraping with anti-detection
    - Content extraction with noise removal
    - Deep text processing and analysis
    - Keyword extraction and sentiment analysis
    - Structured report generation
    """
    start_time = time.time()
    url = str(request.url)
    
    logger.info(f"🔍 Starting comprehensive analysis for URL: {url}")
    
    try:
        # Perform comprehensive analysis using integrated service
        analysis_result = await analysis_service.analyze_content(
            url=url,
            client_ip=client_ip,
            deep_analysis=getattr(request, 'deep_analysis', True),
            extract_images=getattr(request, 'extract_images', True),
            extract_links=getattr(request, 'extract_links', True)
        )
        
        processing_time = time.time() - start_time
        logger.info(f"✅ Analysis completed for {url} in {processing_time:.3f}s")
        
        # Add background task for logging
        background_tasks.add_task(
            log_analysis_completion, 
            url, 
            processing_time, 
            success=True
        )
        
        return analysis_result
        
    except WebAnalyzerException as e:
        processing_time = time.time() - start_time
        
        logger.error(f"❌ Analysis failed for {url}: {e.detail}")
        
        # Add background task for failure logging
        background_tasks.add_task(
            log_analysis_completion, 
            url, 
            processing_time, 
            success=False
        )
        
        # Return user-friendly error
        error_response = create_error_response(e)
        raise HTTPException(
            status_code=e.status_code,
            detail={
                "message": get_user_friendly_message(e),
                "technical_details": e.detail,
                "error_type": e.error_type,
                "url": url,
                "processing_time": processing_time
            }
        )
        
    except Exception as e:
        processing_time = time.time() - start_time
        
        logger.error(f"❌ Unexpected error analyzing {url}: {str(e)}", exc_info=True)
        
        # Add background task for failure logging
        background_tasks.add_task(
            log_analysis_completion, 
            url, 
            processing_time, 
            success=False
        )
        
        raise HTTPException(
            status_code=500,
            detail={
                "message": "An unexpected error occurred while processing your request.",
                "technical_details": str(e),
                "error_type": "INTERNAL_SERVER_ERROR",
                "url": url,
                "processing_time": processing_time
            }
        )

@router.get("/health", response_model=Dict[str, Any])
async def health_check():
    """Detailed service health check for monitoring"""
    try:
        health_info = await analysis_service.get_service_health()
        return health_info
        
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        return {
            "status": "unhealthy",
            "error": str(e),
            "timestamp": time.time()
        }

@router.get("/stats", response_model=Dict[str, Any])
async def get_service_stats():
    """Get detailed service performance statistics"""
    try:
        stats = analysis_service.get_service_stats()
        return {
            "performance_stats": stats,
            "timestamp": time.time()
        }
        
    except Exception as e:
        logger.error(f"Stats retrieval failed: {str(e)}")
        return {
            "error": "Failed to retrieve statistics",
            "detail": str(e),
            "timestamp": time.time()
        }

@router.get("/analyze/{analysis_id}")
async def get_analysis_result(analysis_id: str):
    """Get analysis result by ID (placeholder for future async processing)"""
    logger.info(f"Analysis result requested for ID: {analysis_id}")
    
    return {
        "analysis_id": analysis_id,
        "status": "not_implemented",
        "message": "Async analysis retrieval will be implemented in future milestones",
        "note": "Current implementation provides synchronous analysis via POST /analyze"
    }

@router.delete("/cache")
async def clear_cache():
    """Clear service caches (placeholder for future implementation)"""
    logger.info("Cache clear requested")
    
    return {
        "status": "success",
        "message": "Cache clearing will be implemented when caching is added",
        "timestamp": time.time()
    }
