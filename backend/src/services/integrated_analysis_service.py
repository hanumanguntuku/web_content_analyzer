"""
Integrated Content Analysis Service - M1-SVC-01 Implementation
Enhanced service integrating all Milestone 1 components
"""

import asyncio
import logging
from typing import Optional, Dict, Any
from datetime import datetime
import time

from .scraping_service import WebScraperService
from .report_service import ReportService
from .content_detection_service import ContentTypeDetectionService
from ..scrapers.content_extractor import ContentExtractor
from ..scrapers.web_scraper import WebScraperService as WebScraper
from ..processors.text_processor import TextProcessor
from ..utils.url_validator import URLValidator
from ..utils.security import ContentSanitizer
from ..utils.resource_limits import RateLimiter, ContentSizeLimiter, ResourceMonitor
from ..models.data_models import (
    AnalysisReport,
    AnalysisMetrics,
    ProcessedContent,
    ScrapingStatus,
    ProcessingStage,
    ContentAnalysis
)
from ..services.llm_service import GeminiLLMService
from ..utils.exceptions import (
    ScrapingException,
    ExtractionException,
    TextProcessingException,
    SecurityException,
    ValidationException,
    RateLimitException,
    ContentSizeException,
    ResourceException,
    ProcessingException
)

# Configure logging
logger = logging.getLogger(__name__)

