"""
Web Content Analyzer - Main FastAPI Application
N-Tier Architecture with comprehensive error handling and security
"""
from dotenv import load_dotenv
load_dotenv()
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
import uvicorn
import logging
import time
from typing import Dict, Any

from src.api.routes import router as api_router
from src.api.batch_routes import router as batch_router
from src.api.enhanced_routes import router as enhanced_router
from src.utils.exceptions import WebAnalyzerException
from config.settings import settings

# Configure logging
logging.basicConfig(
    level=getattr(logging, settings.log_level.upper()),
    format=settings.log_format
)
logger = logging.getLogger(__name__)

from src.services.integrated_analysis_service import IntegratedAnalysisService

analysis_service = IntegratedAnalysisService()

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan management"""
    # Startup
    logger.info("🚀 Starting Web Content Analyzer API...")
    logger.info(f"Environment: {settings.environment}")
    logger.info(f"Debug mode: {settings.debug}")
    logger.info(f"API Version: {settings.api_version}")
    
    yield
    
    # Shutdown
    logger.info("🛑 Shutting down Web Content Analyzer API...")
    await analysis_service.cleanup()

# Create FastAPI application
app = FastAPI(
    title=settings.api_title,
    description=settings.api_description,
    version=settings.api_version,
    debug=settings.debug,
    lifespan=lifespan,
    docs_url="/docs" if settings.debug else None,
    redoc_url="/redoc" if settings.debug else None,
)

# Security Middleware - Trusted Host
app.add_middleware(
    TrustedHostMiddleware, 
    allowed_hosts=["localhost", "127.0.0.1", "backend", "frontend"] + settings.allowed_domains
)

# CORS Middleware Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
    expose_headers=["*"],
)

# Request logging middleware
@app.middleware("http")
async def log_requests(request: Request, call_next):
    """Log all HTTP requests with timing"""
    start_time = time.time()
    
    # Log request
    logger.info(f"🔄 {request.method} {request.url.path} - Client: {request.client.host}")
    
    try:
        response = await call_next(request)
        
        # Calculate processing time
        process_time = time.time() - start_time
        
        # Log response
        logger.info(
            f"✅ {request.method} {request.url.path} - "
            f"Status: {response.status_code} - "
            f"Time: {process_time:.3f}s"
        )
        
        # Add timing header
        response.headers["X-Process-Time"] = str(process_time)
        
        return response
        
    except Exception as e:
        process_time = time.time() - start_time
        logger.error(
            f"❌ {request.method} {request.url.path} - "
            f"Error: {str(e)} - "
            f"Time: {process_time:.3f}s"
        )
        raise

# Global exception handler
@app.exception_handler(WebAnalyzerException)
async def web_analyzer_exception_handler(request: Request, exc: WebAnalyzerException):
    """Handle custom Web Analyzer exceptions"""
    logger.error(f"WebAnalyzer Exception: {exc.detail} - URL: {request.url}")
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": exc.error_type,
            "detail": exc.detail,
            "url": str(request.url.path),
            "timestamp": time.time()
        }
    )

@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    """Handle HTTP exceptions"""
    logger.error(f"HTTP Exception: {exc.detail} - URL: {request.url}")
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": "HTTP_ERROR",
            "detail": exc.detail,
            "url": str(request.url.path),
            "timestamp": time.time()
        }
    )

@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """Handle unexpected exceptions"""
    logger.error(f"Unexpected Exception: {str(exc)} - URL: {request.url}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={
            "error": "INTERNAL_SERVER_ERROR",
            "detail": "An unexpected error occurred",
            "url": str(request.url.path),
            "timestamp": time.time()
        }
    )

# Health check endpoint
@app.get("/health", tags=["Health"])
async def health_check() -> Dict[str, Any]:
    """Health check endpoint for monitoring"""
    return {
        "status": "healthy",
        "service": "web-content-analyzer",
        "version": settings.api_version,
        "environment": settings.environment,
        "timestamp": time.time()
    }

# Root endpoint
@app.get("/", tags=["Root"])
async def root() -> Dict[str, str]:
    """Root endpoint with API information"""
    return {
        "message": "Web Content Analyzer API",
        "version": settings.api_version,
        "docs": "/docs" if settings.debug else "Documentation disabled in production",
        "health": "/health",
        "status": "/status"
    }

# Simple status endpoint
@app.get("/status", tags=["Health"])
async def simple_status() -> Dict[str, Any]:
    """Simple status endpoint for quick checks"""
    return {
        "status": "running",
        "service": "web-content-analyzer-api",
        "version": settings.api_version,
        "environment": settings.environment,
        "timestamp": time.time(),
        "detailed_status": "/api/v1/status"
    }

# Include API routes
# Register batch router first so explicit routes like /analyze/history are not
# shadowed by generic param routes (e.g. /analyze/{analysis_id}) in api_router.
app.include_router(batch_router, prefix="/api/v1", tags=["Batch API"])
app.include_router(api_router, prefix="/api/v1", tags=["API"])
app.include_router(enhanced_router, prefix="/api/v1/enhanced", tags=["Enhanced API"])

# Application entry point
if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.reload and settings.debug,
        log_level=settings.log_level.lower(),
        access_log=settings.debug
    )
