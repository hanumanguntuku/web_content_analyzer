"""
Content Type Detection Service - Advanced ML-Based Classification
Intelligent content classification using multiple detection strategies
"""
import re
import logging
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass
from collections import Counter

from ..models.data_models import ContentType, ProcessedContent

logger = logging.getLogger(__name__)

@dataclass
class DetectionResult:
    """Content type detection result with confidence"""
    content_type: ContentType
    confidence: float
    indicators: List[str]
    reasoning: str

class URLPatternDetector:
    """Detect content type based on URL patterns"""
    
    def __init__(self):
        self.url_patterns = {
            ContentType.PRODUCT_PAGE: [
                r'/product/',
                r'/item/',
                r'/shop/',
                r'/buy/',
                r'/p/',
                r'product-',
                r'item-',
                r'/store/'
            ],
            ContentType.ARTICLE: [
                r'/article/',
                r'/news/',
                r'/blog/',
                r'/post/',
                r'/story/',
                r'/read/',
                r'/articles/',
                r'-article-'
            ],
            ContentType.DOCUMENTATION: [
                r'/docs/',
                r'/documentation/',
                r'/guide/',
                r'/manual/',
                r'/help/',
                r'/tutorial/',
                r'/api/',
                r'/reference/'
            ],
            ContentType.FORUM_POST: [
                r'/forum/',
                r'/discussion/',
                r'/thread/',
                r'/topic/',
                r'/community/',
                r'/post/',
                r'/reply/'
            ],
            ContentType.LANDING_PAGE: [
                r'/$',
                r'/home',
                r'/index',
                r'/landing',
                r'/signup',
                r'/register',
                r'/join'
            ]
        }
    
    def detect(self, url: str) -> Optional[DetectionResult]:
        """Detect content type from URL patterns"""
        try:
            url_lower = url.lower()
            scores = {}
            
            for content_type, patterns in self.url_patterns.items():
                matches = []
                for pattern in patterns:
                    if re.search(pattern, url_lower):
                        matches.append(pattern)
                
                if matches:
                    # Calculate confidence based on pattern specificity
                    confidence = min(0.8, len(matches) * 0.3 + 0.2)
                    scores[content_type] = (confidence, matches)
            
            if scores:
                best_type = max(scores.keys(), key=lambda k: scores[k][0])
                confidence, indicators = scores[best_type]
                
                return DetectionResult(
                    content_type=best_type,
                    confidence=confidence,
                    indicators=indicators,
                    reasoning=f"URL contains patterns: {', '.join(indicators)}"
                )
            
            return None
            
        except Exception as e:
            logger.error(f"URL pattern detection error: {str(e)}")
            return None

class ContentStructureDetector:
    """Detect content type based on HTML structure and elements"""
    
    def __init__(self):
        self.structure_indicators = {
            ContentType.PRODUCT_PAGE: {
                'elements': ['price', 'cart', 'buy', 'purchase', 'product'],
                'selectors': ['.price', '.cart', '.buy-btn', '.product-', '#add-to-cart'],
                'required_count': 2
            },
            ContentType.ARTICLE: {
                'elements': ['article', 'content', 'post', 'story'],
                'selectors': ['article', '.article', '.post', '.content', '.story'],
                'required_count': 1
            },
            ContentType.DOCUMENTATION: {
                'elements': ['docs', 'documentation', 'guide', 'manual', 'api'],
                'selectors': ['.docs', '.documentation', '.guide', '.manual', '.toc'],
                'required_count': 1
            },
            ContentType.FORUM_POST: {
                'elements': ['thread', 'reply', 'comment', 'discussion', 'forum'],
                'selectors': ['.thread', '.reply', '.comment', '.discussion', '.forum'],
                'required_count': 1
            },
            ContentType.LANDING_PAGE: {
                'elements': ['hero', 'banner', 'cta', 'signup', 'register'],
                'selectors': ['.hero', '.banner', '.cta', '.signup', '.register'],
                'required_count': 1
            }
        }
    
    def detect(self, processed_content: ProcessedContent) -> Optional[DetectionResult]:
        """Detect content type from structure analysis"""
        try:
            # Combine all text for analysis
            full_text = processed_content.cleaned_text.lower()
            
            # Also check headings for structure clues
            heading_text = ' '.join([h.get('text', '').lower() 
                                   for h in processed_content.headings])
            
            scores = {}
            
            for content_type, indicators in self.structure_indicators.items():
                matches = []
                
                # Check for element keywords in text
                for element in indicators['elements']:
                    count = full_text.count(element) + heading_text.count(element)
                    if count > 0:
                        matches.append(f"{element}({count})")
                
                # Calculate confidence
                if len(matches) >= indicators['required_count']:
                    confidence = min(0.9, len(matches) * 0.2 + 0.3)
                    scores[content_type] = (confidence, matches)
            
            if scores:
                best_type = max(scores.keys(), key=lambda k: scores[k][0])
                confidence, indicators = scores[best_type]
                
                return DetectionResult(
                    content_type=best_type,
                    confidence=confidence,
                    indicators=indicators,
                    reasoning=f"Structure contains: {', '.join(indicators)}"
                )
            
            return None
            
        except Exception as e:
            logger.error(f"Structure detection error: {str(e)}")
            return None