class IntegratedAnalysisService:
    """
    Integrated web content analysis service combining all Milestone 1 components
    
    Features:
    - Security validation and SSRF prevention
    - Rate limiting and resource management
    - Intelligent content extraction
    - Deep text processing and analysis
    - Content sanitization
    - Comprehensive reporting
    """
    
    def __init__(
        self,
        rate_limit_requests: int = 100,
        rate_limit_window: int = 3600,  # 1 hour
        max_content_size: int = 10 * 1024 * 1024,  # 10MB
        request_timeout: int = 30
    ):
        """Initialize the integrated analysis service"""
        
        # Core services
        self.scraper = WebScraperService()
        self.web_scraper = WebScraper()
        self.report_service = ReportService()
        self.content_detection_service = ContentTypeDetectionService()
        self.llm_service = GeminiLLMService()
        
        # Data layer components
        self.content_extractor = ContentExtractor()
        self.text_processor = TextProcessor()
        
        # Security components
        self.url_validator = URLValidator()
        self.content_sanitizer = ContentSanitizer()
        
        # Resource management
        self.rate_limiter = RateLimiter()
        self.size_limiter = ContentSizeLimiter()
        self.resource_monitor = ResourceMonitor()
        
        # Configuration
        self.max_content_size = max_content_size
        self.request_timeout = request_timeout
        
        # Performance tracking
        self.stats = {
            'total_analyses': 0,
            'successful_analyses': 0,
            'failed_analyses': 0,
            'security_blocks': 0,
            'rate_limit_hits': 0,
            'total_processing_time': 0.0,
            'average_processing_time': 0.0
        }
        
        logger.info("IntegratedAnalysisService initialized with all Milestone 1 components")
    
    async def analyze_url(self, url: str) -> AnalysisReport:
        """
        Main analysis method called by API routes
        
        Args:
            url: URL to analyze
            
        Returns:
            Complete analysis report
        """
        try:
            logger.info(f"🔍 Starting URL analysis for: {url}")
            # Step 1: Scrape content
            scraped_data = await self.web_scraper.scrape_website(url)

            # Step 2: Extract and process content
            processed_data = self.text_processor.process_content(
                scraped_data.content, url, html=getattr(scraped_data, 'content', None)
            )

            # Convert dictionary to ProcessedContent object
            processed_content = ProcessedContent(
                url=url,
                cleaned_text=processed_data.get('cleaned_text', ''),
                keywords=processed_data.get('keywords', []),
                emails=processed_data.get('emails', []),
                phones=processed_data.get('phones', []),
                language=processed_data.get('language', 'unknown'),
                readability=processed_data.get('readability', {}),
                entities=processed_data.get('entities', {}),
                analysis=processed_data.get('analysis', {}),
                processing_quality=processed_data.get('processing_quality', 0.0),
                word_count=len(processed_data.get('cleaned_text', '').split()),
                character_count=len(processed_data.get('cleaned_text', '')),
                paragraph_count=processed_data.get('cleaned_text', '').count('\n\n') + 1,
                sentence_count=processed_data.get('cleaned_text', '').count('.') + processed_data.get('cleaned_text', '').count('!') + processed_data.get('cleaned_text', '').count('?'),
                readability_score=processed_data.get('readability_score', 0.0),
                extraction_quality=processed_data.get('extraction_quality', 0.0),
                headings=processed_data.get('analysis', {}).get('headings', []),
                sections=processed_data.get('analysis', {}).get('sections', []),
                sentiment_score=0.0,  # Default sentiment score (can be enhanced later with actual sentiment analysis)
                topics=[],  # Default empty topics list (can be enhanced later with topic modeling)
                internal_links=processed_data.get('analysis', {}).get('internal_links', []),
                external_links=processed_data.get('analysis', {}).get('external_links', []),
                images=processed_data.get('analysis', {}).get('images', []),
                contact_information={'emails': processed_data.get('emails', []), 'phones': processed_data.get('phones', [])}
            )
            # Debug: Log processed_content after creation
            try:
                logger.info(f"[DEBUG] processed_content (type={type(processed_content)}): {str(processed_content)}")
            except Exception as e:
                logger.warning(f"[DEBUG] Could not stringify processed_content: {e}")

            # Step 3: Perform LLM-based analysis in parallel
            llm_tasks = {
                "summary": self.llm_service.get_content_summary(processed_content.cleaned_text),
                "sentiment": self.llm_service.get_sentiment_and_tone(processed_content.cleaned_text),
                "seo": self.llm_service.get_seo_recommendations(
                    processed_content.cleaned_text, 
                    scraped_data.title, 
                    [kw['keyword'] for kw in processed_content.keywords[:5]]
                ),
                "readability": self.llm_service.get_readability_and_accessibility(processed_content.cleaned_text)
            }
            
            llm_results = await asyncio.gather(*llm_tasks.values(), return_exceptions=True)
            
            llm_analysis = dict(zip(llm_tasks.keys(), llm_results))

            # Log any LLM errors but don't fail the whole analysis
            for task, result in llm_analysis.items():
                if isinstance(result, Exception):
                    logger.error(f"LLM task '{task}' failed: {result}")
                    llm_analysis[task] = None # Nullify failed tasks

            # Step 4: Detect content type
            content_type, confidence, detection_details = await self.content_detection_service.detect_content_type(
                processed_content, url
            )

            # Step 5: Generate the final report, now including LLM analysis
            analysis_report = await self.report_service.generate_analysis_report(
                processed_content, 
                scraped_data, 
                url,
                llm_analysis # Pass the LLM results to the report service
            )

            logger.info(f"✅ Analysis completed for {url}")
            return analysis_report
        except Exception as e:
            logger.error(f"❌ Analysis failed for {url}: {str(e)}")
            raise ProcessingException(f"URL analysis failed: {str(e)}")
    
    async def analyze_content(
        self,
        url: str,
        client_ip: str = "127.0.0.1",
        deep_analysis: bool = True,
        extract_images: bool = True,
        extract_links: bool = True
    ) -> AnalysisReport:
        """
        Perform comprehensive content analysis
        
        Args:
            url: URL to analyze
            client_ip: Client IP for rate limiting
            deep_analysis: Enable deep text processing
            extract_images: Extract image information
            extract_links: Extract link information
            
        Returns:
            Comprehensive analysis report
        """
        start_time = time.time()
        analysis_id = f"analysis_{int(start_time)}_{hash(url) % 10000}"
        
        try:
            self.stats['total_analyses'] += 1
            
            logger.info(f"Starting content analysis for {url} (ID: {analysis_id})")
            
            # Phase 1: Security and validation
            await self._perform_security_validation(url, client_ip)
            
            # Phase 2: Web scraping
            scraped_data = await self._scrape_content(url)
            
            # Phase 3: Content extraction
            extracted_content = await self._extract_intelligent_content(scraped_data, url)
            
            # Phase 4: Text processing
            processed_content = await self._process_text_content(
                extracted_content, 
                deep_analysis=deep_analysis
            )
            
            # Phase 5: Generate comprehensive report
            analysis_report = await self._generate_comprehensive_report(
                url=url,
                scraped_data=scraped_data,
                extracted_content=extracted_content,
                processed_content=processed_content,
                extract_images=extract_images,
                extract_links=extract_links,
                processing_time=time.time() - start_time,
                analysis_id=analysis_id
            )
            
            # Update success statistics
            self.stats['successful_analyses'] += 1
            self._update_performance_stats(time.time() - start_time)
            
            logger.info(f"Content analysis completed successfully for {url} (ID: {analysis_id})")
            return analysis_report
            
        except Exception as e:
            # Update failure statistics
            self.stats['failed_analyses'] += 1
            self._update_performance_stats(time.time() - start_time)
            
            if isinstance(e, (SecurityException, ValidationException)):
                self.stats['security_blocks'] += 1
            elif isinstance(e, RateLimitException):
                self.stats['rate_limit_hits'] += 1
            
            logger.error(f"Content analysis failed for {url} (ID: {analysis_id}): {str(e)}")
            
            # Return error report
            return self._create_error_report(url, e, time.time() - start_time, analysis_id)
    
    async def _perform_security_validation(self, url: str, client_ip: str):
        """Perform comprehensive security validation"""
        try:
            logger.debug(f"Performing security validation for {url}")
            
            # Step 1: Rate limiting check
            if not await self.rate_limiter.check_rate_limit(client_ip):
                raise RateLimitException(
                    "Rate limit exceeded for client", 
                    client_ip=client_ip
                )
            
            # Step 2: URL security validation
            validation_result = await self.url_validator.validate_url(url)
            if not validation_result.is_valid:
                raise ValidationException(
                    f"URL validation failed: {validation_result.error_message}",
                    context={'url': url, 'errors': validation_result.error_message}
                )
            
            # Step 3: Resource availability check
            resource_stats = self.resource_monitor.get_resource_stats()
            if 'error' in resource_stats or resource_stats.get('available_slots', 0) <= 0:
                raise ResourceException("System resources exhausted")
            
            logger.debug(f"Security validation passed for {url}")
            
        except Exception as e:
            logger.error(f"Security validation failed for {url}: {str(e)}")
            raise
    
    async def _scrape_content(self, url: str):
        """Scrape content using the web scraper service"""
        try:
            logger.debug(f"Scraping content from {url}")
            
            # Use the existing web scraper service
            scraped_content = await self.scraper.scrape_url(url)
            
            # Validate content size
            content_size = scraped_content.page_size
            if content_size > self.max_content_size:
                raise ContentSizeException(
                    "Content size exceeds maximum limit",
                    size=content_size,
                    limit=self.max_content_size
                )
            
            logger.debug(f"Successfully scraped {content_size} bytes from {url}")
            return scraped_content
            
        except Exception as e:
            logger.error(f"Content scraping failed for {url}: {str(e)}")
            if not isinstance(e, (ContentSizeException, ScrapingException)):
                raise ScrapingException(f"Scraping failed: {str(e)}", url=url)
            raise
    
    async def _extract_intelligent_content(self, scraped_data, url: str):
        """Extract intelligent content using content extractor"""
        try:
            logger.debug(f"Extracting intelligent content from {url}")
            
            # Sanitize content for security
            sanitized_content = await self.content_sanitizer.sanitize_content(
                scraped_data.content
            )
            
            # Extract content using intelligent extractor
            extracted_content = await self.content_extractor.extract_content(
                sanitized_content, url
            )
            
            logger.debug(f"Successfully extracted content from {url}")
            return extracted_content
            
        except Exception as e:
            logger.error(f"Content extraction failed for {url}: {str(e)}")
            raise ExtractionException(f"Content extraction failed: {str(e)}", url=url)
    
    async def _process_text_content(self, extracted_content, deep_analysis: bool = True):
        """Process text content using text processor"""
        try:
            logger.debug("Processing text content with deep analysis")
            
            # Process text using text processor
            processed_content = await self.text_processor.process_content(
                extracted_content,
                deep_analysis=deep_analysis
            )
            
            logger.debug("Successfully processed text content")
            return processed_content
            
        except Exception as e:
            logger.error(f"Text processing failed: {str(e)}")
            raise TextProcessingException(f"Text processing failed: {str(e)}")
    
    async def _generate_comprehensive_report(
        self,
        url: str,
        scraped_data,
        extracted_content,
        processed_content,
        extract_images: bool,
        extract_links: bool,
        processing_time: float,
        analysis_id: str
    ) -> AnalysisReport:
        """Generate comprehensive analysis report"""
        try:
            logger.debug(f"Generating comprehensive report for {url}")

            # Step 1: Run LLM-based analysis in parallel (summary, sentiment, seo, readability)
            llm_tasks = {
                "summary": self.llm_service.get_content_summary(processed_content.cleaned_text),
                "sentiment": self.llm_service.get_sentiment_and_tone(processed_content.cleaned_text),
                "seo": self.llm_service.get_seo_recommendations(
                    processed_content.cleaned_text,
                    getattr(scraped_data, 'title', ''),
                    [kw['keyword'] for kw in getattr(processed_content, 'keywords', [])[:5]]
                ),
                "readability": self.llm_service.get_readability_and_accessibility(processed_content.cleaned_text)
            }
            import asyncio
            llm_results = await asyncio.gather(*llm_tasks.values(), return_exceptions=True)
            llm_analysis = dict(zip(llm_tasks.keys(), llm_results))
            # Nullify failed tasks
            for task, result in llm_analysis.items():
                if isinstance(result, Exception):
                    logger.error(f"LLM task '{task}' failed: {result}")
                    llm_analysis[task] = None

            # Step 2: Generate the final report, now including LLM analysis
            analysis_report = await self.report_service.generate_analysis_report(
                processed_content,
                scraped_data,
                url,
                llm_analysis
            )
            return analysis_report
        except Exception as e:
            logger.error(f"Failed to generate comprehensive report for {url}: {str(e)}", exc_info=True)
            raise ProcessingException(f"Report generation failed: {str(e)}", url=url)
    
    def _create_error_report(
        self, 
        url: str, 
        error: Exception, 
        processing_time: float,
        analysis_id: str
    ) -> AnalysisReport:
        """Create error report for failed analysis"""
        return AnalysisReport(
            url=url,
            title="Analysis Failed",
            summary=f"Content analysis failed: {str(error)}",
            keywords=[],
            content_type="unknown",
            language="unknown",
            metrics=AnalysisMetrics(
                processing_time=processing_time,
                content_size=0,
                word_count=0,
                readability_score=0,
                keyword_density=0,
                image_count=0,
                link_count=0,
                performance_score=0
            ),
            images=[],
            links=[],
            metadata={
                'analysis_id': analysis_id,
                'error': str(error),
                'error_type': type(error).__name__,
                'processing_stage': ProcessingStage.FAILED.value,
                'security_scanned': isinstance(error, (SecurityException, ValidationException))
            },
            analyzed_at=datetime.utcnow(),
            status=ScrapingStatus.FAILED
        )
    
    def _update_performance_stats(self, processing_time: float):
        """Update performance statistics"""
        self.stats['total_processing_time'] += processing_time
        if self.stats['total_analyses'] > 0:
            self.stats['average_processing_time'] = (
                self.stats['total_processing_time'] / self.stats['total_analyses']
            )
    
    async def get_service_health(self) -> Dict[str, Any]:
        """Get comprehensive service health information"""
        try:
            # Check component health
            component_health = {
                'scraper': self.scraper is not None,
                'content_extractor': self.content_extractor is not None,
                'text_processor': self.text_processor is not None,
                'url_validator': self.url_validator is not None,
                'content_sanitizer': self.content_sanitizer is not None,
                'rate_limiter': self.rate_limiter is not None,
                'resource_monitor': self.resource_monitor is not None
            }
            
            # Check system resources
            resource_stats = self.resource_monitor.get_resource_stats()
            resources_healthy = 'error' not in resource_stats and resource_stats.get('available_slots', 0) > 0
            
            # Calculate success rate
            success_rate = 0.0
            if self.stats['total_analyses'] > 0:
                success_rate = (
                    self.stats['successful_analyses'] / self.stats['total_analyses']
                ) * 100
            
            overall_healthy = all(component_health.values()) and resources_healthy
            
            return {
                'status': 'healthy' if overall_healthy else 'degraded',
                'components': component_health,
                'system_resources': {
                    'available': resources_healthy,
                    'details': self.resource_monitor.get_resource_stats()
                },
                'performance': {
                    'success_rate': round(success_rate, 2),
                    'average_processing_time': round(self.stats['average_processing_time'], 3),
                    'total_analyses': self.stats['total_analyses']
                },
                'security': {
                    'rate_limit_config': {
                        'max_per_minute': self.rate_limiter.max_requests_per_minute,
                        'max_per_hour': self.rate_limiter.max_requests_per_hour,
                        'max_per_day': self.rate_limiter.max_requests_per_day
                    },
                    'security_blocks': self.stats['security_blocks'],
                    'rate_limit_hits': self.stats['rate_limit_hits']
                },
                'timestamp': datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Health check failed: {str(e)}")
            return {
                'status': 'unhealthy',
                'error': str(e),
                'timestamp': datetime.utcnow().isoformat()
            }
    
    def get_service_stats(self) -> Dict[str, Any]:
        """Get detailed service statistics"""
        return {
            **self.stats,
            'success_rate': (
                self.stats['successful_analyses'] / max(self.stats['total_analyses'], 1)
            ) * 100,
            'failure_rate': (
                self.stats['failed_analyses'] / max(self.stats['total_analyses'], 1)
            ) * 100,
            'security_block_rate': (
                self.stats['security_blocks'] / max(self.stats['total_analyses'], 1)
            ) * 100,
            'rate_limit_config': {
                'max_per_minute': self.rate_limiter.max_requests_per_minute,
                'max_per_hour': self.rate_limiter.max_requests_per_hour,
                'max_per_day': self.rate_limiter.max_requests_per_day
            },
            'resource_stats': self.resource_monitor.get_resource_stats()
        }
    
    async def cleanup(self):
        """Cleanup service resources"""
        try:
            if hasattr(self.scraper, 'close'):
                await self.scraper.close()
            logger.info("IntegratedAnalysisService cleaned up successfully")
        except Exception as e:
            logger.error(f"Cleanup failed: {str(e)}")
