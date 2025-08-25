"""
Report Generation Service - M1-SVC-02 Implementation
Comprehensive analysis report generation with metrics and insights
"""
import time
import logging
from datetime import datetime
from typing import Dict, Any, List, Optional
from urllib.parse import urlparse

from ..models.data_models import (
    AnalysisReport, ContentAnalysis, TechnicalMetadata, 
    ProcessedContent, ScrapedContent, ContentType, QualityLevel,
    ProcessingStatus
)
from ..utils.exceptions import ProcessingException

logger = logging.getLogger(__name__)

class MetricsCalculator:
    """Calculate various content and performance metrics"""
    
    def __init__(self):
        self.quality_thresholds = {
            'excellent': 85,
            'good': 70,
            'fair': 50,
            'poor': 0
        }
    
    async def calculate_all_metrics(self, 
                                  processed_content: ProcessedContent,
                                  scraped_data: ScrapedContent) -> Dict[str, Any]:
        """Calculate comprehensive metrics for content analysis"""
        
        try:
            # Performance metrics
            performance = {
                'response_time': scraped_data.load_time,
                'load_time': scraped_data.load_time,
                'content_size': len(scraped_data.content),
                'processing_efficiency': self._calculate_efficiency(processed_content, scraped_data)
            }
            
            # Content quality metrics
            quality_score = self._calculate_quality_score(processed_content)
            
            # Content metrics
            content_metrics = {
                'word_count': processed_content.word_count,
                'character_count': len(processed_content.cleaned_text),
                'paragraph_count': processed_content.paragraph_count,
                'sentence_count': processed_content.sentence_count,
                'readability_score': processed_content.readability_score,
                'keyword_density': self._calculate_keyword_density(processed_content)
            }
            
            return {
                'performance': performance,
                'quality_score': quality_score,
                'content': content_metrics,
                'processing_time': scraped_data.load_time
            }
            
        except Exception as e:
            logger.error(f"Error calculating metrics: {str(e)}")
            raise ProcessingException(f"Metrics calculation failed: {str(e)}")
    
    def _calculate_efficiency(self, processed_content: ProcessedContent, 
                            scraped_data: ScrapedContent) -> float:
        """Calculate processing efficiency score"""
        try:
            # Ratio of useful content to total content
            if not scraped_data.content:
                return 0.0
                
            useful_content_ratio = len(processed_content.cleaned_text) / len(scraped_data.content)
            
            # Time efficiency (faster = better, normalized to 0-100)
            time_efficiency = max(0, 100 - (scraped_data.load_time * 10))
            
            # Combined efficiency score
            return min(100, (useful_content_ratio * 50) + (time_efficiency * 0.5))
            
        except Exception:
            return 0.0
    
    def _calculate_quality_score(self, processed_content: ProcessedContent) -> float:
        """Calculate overall content quality score"""
        try:
            scores = []
            
            # Content length score (optimal range: 500-3000 words)
            word_count = processed_content.word_count
            if word_count >= 500 and word_count <= 3000:
                length_score = 100
            elif word_count < 500:
                length_score = (word_count / 500) * 100
            else:
                length_score = max(50, 100 - ((word_count - 3000) / 100))
            scores.append(length_score)
            
            # Readability score
            scores.append(processed_content.readability_score)
            
            # Structure score based on headings and paragraphs
            structure_score = min(100, (processed_content.paragraph_count * 10) + 
                                      (len(processed_content.headings) * 5))
            scores.append(structure_score)
            
            # Keyword relevance score
            keyword_score = min(100, len(processed_content.keywords) * 10)
            scores.append(keyword_score)
            
            # Average all scores
            return sum(scores) / len(scores) if scores else 0.0
            
        except Exception:
            return 0.0
    
    def _calculate_keyword_density(self, processed_content: ProcessedContent) -> Dict[str, float]:
        """Calculate keyword density metrics"""
        try:
            if not processed_content.keywords or not processed_content.word_count:
                return {}
                
            densities = {}
            for keyword_data in processed_content.keywords:
                keyword = keyword_data.get('keyword', '')
                frequency = keyword_data.get('frequency', 0)
                if keyword and frequency > 0:
                    density = (frequency / processed_content.word_count) * 100
                    densities[keyword] = round(density, 2)
                    
            return densities
            
        except Exception:
            return {}