class KeywordAnalysisDetector:
    """Detect content type based on keyword analysis"""
    
    def __init__(self):
        self.keyword_weights = {
            ContentType.PRODUCT_PAGE: {
                'high': ['price', 'buy', 'purchase', 'cart', 'order', 'shipping', 'reviews'],
                'medium': ['product', 'item', 'sale', 'discount', 'delivery', 'warranty'],
                'low': ['shop', 'store', 'brand', 'model', 'features']
            },
            ContentType.ARTICLE: {
                'high': ['article', 'story', 'news', 'published', 'author', 'read more'],
                'medium': ['content', 'post', 'blog', 'opinion', 'analysis', 'report'],
                'low': ['information', 'details', 'facts', 'research', 'study']
            },
            ContentType.DOCUMENTATION: {
                'high': ['documentation', 'guide', 'tutorial', 'manual', 'api', 'reference'],
                'medium': ['instructions', 'steps', 'example', 'usage', 'syntax'],
                'low': ['help', 'support', 'faq', 'troubleshooting']
            },
            ContentType.FORUM_POST: {
                'high': ['forum', 'discussion', 'reply', 'comment', 'thread', 'post'],
                'medium': ['community', 'topic', 'question', 'answer', 'member'],
                'low': ['user', 'joined', 'profile', 'activity']
            },
            ContentType.LANDING_PAGE: {
                'high': ['sign up', 'register', 'join', 'get started', 'free trial'],
                'medium': ['benefits', 'features', 'pricing', 'testimonials'],
                'low': ['welcome', 'about', 'company', 'service']
            }
        }
    
    def detect(self, processed_content: ProcessedContent) -> Optional[DetectionResult]:
        """Detect content type from keyword analysis"""
        try:
            full_text = processed_content.cleaned_text.lower()
            keyword_data = processed_content.keywords or []
            
            # Extract keywords from processed content
            content_keywords = [kw.get('keyword', '').lower() for kw in keyword_data]
            
            scores = {}
            
            for content_type, weight_categories in self.keyword_weights.items():
                score = 0
                matches = []
                
                # Check high-weight keywords
                for keyword in weight_categories['high']:
                    if keyword in full_text or keyword in content_keywords:
                        score += 3
                        matches.append(f"{keyword}(high)")
                
                # Check medium-weight keywords
                for keyword in weight_categories['medium']:
                    if keyword in full_text or keyword in content_keywords:
                        score += 2
                        matches.append(f"{keyword}(med)")
                
                # Check low-weight keywords
                for keyword in weight_categories['low']:
                    if keyword in full_text or keyword in content_keywords:
                        score += 1
                        matches.append(f"{keyword}(low)")
                
                if score > 0:
                    # Normalize confidence to 0-1 range
                    confidence = min(0.95, score * 0.1)
                    scores[content_type] = (confidence, matches[:5])  # Top 5 matches
            
            if scores:
                best_type = max(scores.keys(), key=lambda k: scores[k][0])
                confidence, indicators = scores[best_type]
                
                return DetectionResult(
                    content_type=best_type,
                    confidence=confidence,
                    indicators=indicators,
                    reasoning=f"Keyword analysis: {', '.join(indicators)}"
                )
            
            return None
            
        except Exception as e:
            logger.error(f"Keyword analysis detection error: {str(e)}")
            return None

