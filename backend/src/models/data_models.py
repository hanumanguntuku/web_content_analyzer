"""
Data Models - M1-DATA-04 Implementation
Comprehensive data models for web content analysis pipeline
"""
from pydantic import BaseModel, Field, HttpUrl, validator
from typing import List, Dict, Any, Optional, Union
from datetime import datetime
from dataclasses import dataclass
from enum import Enum
import logging

# Enterprise logging setup
logger = logging.getLogger("web_content_analyzer.models")
if not logger.hasHandlers():
    handler = logging.StreamHandler()
    formatter = logging.Formatter('[%(asctime)s] %(levelname)s %(name)s: %(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler)
logger.setLevel(logging.INFO)
# Enums for structured data
class ContentType(str, Enum):
    """Content types for classification"""
    ARTICLE = "article"
    BLOG_POST = "blog_post"
    NEWS = "news"
    PRODUCT_PAGE = "product_page"
    LANDING_PAGE = "landing_page"
    DOCUMENTATION = "documentation"
    FORUM_POST = "forum_post"
    SOCIAL_MEDIA = "social_media"
    UNKNOWN = "unknown"

class ProcessingStatus(str, Enum):
    """Processing status indicators"""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    TIMEOUT = "timeout"

class ScrapingStatus(str, Enum):
    """Scraping status enumeration"""
    PENDING = "pending"
    CONNECTING = "connecting"
    DOWNLOADING = "downloading"
    PARSING = "parsing"
    COMPLETED = "completed"
    FAILED = "failed"

class ProcessingStage(str, Enum):
    """Processing stage enumeration"""
    VALIDATION = "validation"
    SCRAPING = "scraping"
    EXTRACTION = "extraction"
    ANALYSIS = "analysis"
    REPORTING = "reporting"
    COMPLETE = "complete"

class QualityLevel(str, Enum):
    """Content quality levels"""
    EXCELLENT = "excellent"  # 80-100
    GOOD = "good"           # 60-79
    FAIR = "fair"           # 40-59
    POOR = "poor"           # 0-39

# Request Models
class URLAnalysisRequest(BaseModel):
    """Request model for URL analysis"""
    url: HttpUrl = Field(..., description="URL to analyze")
    options: Dict[str, Any] = Field(default_factory=dict, description="Analysis options")
    deep_analysis: bool = Field(default=True, description="Enable deep content analysis")
    extract_media: bool = Field(default=True, description="Extract media information")
    extract_contacts: bool = Field(default=True, description="Extract contact information")
    
    @validator('url')
    def validate_url(cls, v):
        """Validate URL format and security"""
        url_str = str(v)
        if any(blocked in url_str.lower() for blocked in ['localhost', '127.0.0.1', '192.168.']):
            logger.warning(f"Blocked attempt to analyze private/local URL: {url_str}")
            raise ValueError("Private/local URLs are not allowed")
        logger.info(f"Validated URL for analysis: {url_str}")
        return v

class AnalysisOptions(BaseModel):
    """Analysis configuration options"""
    timeout: int = Field(default=30, ge=5, le=120, description="Request timeout in seconds")
    max_content_size: int = Field(default=10485760, description="Maximum content size in bytes")
    follow_redirects: bool = Field(default=True, description="Follow HTTP redirects")
    extract_images: bool = Field(default=True, description="Extract image information")
    extract_links: bool = Field(default=True, description="Extract link information")
    language_detection: bool = Field(default=True, description="Detect content language")

# Content Section Model
@dataclass
class ContentSection:
    """Represents a section of content"""
    type: str
    content: str
    word_count: int
    headings: Dict[str, List[str]]

# Core Content Models
class ScrapedContent(BaseModel):
    """Raw scraped content from web scraper"""
    url: str = Field(..., description="Source URL")
    title: str = Field(..., description="Page title")
    description: str = Field(default="", description="Meta description")
    content: str = Field(..., description="Main content text")
    headings: Dict[str, List[str]] = Field(default_factory=dict, description="Heading hierarchy")
    links: List[Dict[str, Any]] = Field(default_factory=list, description="Extracted links")
    images: List[Dict[str, Any]] = Field(default_factory=list, description="Extracted images")
    meta_data: Dict[str, Any] = Field(default_factory=dict, description="Page metadata")
    word_count: int = Field(default=0, description="Word count")
    page_size: int = Field(default=0, description="Page size in bytes")
    load_time: float = Field(default=0.0, description="Page load time in seconds")
    status_code: int = Field(default=200, description="HTTP status code")
    content_type: str = Field(default="text/html", description="Content MIME type")
    language: Optional[str] = Field(default=None, description="Detected language")
    emails: List[str] = Field(default_factory=list, description="Extracted email addresses")
    phones: List[str] = Field(default_factory=list, description="Extracted phone numbers")
    success: bool = Field(default=True, description="Scraping success status")
    error: Optional[str] = Field(default=None, description="Error message if failed")

class ExtractedContent(BaseModel):
    """Processed content from content extractor"""
    url: str = Field(..., description="Source URL")
    main_content: str = Field(..., description="Main content text")
    headings: Dict[str, List[str]] = Field(default_factory=dict, description="Structured headings")
    links: List[Dict[str, Any]] = Field(default_factory=list, description="Categorized links")
    images: List[Dict[str, Any]] = Field(default_factory=list, description="Image metadata")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Page metadata")
    word_count: int = Field(default=0, description="Word count of main content")
    sections: List[Dict[str, Any]] = Field(default_factory=list, description="Content sections")
    extraction_quality: float = Field(default=0.0, ge=0.0, le=100.0, description="Extraction quality score")
    
    class Config:
        arbitrary_types_allowed = True

class ProcessedContent(BaseModel):
    """Fully processed content from text processor"""
    url: str = Field(..., description="Source URL")
    cleaned_text: str = Field(..., description="Cleaned and normalized text")

    keywords: List[Dict[str, Any]] = Field(default_factory=list, description="Extracted keywords")
    emails: List[str] = Field(default_factory=list, description="Email addresses")
    phones: List[str] = Field(default_factory=list, description="Phone numbers")
    language: str = Field(default="unknown", description="Detected language")
    readability: Dict[str, float] = Field(default_factory=dict, description="Readability scores")
    entities: Dict[str, List[str]] = Field(default_factory=dict, description="Named entities")
    analysis: Dict[str, Any] = Field(default_factory=dict, description="Content analysis")
    processing_quality: float = Field(default=0.0, ge=0.0, le=100.0, description="Processing quality score")
    word_count: int = Field(default=0, description="Word count")
    character_count: int = Field(default=0, description="Character count")
    paragraph_count: int = Field(default=0, description="Paragraph count")
    sentence_count: int = Field(default=0, description="Sentence count")
    readability_score: float = Field(default=0.0, description="Readability score")
    headings: List[Dict[str, Any]] = Field(default_factory=list, description="Page headings")
    sections: List[Dict[str, Any]] = Field(default_factory=list, description="Content sections")
    sentiment_score: float = Field(default=0.0, description="Sentiment analysis score")
    topics: List[str] = Field(default_factory=list, description="Identified topics")
    internal_links: List[Dict[str, Any]] = Field(default_factory=list, description="Internal links")
    external_links: List[Dict[str, Any]] = Field(default_factory=list, description="External links")
    images: List[Dict[str, Any]] = Field(default_factory=list, description="Images metadata")
    contact_information: Dict[str, List[str]] = Field(default_factory=dict, description="Contact information")
    # Additional summary/metrics fields for frontend completeness
    processing_time: float = Field(default=0.0, description="Total processing time in seconds")
    performance_score: float = Field(default=0.0, description="Overall performance score")
    scraping_time: float = Field(default=0.0, description="Scraping time in seconds")
    extraction_time: float = Field(default=0.0, description="Content extraction time in seconds")
    analysis_time: float = Field(default=0.0, description="Analysis time in seconds")
    content_size: int = Field(default=0, description="Content size in bytes")
    content_quality_score: float = Field(default=0.0, description="Content quality score")
    extraction_quality: float = Field(default=0.0, description="Extraction quality score")
    http_status: int = Field(default=200, description="HTTP status code")
    response_time: float = Field(default=0.0, description="Response time in seconds")
    redirect_count: int = Field(default=0, description="Number of redirects")

# Analysis Report Models
class ContentAnalysis(BaseModel):
    """Detailed content analysis results"""
    content_type: ContentType = Field(default=ContentType.UNKNOWN, description="Classified content type")
    quality_level: QualityLevel = Field(..., description="Content quality assessment")
    readability_score: float = Field(default=0.0, description="Readability score (e.g., Flesch Reading Ease)")
    sentiment_score: Optional[float] = Field(default=None, description="Sentiment analysis score (-1 to 1)")
    sentiment_label: Optional[str] = Field(default=None, description="Sentiment label (e.g., Positive, Neutral)")
    detected_tones: List[str] = Field(default_factory=list, description="Detected content tones (e.g., Formal, Optimistic)")
    topic_categories: List[str] = Field(default_factory=list, description="Topic categories")
    key_themes: List[str] = Field(default_factory=list, description="Key themes")
    content_density: float = Field(default=0.0, description="Content density score")
    uniqueness_score: float = Field(default=0.0, description="Content uniqueness score")
    seo_score: float = Field(default=0.0, description="SEO friendliness score (0-100)")
    seo_recommendations: List[str] = Field(default_factory=list, description="Actionable SEO recommendations")
    accessibility_score: float = Field(default=0.0, description="Accessibility score (0-100)")
    accessibility_notes: List[str] = Field(default_factory=list, description="Actionable accessibility recommendations")

class AnalysisMetrics(BaseModel):
    """Performance and analysis metrics"""
    processing_time: float = Field(default=0.0, description="Total processing time in seconds")
    scraping_time: float = Field(default=0.0, description="Scraping time in seconds")
    extraction_time: float = Field(default=0.0, description="Content extraction time in seconds")
    analysis_time: float = Field(default=0.0, description="Analysis time in seconds")
    # Content metrics
    content_size: int = Field(default=0, description="Content size in bytes")
    word_count: int = Field(default=0, description="Word count")
    character_count: int = Field(default=0, description="Character count")
    paragraph_count: int = Field(default=0, description="Paragraph count")
    sentence_count: int = Field(default=0, description="Sentence count")
    readability_score: float = Field(default=0.0, description="Readability score")
    image_count: int = Field(default=0, description="Number of images")
    link_count: int = Field(default=0, description="Number of links")
    # Quality metrics
    performance_score: float = Field(default=0.0, description="Overall performance score")
    content_quality_score: float = Field(default=0.0, description="Content quality score")
    extraction_quality: float = Field(default=0.0, description="Extraction quality score")
    # Technical metrics
    http_status: int = Field(default=200, description="HTTP status code")
    response_time: float = Field(default=0.0, description="Response time in seconds")
    redirect_count: int = Field(default=0, description="Number of redirects")

class TechnicalMetadata(BaseModel):
    """Technical metadata about the webpage"""
    domain: str = Field(..., description="Domain name")
    subdomain: Optional[str] = Field(default=None, description="Subdomain")
    path: str = Field(..., description="URL path")
    protocol: str = Field(..., description="Protocol (http/https)")
    encoding: Optional[str] = Field(default=None, description="Character encoding")
    server: Optional[str] = Field(default=None, description="Server information")
    cms: Optional[str] = Field(default=None, description="Detected CMS")
    framework: Optional[str] = Field(default=None, description="Detected framework")

class AnalysisReport(BaseModel):
    def __init__(self, **data):
        super().__init__(**data)
        logger.info(f"AnalysisReport created for URL: {self.url} | Status: {self.processing_status} | Time: {self.analysis_timestamp}")
    """Comprehensive analysis report"""
    # Basic Information
    url: str = Field(..., description="Analyzed URL")
    title: str = Field(..., description="Page title")
    description: str = Field(default="", description="Page description")
    
    # Content Analysis
    content_analysis: ContentAnalysis = Field(..., description="Content analysis results")
    
    # Metrics
    word_count: int = Field(default=0, description="Total word count")
    character_count: int = Field(default=0, description="Total character count")
    paragraph_count: int = Field(default=0, description="Number of paragraphs")
    heading_count: int = Field(default=0, description="Total number of headings")
    link_count: int = Field(default=0, description="Number of links")
    image_count: int = Field(default=0, description="Number of images")
    
    # Extracted Data
    keywords: List[Dict[str, Any]] = Field(default_factory=list, description="Top keywords")
    key_sections: List[Dict[str, Any]] = Field(default_factory=list, description="Key content sections")
    contact_information: Dict[str, List[str]] = Field(default_factory=dict, description="Contact info")
    
    # Technical Data
    technical_metadata: TechnicalMetadata = Field(..., description="Technical metadata")
    performance_metrics: Dict[str, float] = Field(default_factory=dict, description="Performance metrics")
    
    # Processing Information
    processing_status: ProcessingStatus = Field(default=ProcessingStatus.COMPLETED, description="Processing status")
    processing_time: float = Field(default=0.0, description="Total processing time")
    analysis_timestamp: datetime = Field(default_factory=datetime.now, description="Analysis timestamp")
    
    # Quality Scores
    overall_quality_score: float = Field(default=0.0, ge=0.0, le=100.0, description="Overall quality score")
    extraction_quality: float = Field(default=0.0, ge=0.0, le=100.0, description="Extraction quality")
    processing_quality: float = Field(default=0.0, ge=0.0, le=100.0, description="Processing quality")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata including AI summary, outline, etc.")

# Error Models
class ValidationError(BaseModel):
    """Validation error details"""
    field: str = Field(..., description="Field with validation error")
    message: str = Field(..., description="Error message")
    value: Any = Field(default=None, description="Invalid value")

class ErrorResponse(BaseModel):
    """Comprehensive error response"""
    error: str = Field(..., description="Error type")
    message: str = Field(..., description="Human-readable error message")
    detail: Optional[str] = Field(default=None, description="Detailed error information")
    url: Optional[str] = Field(default=None, description="URL that caused the error")
    status_code: int = Field(default=500, description="HTTP status code")
    timestamp: datetime = Field(default_factory=datetime.now, description="Error timestamp")
    validation_errors: List[ValidationError] = Field(default_factory=list, description="Validation errors")
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }

# Response Models
class AnalysisResponse(BaseModel):
    """Response model for analysis endpoints"""
    success: bool = Field(..., description="Operation success status")
    data: Optional[Union[AnalysisReport, Dict[str, Any]]] = Field(default=None, description="Response data")
    error: Optional[ErrorResponse] = Field(default=None, description="Error information")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Response metadata")

class HealthResponse(BaseModel):
    """Health check response"""
    status: str = Field(default="healthy", description="Service status")
    timestamp: datetime = Field(default_factory=datetime.now, description="Health check timestamp")
    version: str = Field(default="1.0.0", description="API version")
    uptime: float = Field(default=0.0, description="Service uptime in seconds")

# Utility Models
class ProcessingProgress(BaseModel):
    """Processing progress information"""
    stage: str = Field(..., description="Current processing stage")
    progress: float = Field(..., ge=0.0, le=100.0, description="Progress percentage")
    message: str = Field(default="", description="Status message")
    estimated_completion: Optional[datetime] = Field(default=None, description="Estimated completion time")

# Legacy compatibility for existing code
class URLAnalysisRequest_Legacy(BaseModel):
    """Legacy request model for backward compatibility"""
    url: str
    options: Dict[str, Any] = Field(default_factory=dict)
