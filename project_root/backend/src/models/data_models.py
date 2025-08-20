from pydantic import BaseModel, HttpUrl
from typing import List, Optional, Dict, Any
from datetime import datetime

class ScrapedContent(BaseModel):
    """Model for scraped content data with enhanced metadata"""
    url: HttpUrl
    final_url: HttpUrl
    html: str
    text: str
    content_length: int
    success: bool
    error_message: Optional[str] = None
    # Enhanced fields
    metadata: Optional[Dict[str, Any]] = None
    extraction_method: Optional[str] = None
    confidence: Optional[float] = None

class ScrapeResult(BaseModel):
    """Legacy model for backwards compatibility"""
    url: HttpUrl
    html: str
    text: str

class AnalysisResult(BaseModel):
    summary: str
    keywords: List[str]
    length: int

class Report(BaseModel):
    source_url: HttpUrl
    summary: str
    keywords: List[str]
    content_length: int

# Structured AI analysis output format (example schema)
class AIAnalysisSchema(BaseModel):
    id: Optional[str]
    summary: str
    topics: List[str]
    sentiment: Optional[str]
    entities: Optional[List[str]]