class ContentLengthDetector:
    """Detect content type based on content length and structure patterns"""
    
    def __init__(self):
        self.length_patterns = {
            ContentType.ARTICLE: {'min_words': 300, 'typical_range': (500, 3000)},
            ContentType.PRODUCT_PAGE: {'min_words': 50, 'typical_range': (100, 800)},
            ContentType.DOCUMENTATION: {'min_words': 200, 'typical_range': (400, 5000)},
            ContentType.FORUM_POST: {'min_words': 10, 'typical_range': (20, 500)},
            ContentType.LANDING_PAGE: {'min_words': 100, 'typical_range': (200, 1000)}
        }
    
    def detect(self, processed_content: ProcessedContent) -> Optional[DetectionResult]:
        """Detect content type from length and structure patterns"""
        try:
            word_count = processed_content.word_count
            paragraph_count = processed_content.paragraph_count
            heading_count = len(processed_content.headings)
            
            scores = {}
            
            for content_type, patterns in self.length_patterns.items():
                if word_count >= patterns['min_words']:
                    min_range, max_range = patterns['typical_range']
                    
                    # Calculate length score
                    if min_range <= word_count <= max_range:
                        length_score = 1.0
                    elif word_count < min_range:
                        length_score = word_count / min_range
                    else:
                        length_score = max(0.2, max_range / word_count)
                    
                    # Structure bonus
                    structure_bonus = 0
                    if content_type == ContentType.ARTICLE and heading_count >= 3:
                        structure_bonus = 0.2
                    elif content_type == ContentType.DOCUMENTATION and heading_count >= 5:
                        structure_bonus = 0.3
                    elif content_type == ContentType.PRODUCT_PAGE and paragraph_count <= 10:
                        structure_bonus = 0.2
                    
                    confidence = min(0.7, length_score * 0.5 + structure_bonus)
                    
                    if confidence > 0.1:
                        scores[content_type] = (
                            confidence,
                            [f"words:{word_count}", f"paragraphs:{paragraph_count}", 
                             f"headings:{heading_count}"]
                        )
            
            if scores:
                best_type = max(scores.keys(), key=lambda k: scores[k][0])
                confidence, indicators = scores[best_type]
                
                return DetectionResult(
                    content_type=best_type,
                    confidence=confidence,
                    indicators=indicators,
                    reasoning=f"Content length analysis: {', '.join(indicators)}"
                )
            
            return None
            
        except Exception as e:
            logger.error(f"Content length detection error: {str(e)}")
            return None