class InsightsExtractor:
    """Extract insights and key information from processed content"""
    
    def __init__(self):
        self.content_type_keywords = {
            'article': ['article', 'story', 'news', 'blog', 'post'],
            'product_page': ['product', 'buy', 'price', 'cart', 'purchase'],
            'landing_page': ['sign up', 'register', 'join', 'subscribe'],
            'documentation': ['docs', 'guide', 'tutorial', 'manual'],
            'forum_post': ['forum', 'discussion', 'reply', 'comment']
        }
    
    async def extract_insights(self, processed_content: ProcessedContent, 
                             metrics: Dict[str, Any]) -> Dict[str, Any]:
        """Extract key insights from processed content"""
        
        try:
            return {
                'keywords': self._format_keywords(processed_content.keywords),
                'sections': self._extract_key_sections(processed_content),
                'content_classification': self._classify_content(processed_content),
                'quality_assessment': self._assess_quality(metrics['quality_score']),
                'recommendations': self._generate_recommendations(processed_content, metrics)
            }
            
        except Exception as e:
            logger.error(f"Error extracting insights: {str(e)}")
            return {
                'keywords': [],
                'sections': [],
                'content_classification': 'unknown',
                'quality_assessment': 'unknown',
                'recommendations': []
            }
    
    def _format_keywords(self, keywords: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Format keywords for report display"""
        try:
            formatted = []
            for i, keyword_data in enumerate(keywords[:10]):  # Top 10 keywords
                formatted.append({
                    'keyword': keyword_data.get('keyword', ''),
                    'frequency': keyword_data.get('frequency', 0),
                    'relevance': keyword_data.get('relevance', 0.0),
                    'rank': i + 1
                })
            return formatted
        except Exception:
            return []
    
    def _extract_key_sections(self, processed_content: ProcessedContent) -> List[Dict[str, Any]]:
        """Extract and format key content sections"""
        try:
            sections = []
            
            # Add headings as sections
            for i, heading in enumerate(processed_content.headings[:5]):  # Top 5 headings
                sections.append({
                    'title': heading.get('text', ''),
                    'level': heading.get('level', 1),
                    'type': 'heading',
                    'order': i + 1
                })
            
            # Add content sections if available
            if hasattr(processed_content, 'sections'):
                for section in processed_content.sections[:3]:  # Top 3 content sections
                    sections.append({
                        'title': section.get('title', 'Content Section'),
                        'content': section.get('content', '')[:200] + '...',  # Truncate
                        'word_count': section.get('word_count', 0),
                        'type': 'content'
                    })
            
            return sections
            
        except Exception:
            return []
    
    def _classify_content(self, processed_content: ProcessedContent) -> str:
        """Classify content type based on keywords and structure"""
        try:
            text_lower = processed_content.cleaned_text.lower()
            
            # Score each content type
            type_scores = {}
            for content_type, keywords in self.content_type_keywords.items():
                score = sum(1 for keyword in keywords if keyword in text_lower)
                if score > 0:
                    type_scores[content_type] = score
            
            # Return highest scoring type
            if type_scores:
                return max(type_scores, key=type_scores.get)
            else:
                return 'unknown'
                
        except Exception:
            return 'unknown'
    
    def _assess_quality(self, quality_score: float) -> str:
        """Assess content quality based on score"""
        if quality_score >= 85:
            return 'excellent'
        elif quality_score >= 70:
            return 'good'
        elif quality_score >= 50:
            return 'fair'
        else:
            return 'poor'
    
    def _generate_recommendations(self, processed_content: ProcessedContent, 
                                metrics: Dict[str, Any]) -> List[str]:
        """Generate improvement recommendations"""
        recommendations = []
        
        try:
            quality_score = metrics['quality_score']
            word_count = processed_content.word_count
            readability = processed_content.readability_score
            
            # Content length recommendations
            if word_count < 300:
                recommendations.append("Consider adding more content for better SEO performance")
            elif word_count > 5000:
                recommendations.append("Consider breaking content into smaller sections for better readability")
            
            # Readability recommendations
            if readability < 60:
                recommendations.append("Improve readability by using shorter sentences and simpler words")
            
            # Structure recommendations
            if len(processed_content.headings) < 3:
                recommendations.append("Add more headings to improve content structure")
            
            # Quality recommendations
            if quality_score < 70:
                recommendations.append("Enhance content quality by adding more relevant keywords and improving structure")
            
            return recommendations[:5]  # Max 5 recommendations
            
        except Exception:
            return ["Unable to generate specific recommendations"]

class ReportService:
    """Main report generation service"""
    
    def __init__(self):
        self.metrics_calculator = MetricsCalculator()
        self.insights_extractor = InsightsExtractor()
    
    async def generate_analysis_report(self, 
                                     processed_content: ProcessedContent,
                                     scraped_data: ScrapedContent,
                                     url: str,
                                     llm_analysis: Optional[Dict[str, Any]] = None) -> AnalysisReport:
        """Generate comprehensive analysis report"""
        
        try:
            logger.info(f"Generating analysis report for {url}")
            start_time = time.time()
            
            # Calculate metrics
            metrics = await self.metrics_calculator.calculate_all_metrics(
                processed_content, scraped_data
            )
            
            # Extract insights
            insights = await self.insights_extractor.extract_insights(
                processed_content, metrics
            )
            
            # Build content analysis, now with LLM data
            content_analysis = self._build_content_analysis(processed_content, insights, llm_analysis)
            
            # Build technical metadata
            technical_metadata = self._build_technical_metadata(scraped_data, url)
            
            # Prepare metadata for the final report, including the raw summary
            report_metadata = {
                'ai_summary': llm_analysis.get('summary') if llm_analysis else "LLM analysis not available."
            }

            # Generate final report
            report = AnalysisReport(
                url=url,
                title=scraped_data.title or 'No Title',
                description=scraped_data.description or '',
                
                # Content analysis
                content_analysis=content_analysis,
                
                # Metrics
                word_count=processed_content.word_count,
                character_count=len(processed_content.cleaned_text),
                paragraph_count=processed_content.paragraph_count,
                heading_count=len(processed_content.headings),
                link_count=len(processed_content.internal_links) + len(processed_content.external_links),
                image_count=len(processed_content.images),
                
                # Extracted data
                keywords=insights['keywords'],
                key_sections=insights['sections'],
                contact_information=processed_content.contact_information,
                
                # Technical data
                technical_metadata=technical_metadata,
                performance_metrics=metrics['performance'],
                
                # Processing information
                processing_status=ProcessingStatus.COMPLETED,
                processing_time=metrics.get('processing_time', time.time() - start_time),
                analysis_timestamp=datetime.now(),
                
                # Quality scores
                overall_quality_score=metrics.get('quality_score', 0.0),
                extraction_quality=processed_content.extraction_quality,
                processing_quality=processed_content.processing_quality,
                metadata=report_metadata
            )
            
            logger.info(f"Report generated successfully for {url}")
            return report
            
        except Exception as e:
            logger.error(f"Error generating report for {url}: {str(e)}")
            raise ProcessingException(f"Report generation failed: {str(e)}")
    
    def _build_content_analysis(self, 
                              processed_content: ProcessedContent, 
                              insights: Dict[str, Any],
                              llm_analysis: Optional[Dict[str, Any]] = None) -> ContentAnalysis:
        """Build content analysis object, incorporating LLM results if available."""
        
        llm_analysis = llm_analysis or {}
        sentiment_data = llm_analysis.get('sentiment') or {}
        seo_data = llm_analysis.get('seo') or {}
        readability_data = llm_analysis.get('readability') or {}

        # Map quality assessment to enum
        quality_mapping = {
            'excellent': QualityLevel.EXCELLENT,
            'good': QualityLevel.GOOD,
            'fair': QualityLevel.FAIR,
            'poor': QualityLevel.POOR
        }
        
        # Map content classification to enum
        content_type_mapping = {
            'article': ContentType.ARTICLE,
            'product_page': ContentType.PRODUCT_PAGE,
            'landing_page': ContentType.LANDING_PAGE,
            'documentation': ContentType.DOCUMENTATION,
            'forum_post': ContentType.FORUM_POST,
            'unknown': ContentType.UNKNOWN
        }
        
        return ContentAnalysis(
            content_type=content_type_mapping.get(insights['content_classification'], ContentType.UNKNOWN),
            quality_level=quality_mapping.get(insights['quality_assessment'], QualityLevel.FAIR),
            readability_score=readability_data.get('readability_score', processed_content.readability_score),
            sentiment_score=sentiment_data.get('sentiment_score', processed_content.sentiment_score),
            sentiment_label=sentiment_data.get('sentiment_label'),
            detected_tones=sentiment_data.get('detected_tones', []),
            topic_categories=processed_content.topics,
            key_themes=[kw['keyword'] for kw in insights['keywords'][:5]],
            content_density=len(processed_content.cleaned_text) / max(1, processed_content.word_count),
            uniqueness_score=85.0,  # Placeholder
            seo_score=seo_data.get('overall_score', 0.0),
            seo_recommendations=seo_data.get('recommendations', []),
            accessibility_score=readability_data.get('readability_score', 0.0), # Using readability as a proxy
            accessibility_notes=readability_data.get('accessibility_notes', [])
        )
    
    def _build_technical_metadata(self, scraped_data: ScrapedContent, url: str) -> TechnicalMetadata:
        """Build technical metadata object"""
        
        parsed_url = urlparse(url)
        metadata = scraped_data.meta_data
        
        return TechnicalMetadata(
            domain=parsed_url.netloc,
            subdomain=parsed_url.netloc.split('.')[0] if '.' in parsed_url.netloc else None,
            path=parsed_url.path,
            protocol=parsed_url.scheme,
            encoding=metadata.get('encoding', 'utf-8'),
            server=metadata.get('server'),
            cms=None,  # Would need CMS detection logic
            framework=None  # Would need framework detection logic
        )
