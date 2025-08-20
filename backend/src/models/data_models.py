"""
Data Models - Placeholder for M1 Foundation
Basic models to support API structure - will be expanded in data layer implementation
"""
from pydantic import BaseModel, Field, HttpUrl
from typing import List, Dict, Any, Optional
from datetime import datetime

class URLAnalysisRequest(BaseModel):
    """Request model for URL analysis - placeholder"""
    url: HttpUrl = Field(..., description="URL to analyze")
    options: Dict[str, Any] = Field(default_factory=dict, description="Analysis options")

class AnalysisReport(BaseModel):
    """Analysis report model - placeholder"""
    url: str
    title: str
    summary: str
    content_type: str
    word_count: int
    readability_score: float
    language: str
    keywords: List[str]
    key_sections: List[Dict[str, Any]]
    contact_information: Dict[str, List[str]]
    metadata: Dict[str, Any]
    analysis_timestamp: float
    processing_time: float

class ErrorResponse(BaseModel):
    """Error response model"""
    error: str
    detail: str
    url: Optional[str] = None
    timestamp: float = Field(default_factory=lambda: datetime.now().timestamp())

# Note: Complete data models will be implemented in M1-DATA-04 phase