class ContentTypeDetectionService:
    """
    ContentTypeDetectionService detects the type of web content using an ensemble of strategies (URL patterns, structure, keywords, length).
    """
    
    def __init__(self):
        self.url_detector = URLPatternDetector()
        self.structure_detector = ContentStructureDetector()
        self.keyword_detector = KeywordAnalysisDetector()
        self.length_detector = ContentLengthDetector()
    
    async def detect_content_type(self, 
                                processed_content: ProcessedContent,
                                url: str) -> Tuple[ContentType, float, Dict[str, Any]]:
        """
        Detect the content type of processed content using multiple strategies.
        Args:
            processed_content (ProcessedContent): The processed content object.
            url (str): The source URL.
        Returns:
            Tuple[ContentType, float, Dict[str, Any]]: (content_type, confidence, detection_details)
        """
        try:
            logger.info(f"Detecting content type for {url}")
            
            # Run all detectors
            results = []
            
            # URL pattern detection
            url_result = self.url_detector.detect(url)
            if url_result:
                results.append(('url_pattern', url_result))
            
            # Structure detection
            structure_result = self.structure_detector.detect(processed_content)
            if structure_result:
                results.append(('structure', structure_result))
            
            # Keyword analysis
            keyword_result = self.keyword_detector.detect(processed_content)
            if keyword_result:
                results.append(('keyword', keyword_result))
            
            # Length analysis
            length_result = self.length_detector.detect(processed_content)
            if length_result:
                results.append(('length', length_result))
            
            # Combine results using weighted voting
            if results:
                final_type, final_confidence, details = self._combine_results(results)
            else:
                # Default classification
                final_type = ContentType.UNKNOWN
                final_confidence = 0.1
                details = {'reasoning': 'No strong indicators found', 'methods': []}
            
            logger.info(f"Detected content type: {final_type.value} (confidence: {final_confidence:.2f})")
            
            return final_type, final_confidence, details
            
        except Exception as e:
            logger.error(f"Content type detection error: {str(e)}")
            return ContentType.UNKNOWN, 0.0, {'error': str(e)}
    
    def _combine_results(self, results: List[Tuple[str, DetectionResult]]) -> Tuple[ContentType, float, Dict[str, Any]]:
        """Combine detection results using weighted ensemble"""
        try:
            # Weights for different detection methods
            method_weights = {
                'url_pattern': 0.3,
                'structure': 0.25,
                'keyword': 0.3,
                'length': 0.15
            }
            
            # Collect votes for each content type
            votes = {}
            method_details = {}
            
            for method, result in results:
                weight = method_weights.get(method, 0.1)
                weighted_confidence = result.confidence * weight
                
                if result.content_type not in votes:
                    votes[result.content_type] = 0
                
                votes[result.content_type] += weighted_confidence
                
                method_details[method] = {
                    'content_type': result.content_type.value,
                    'confidence': result.confidence,
                    'indicators': result.indicators,
                    'reasoning': result.reasoning
                }
            
            # Find best classification
            if votes:
                best_type = max(votes.keys(), key=votes.get)
                
                # Calculate final confidence
                total_weight = sum(method_weights[method] for method, _ in results)
                normalized_confidence = min(1.0, votes[best_type] / total_weight)
                
                # Apply consistency bonus
                type_count = sum(1 for _, result in results if result.content_type == best_type)
                consistency_bonus = min(0.2, (type_count - 1) * 0.1)
                final_confidence = min(1.0, normalized_confidence + consistency_bonus)
                
                details = {
                    'reasoning': f'Ensemble classification with {type_count}/{len(results)} methods agreeing',
                    'methods': method_details,
                    'votes': {t.value: v for t, v in votes.items()},
                    'consistency': consistency_bonus
                }
                
                return best_type, final_confidence, details
            
            # Fallback
            return ContentType.UNKNOWN, 0.0, {'reasoning': 'No valid classifications'}
            
        except Exception as e:
            logger.error(f"Result combination error: {str(e)}")
            return ContentType.UNKNOWN, 0.0, {'error': str(e)}
    
    def get_content_type_info(self, content_type: ContentType) -> Dict[str, Any]:
        """Get detailed information about a content type"""
        
        type_info = {
            ContentType.ARTICLE: {
                'description': 'News articles, blog posts, and editorial content',
                'typical_features': ['Author byline', 'Publication date', 'Multiple paragraphs', 'Headlines'],
                'optimal_length': '500-3000 words',
                'seo_tips': ['Use proper heading structure', 'Include relevant keywords', 'Add meta description']
            },
            ContentType.PRODUCT_PAGE: {
                'description': 'E-commerce product listings and details',
                'typical_features': ['Product images', 'Price information', 'Buy buttons', 'Reviews'],
                'optimal_length': '100-800 words',
                'seo_tips': ['Include product specifications', 'Add customer reviews', 'Use structured data']
            },
            ContentType.DOCUMENTATION: {
                'description': 'Technical documentation and guides',
                'typical_features': ['Table of contents', 'Code examples', 'Step-by-step instructions'],
                'optimal_length': '400-5000 words',
                'seo_tips': ['Use clear headings', 'Include search functionality', 'Cross-reference related topics']
            },
            ContentType.FORUM_POST: {
                'description': 'Community discussions and forum threads',
                'typical_features': ['User profiles', 'Reply chains', 'Voting systems', 'Timestamps'],
                'optimal_length': '20-500 words',
                'seo_tips': ['Encourage user engagement', 'Moderate content quality', 'Use relevant tags']
            },
            ContentType.LANDING_PAGE: {
                'description': 'Marketing pages designed for conversions',
                'typical_features': ['Hero sections', 'Call-to-action buttons', 'Testimonials', 'Forms'],
                'optimal_length': '200-1000 words',
                'seo_tips': ['Focus on single goal', 'Optimize for conversions', 'A/B test elements']
            },
            ContentType.UNKNOWN: {
                'description': 'Content type could not be determined',
                'typical_features': ['Mixed or unclear content structure'],
                'optimal_length': 'Varies',
                'seo_tips': ['Analyze content manually', 'Improve content structure', 'Add clear indicators']
            }
        }
        
        return type_info.get(content_type, type_info[ContentType.UNKNOWN])
