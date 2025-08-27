"""
Text Processing Pipeline - M1-DATA-03 Implementation
Deep text cleaning, keyword extraction, and content analysis
"""
import re
import logging
from typing import List, Dict, Any, Optional, Set
from collections import Counter
import unicodedata
from urllib.parse import urlparse
from .keyphrase_extractor import SimpleKeyPhraseExtractor
from .outline_generator import DocumentOutlineGenerator

logger = logging.getLogger(__name__)

class TextProcessor:
    """
    Advanced text processing and content analysis.
    Provides methods for deep cleaning, keyword extraction, entity recognition, and content analysis.
    """
    
    def __init__(self):
        """Initialize text processor with patterns and stopwords"""
        # Common English stopwords
        self.stopwords = {
            'a', 'an', 'and', 'are', 'as', 'at', 'be', 'by', 'for', 'from',
            'has', 'he', 'in', 'is', 'it', 'its', 'of', 'on', 'that', 'the',
            'to', 'was', 'will', 'with', 'this', 'they', 'them', 'their',
            'have', 'had', 'but', 'or', 'we', 'you', 'your', 'all', 'can',
            'do', 'if', 'no', 'not', 'so', 'up', 'out', 'get', 'go', 'how',
            'now', 'may', 'new', 'use', 'way', 'who', 'see', 'her', 'him',
            'his', 'our', 'she', 'two', 'more', 'than', 'been', 'into',
            'only', 'over', 'also', 'back', 'after', 'first', 'well', 'any',
            'just', 'where', 'most', 'some', 'would', 'there', 'what', 'when'
        }
        
        # Content chunking configuration for LLM context management
        self.max_chunk_size = 4000  # Characters per chunk (safe for most LLMs)
        self.chunk_overlap = 200    # Overlap between chunks for context preservation
        
        # Email patterns
        self.email_patterns = [
            r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',
            r'\b[A-Za-z0-9._%+-]+\s*\[at\]\s*[A-Za-z0-9.-]+\s*\[dot\]\s*[A-Za-z]{2,}\b'
        ]
        
        # Phone patterns
        self.phone_patterns = [
            r'\+?1?\s*\(?(\d{3})\)?[-.\s]*(\d{3})[-.\s]*(\d{4})',  # US format
            r'\+?(\d{1,3})\s*[-.\s]*\(?(\d{1,4})\)?[-.\s]*(\d{3,4})[-.\s]*(\d{3,4})',  # International
            r'\b\d{3}[-.\s]?\d{3}[-.\s]?\d{4}\b',  # Simple US format
            r'\(\d{3}\)\s*\d{3}-\d{4}',  # (123) 456-7890
        ]
        
        # Social media patterns
        self.social_patterns = {
            'twitter': r'@[A-Za-z0-9_]+',
            'hashtag': r'#[A-Za-z0-9_]+',
            'url': r'https?://[^\s]+',
            'mention': r'@[A-Za-z0-9._-]+',
        }
        
        # Readability constants
        self.flesch_kincaid_constants = {
            'sentence_weight': 1.015,
            'syllable_weight': 84.6,
            'base_score': 206.835
        }
        
        # Initialize keyphrase extractor
        self.keyphrase_extractor = SimpleKeyPhraseExtractor()
        self.outline_generator = DocumentOutlineGenerator()
        
        logger.info("TextProcessor initialized with advanced cleaning and analysis capabilities")
    
    def process_content(self, content: str, url: Optional[str] = None, html: Optional[str] = None) -> Dict[str, Any]:
        """
        Process raw content and return structured analysis results.
        Args:
            content (str): Raw text content.
            url (Optional[str]): Source URL.
            html (Optional[str]): Raw HTML content.
        Returns:
            Dict[str, Any]: Structured analysis results.
        """
        """Comprehensive content processing pipeline"""
        import time
        start_time = time.time()
        try:
            logger.info(f"Starting text processing for content length: {len(content)}")
            # Deep text cleaning
            cleaned_text = self.deep_clean_text(content)
            # Extract keywords
            keywords = self.extract_keywords(cleaned_text)
            # Extract key phrases
            key_phrases = self.keyphrase_extractor.extract(cleaned_text)
            # Extract contact information
            emails = self.extract_emails(content)  # Use original content for better detection
            phones = self.extract_phones(content)
            # Detect language
            language = self.detect_language(cleaned_text)
            # Calculate readability scores
            readability = self.calculate_readability_scores(cleaned_text)
            # Extract entities and patterns
            entities = self.extract_entities(cleaned_text)
            # Content analysis
            analysis = self.analyze_content_structure(cleaned_text)
            # Generate document outline
            outline = self.outline_generator.generate_outline(html or content)
            processing_time = time.time() - start_time
            processing_quality = self._calculate_processing_quality(cleaned_text, keywords, entities)
            # Calculate a main readability score (Flesch-Kincaid or fallback)
            readability_score = 0.0
            if isinstance(readability, dict):
                readability_score = readability.get('flesch_kincaid', 0.0)
            # Extraction quality: ratio of cleaned text to original content length (simple heuristic)
            extraction_quality = 0.0
            if cleaned_text and content:
                extraction_quality = min(100.0, (len(cleaned_text) / max(1, len(content))) * 100)

            result = {
                'cleaned_text': cleaned_text,
                'keywords': keywords,
                'key_phrases': key_phrases,
                'outline': outline,
                'emails': emails,
                'phones': phones,
                'language': language,
                'readability': readability,
                'readability_score': readability_score,
                'extraction_quality': extraction_quality,
                'entities': entities,
                'analysis': analysis,
                'processing_quality': processing_quality,
                'status': 'COMPLETED',
                'summary': analysis.get('summary', '') if isinstance(analysis, dict) else '',
                'processing_time': processing_time,
                'performance_score': processing_quality,
            }
            logger.info(f"Text processing complete. Extracted {len(keywords)} keywords, "
                       f"{len(emails)} emails, {len(phones)} phones")
            # If using ProcessedContent model, ensure these fields are set
            if hasattr(self, 'as_model') and self.as_model:
                from ..models.data_models import ProcessedContent
                return ProcessedContent(
                    url=url if 'url' in locals() else '',
                    cleaned_text=cleaned_text,
                    keywords=keywords,
                    emails=emails,
                    phones=phones,
                    language=language,
                    readability=readability,
                    analysis=analysis,
                    processing_quality=processing_quality,
                    word_count=len(cleaned_text.split()),
                    character_count=len(cleaned_text),
                    paragraph_count=cleaned_text.count('\n\n'),
                    sentence_count=cleaned_text.count('.') + cleaned_text.count('!') + cleaned_text.count('?'),
                    readability_score=readability_score,
                    extraction_quality=extraction_quality,
                    headings=[],
                    sections=[],
                    sentiment_score=0.0,
                    topics=[]
                )
            return result
        except Exception as e:
            logger.error(f"Text processing failed: {str(e)}")
            return {
                'status': 'FAILED',
                'summary': f'Processing failed: {str(e)}',
                'processing_time': 0,
                'performance_score': 0,
            }
    
    def deep_clean_text(self, text: str) -> str:
        """
        Perform deep cleaning on input text, removing noise and normalizing whitespace.
        Args:
            text (str): Input text.
        Returns:
            str: Cleaned text.
        """
        """Comprehensive text cleaning and normalization, including HTML tag removal"""
        if not text:
            return ""

        logger.debug("Starting deep text cleaning")

        # Remove HTML tags using BeautifulSoup if available, else fallback to regex
        try:
            from bs4 import BeautifulSoup
            text = BeautifulSoup(text, "lxml").get_text(separator=" ")
        except Exception:
            # Fallback: remove tags with regex (less robust)
            text = re.sub(r'<[^>]+>', ' ', text)

        # Unicode normalization
        text = unicodedata.normalize('NFKD', text)

        # Remove HTML entities that might have been missed
        text = re.sub(r'&[a-zA-Z0-9#]+;', ' ', text)

        # Remove URLs (but keep them for separate extraction)
        text = re.sub(r'https?://[^\s]+', ' [URL] ', text)

        # Remove email addresses (but keep them for separate extraction)
        for pattern in self.email_patterns:
            text = re.sub(pattern, ' [EMAIL] ', text, flags=re.IGNORECASE)

        # Remove phone numbers (but keep them for separate extraction)
        for pattern in self.phone_patterns:
            text = re.sub(pattern, ' [PHONE] ', text)

        # Remove social media handles and hashtags
        text = re.sub(r'@[A-Za-z0-9_]+', ' [MENTION] ', text)
        text = re.sub(r'#[A-Za-z0-9_]+', ' [HASHTAG] ', text)

        # Remove special characters but preserve sentence structure
        text = re.sub(r'[^\w\s\.\!\?\,\;\:\-\(\)]', ' ', text)

        # Clean up punctuation spacing
        text = re.sub(r'\s+([\.\!\?])', r'\1', text)  # Remove space before punctuation
        text = re.sub(r'([\.\!\?])\s*', r'\1 ', text)  # Ensure space after punctuation

        # Remove repeated punctuation
        text = re.sub(r'([\.\!\?]){2,}', r'\1', text)

        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text)

        # Remove leading/trailing whitespace
        text = text.strip()

        # Remove very short "words" that are likely noise
        words = text.split()
        cleaned_words = [word for word in words if len(word) > 1 or word.lower() in ['a', 'i']]
        text = ' '.join(cleaned_words)

        logger.debug(f"Deep cleaning complete. Original: {len(text)} chars")
        return text
    
    def extract_keywords(self, text: str, max_keywords: int = 20) -> List[Dict[str, Any]]:
        """
        Extract keywords from text using frequency and context analysis.
        Args:
            text (str): Input text.
            max_keywords (int): Maximum number of keywords to extract.
        Returns:
            List[Dict[str, Any]]: List of extracted keywords with metadata.
        """
        """Extract keywords using frequency analysis and filtering"""
        if not text:
            return []
        logger.debug("Extracting keywords from text")
        # Convert to lowercase and split into words
        words = re.findall(r'\b[a-zA-Z]{3,}\b', text.lower())
        # Filter out stopwords
        filtered_words = [word for word in words if word not in self.stopwords]
        # Count word frequencies
        word_freq = Counter(filtered_words)
        # Extract n-grams (2-word and 3-word phrases)
        bigrams = self._extract_ngrams(text, 2)
        trigrams = self._extract_ngrams(text, 3)
        # Combine single words and n-grams
        all_terms = {}
        # Add single words
        for word, freq in word_freq.most_common():
            if len(word) >= 3:  # Minimum word length
                all_terms[word] = {
                    'keyword': word,
                    'frequency': freq,
                    'type': 'word',
                    'score': freq * len(word)  # Basic scoring
                }
        # Add bigrams
        for bigram, freq in bigrams.most_common(10):
            if freq >= 2:  # Minimum frequency for phrases
                all_terms[bigram] = {
                    'keyword': bigram,
                    'frequency': freq,
                    'type': 'bigram',
                    'score': freq * 2  # Bonus for phrases
                }
        # Add trigrams
        for trigram, freq in trigrams.most_common(5):
            if freq >= 2:
                all_terms[trigram] = {
                    'keyword': trigram,
                    'frequency': freq,
                    'type': 'trigram',
                    'score': freq * 3  # Higher bonus for longer phrases
                }
        # Sort by score and return top keywords
        keywords = sorted(all_terms.values(), key=lambda x: x['score'], reverse=True)
        # Filter out empty or whitespace-only terms
        filtered_keywords = [k for k in keywords if k.get('keyword', '').strip()]
        result = filtered_keywords[:max_keywords]
        logger.debug(f"Extracted {len(result)} keywords (after filtering empty terms)")
        return result
    
    def _extract_ngrams(self, text: str, n: int) -> Counter:
        """Extract n-grams from text"""
        words = re.findall(r'\b[a-zA-Z]{3,}\b', text.lower())
        filtered_words = [word for word in words if word not in self.stopwords]
        
        ngrams = []
        for i in range(len(filtered_words) - n + 1):
            ngram = ' '.join(filtered_words[i:i + n])
            ngrams.append(ngram)
        
        return Counter(ngrams)
    
    def extract_emails(self, text: str) -> List[str]:
        """
        Extract email addresses from text.
        Args:
            text (str): Input text.
        Returns:
            List[str]: List of email addresses found.
        """
        """Extract email addresses from text"""
        emails = set()
        
        for pattern in self.email_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            emails.update(matches)
        
        # Clean and validate emails
        valid_emails = []
        for email in emails:
            # Clean up
            email = email.strip().lower()
            # Basic validation
            if '@' in email and '.' in email.split('@')[1]:
                valid_emails.append(email)
        
        logger.debug(f"Extracted {len(valid_emails)} email addresses")
        return list(set(valid_emails))  # Remove duplicates
    
    def extract_phones(self, text: str) -> List[str]:
        """
        Extract phone numbers from text.
        Args:
            text (str): Input text.
        Returns:
            List[str]: List of phone numbers found.
        """
        """Extract phone numbers from text"""
        phones = set()
        
        for pattern in self.phone_patterns:
            matches = re.findall(pattern, text)
            if isinstance(matches[0], tuple) if matches else False:
                # Handle tuple matches from grouped patterns
                for match in matches:
                    phone = ''.join(match)
                    phones.add(phone)
            else:
                phones.update(matches)
        
        # Clean and format phone numbers
        formatted_phones = []
        for phone in phones:
            # Remove non-digit characters
            digits = re.sub(r'\D', '', phone)
            
            # Validate length
            if 10 <= len(digits) <= 15:
                formatted_phones.append(digits)
        
        logger.debug(f"Extracted {len(formatted_phones)} phone numbers")
        return list(set(formatted_phones))  # Remove duplicates
    
    def detect_language(self, text: str) -> Optional[str]:
        """
        Detect the language of the input text.
        Args:
            text (str): Input text.
        Returns:
            Optional[str]: Detected language code or None.
        """
        """Simple language detection based on common words"""
        if not text:
            return None
        
        # Sample text for analysis
        sample = text[:1000].lower()
        
        # Language indicators
        language_indicators = {
            'en': ['the', 'and', 'is', 'in', 'to', 'of', 'a', 'that', 'it', 'with'],
            'es': ['el', 'la', 'de', 'que', 'y', 'en', 'un', 'es', 'se', 'no'],
            'fr': ['le', 'de', 'et', 'à', 'un', 'il', 'être', 'et', 'en', 'avoir'],
            'de': ['der', 'die', 'und', 'in', 'den', 'von', 'zu', 'das', 'mit', 'sich'],
            'it': ['il', 'di', 'che', 'e', 'la', 'per', 'in', 'un', 'del', 'con'],
        }
        
        scores = {}
        for lang, indicators in language_indicators.items():
            score = sum(1 for word in indicators if word in sample)
            scores[lang] = score
        
        # Return language with highest score if above threshold
        best_lang = max(scores, key=scores.get)
        if scores[best_lang] >= 3:  # Minimum confidence threshold
            logger.debug(f"Detected language: {best_lang} (score: {scores[best_lang]})")
            return best_lang
        
        return 'unknown'
    
    def calculate_readability_scores(self, text: str) -> Dict[str, float]:
        """
        Calculate readability scores for the input text.
        Args:
            text (str): Input text.
        Returns:
            Dict[str, float]: Readability metrics.
        """
        """Calculate various readability scores"""
        if not text:
            return {'flesch_kincaid': 0, 'avg_sentence_length': 0, 'avg_word_length': 0}
        
        # Count sentences
        sentences = re.split(r'[.!?]+', text)
        sentence_count = len([s for s in sentences if s.strip()])
        
        # Count words
        words = re.findall(r'\b\w+\b', text)
        word_count = len(words)
        
        # Count syllables (approximation)
        syllable_count = self._count_syllables_approximate(text)
        
        if sentence_count == 0 or word_count == 0:
            return {'flesch_kincaid': 0, 'avg_sentence_length': 0, 'avg_word_length': 0}
        
        # Flesch-Kincaid Grade Level
        avg_sentence_length = word_count / sentence_count
        avg_syllables_per_word = syllable_count / word_count
        
        flesch_kincaid = (
            self.flesch_kincaid_constants['sentence_weight'] * avg_sentence_length +
            self.flesch_kincaid_constants['syllable_weight'] * avg_syllables_per_word -
            15.59
        )
        
        # Average word length
        total_chars = sum(len(word) for word in words)
        avg_word_length = total_chars / word_count if word_count > 0 else 0
        
        result = {
            'flesch_kincaid': round(flesch_kincaid, 2),
            'avg_sentence_length': round(avg_sentence_length, 2),
            'avg_word_length': round(avg_word_length, 2),
            'word_count': word_count,
            'sentence_count': sentence_count
        }
        
        logger.debug(f"Calculated readability scores: FK={result['flesch_kincaid']}")
        return result
    
    def _count_syllables_approximate(self, text: str) -> int:
        """Approximate syllable counting"""
        words = re.findall(r'\b[a-zA-Z]+\b', text.lower())
        total_syllables = 0
        
        for word in words:
            # Count vowel groups
            vowel_groups = re.findall(r'[aeiouy]+', word)
            syllables = len(vowel_groups)
            
            # Adjust for silent 'e'
            if word.endswith('e') and syllables > 1:
                syllables -= 1
            
            # Minimum one syllable per word
            syllables = max(1, syllables)
            total_syllables += syllables
        
        return total_syllables
    
    def extract_entities(self, text: str) -> Dict[str, List[str]]:
        """Extract named entities and patterns"""
        entities = {
            'urls': [],
            'mentions': [],
            'hashtags': [],
            'capitalized_terms': [],
            'numbers': [],
            'dates': []
        }
        
        # URLs
        entities['urls'] = re.findall(r'https?://[^\s]+', text)
        
        # Social media mentions and hashtags
        entities['mentions'] = re.findall(r'@[A-Za-z0-9_]+', text)
        entities['hashtags'] = re.findall(r'#[A-Za-z0-9_]+', text)
        
        # Capitalized terms (potential proper nouns)
        entities['capitalized_terms'] = re.findall(r'\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\b', text)
        
        # Numbers
        entities['numbers'] = re.findall(r'\b\d+(?:,\d{3})*(?:\.\d+)?\b', text)
        
        # Simple date patterns
        date_patterns = [
            r'\b\d{1,2}/\d{1,2}/\d{2,4}\b',  # MM/DD/YYYY
            r'\b\d{1,2}-\d{1,2}-\d{2,4}\b',  # MM-DD-YYYY
            r'\b[A-Za-z]{3,9}\s+\d{1,2},?\s+\d{2,4}\b',  # Month DD, YYYY
        ]
        
        for pattern in date_patterns:
            entities['dates'].extend(re.findall(pattern, text))
        
        # Remove duplicates and limit results
        for key in entities:
            entities[key] = list(set(entities[key]))[:10]  # Limit to 10 per type
        
        logger.debug(f"Extracted entities: {sum(len(v) for v in entities.values())} total")
        return entities
    
    def analyze_content_structure(self, text: str) -> Dict[str, Any]:
        """Analyze content structure and characteristics"""
        if not text:
            return {}
        
        # Paragraph analysis
        paragraphs = [p.strip() for p in text.split('\n') if p.strip()]
        paragraph_lengths = [len(p.split()) for p in paragraphs]
        
        # Sentence analysis
        sentences = re.split(r'[.!?]+', text)
        sentences = [s.strip() for s in sentences if s.strip()]
        sentence_lengths = [len(s.split()) for s in sentences]
        
        # Content characteristics
        analysis = {
            'paragraph_count': len(paragraphs),
            'avg_paragraph_length': sum(paragraph_lengths) / len(paragraph_lengths) if paragraph_lengths else 0,
            'sentence_count': len(sentences),
            'avg_sentence_length': sum(sentence_lengths) / len(sentence_lengths) if sentence_lengths else 0,
            'longest_sentence': max(sentence_lengths) if sentence_lengths else 0,
            'shortest_sentence': min(sentence_lengths) if sentence_lengths else 0,
            'content_density': self._calculate_content_density(text),
            'complexity_score': self._calculate_complexity_score(text)
        }
        
        return analysis
    
    def _calculate_content_density(self, text: str) -> float:
        """Calculate content density (meaningful words per total words)"""
        if not text:
            return 0.0
        
        words = re.findall(r'\b[a-zA-Z]+\b', text.lower())
        meaningful_words = [w for w in words if w not in self.stopwords and len(w) > 2]
        
        if not words:
            return 0.0
        
        return len(meaningful_words) / len(words)
    
    def _calculate_complexity_score(self, text: str) -> float:
        """Calculate text complexity score"""
        if not text:
            return 0.0
        
        words = re.findall(r'\b[a-zA-Z]+\b', text)
        if not words:
            return 0.0
        
        # Factors contributing to complexity
        long_words = sum(1 for word in words if len(word) > 6)
        complex_punctuation = len(re.findall(r'[;:,\-\(\)]', text))
        
        complexity = (long_words / len(words)) * 50 + (complex_punctuation / len(text)) * 100
        
        return min(complexity, 100.0)  # Cap at 100
    
    def _calculate_processing_quality(self, text: str, keywords: List[Dict], entities: Dict) -> float:
        """Calculate overall processing quality score"""
        score = 0.0
        
        # Text quality (0-40 points)
        if text:
            word_count = len(text.split())
            if word_count >= 100:
                score += 40
            elif word_count >= 50:
                score += 25
            elif word_count >= 20:
                score += 15
        
        # Keyword extraction quality (0-30 points)
        if keywords:
            high_quality_keywords = sum(1 for kw in keywords if kw['frequency'] >= 2)
            if high_quality_keywords >= 5:
                score += 30
            elif high_quality_keywords >= 3:
                score += 20
            elif high_quality_keywords >= 1:
                score += 10
        
        # Entity extraction quality (0-30 points)
        total_entities = sum(len(entity_list) for entity_list in entities.values())
        if total_entities >= 5:
            score += 30
        elif total_entities >= 3:
            score += 20
        elif total_entities >= 1:
            score += 10
        
        return min(score, 100.0)
    
    def chunk_content_for_llm(self, text: str) -> List[Dict[str, Any]]:
        """
        Chunk large content for LLM processing with context preservation
        
        Args:
            text: Input text to chunk
            
        Returns:
            List of chunks with metadata
        """
        if len(text) <= self.max_chunk_size:
            return [{
                'chunk_id': 0,
                'content': text,
                'start_pos': 0,
                'end_pos': len(text),
                'word_count': len(text.split()),
                'is_complete': True
            }]
        
        chunks = []
        start = 0
        chunk_id = 0
        
        while start < len(text):
            # Calculate end position
            end = start + self.max_chunk_size
            
            if end >= len(text):
                # Last chunk
                chunk_text = text[start:]
                chunks.append({
                    'chunk_id': chunk_id,
                    'content': chunk_text,
                    'start_pos': start,
                    'end_pos': len(text),
                    'word_count': len(chunk_text.split()),
                    'is_complete': True
                })
                break
            else:
                # Find good breaking point (sentence boundary)
                chunk_text = text[start:end]
                
                # Look for sentence endings near the end of the chunk
                sentence_endings = ['.', '!', '?']
                best_break = -1
                
                # Search backwards from the end for sentence boundary
                for i in range(len(chunk_text) - 1, max(0, len(chunk_text) - 200), -1):
                    if chunk_text[i] in sentence_endings and i < len(chunk_text) - 1:
                        if chunk_text[i + 1] in [' ', '\n', '\t']:
                            best_break = i + 1
                            break
                
                # If no good sentence break found, use word boundary
                if best_break == -1:
                    words = chunk_text.split()
                    if len(words) > 10:  # Keep at least 10 words
                        word_break = len(' '.join(words[:-5]))  # Remove last 5 words
                        best_break = word_break
                    else:
                        best_break = len(chunk_text)
                
                # Create chunk
                final_chunk_text = text[start:start + best_break]
                chunks.append({
                    'chunk_id': chunk_id,
                    'content': final_chunk_text,
                    'start_pos': start,
                    'end_pos': start + best_break,
                    'word_count': len(final_chunk_text.split()),
                    'is_complete': False
                })
                
                # Move start position with overlap
                start = start + best_break - self.chunk_overlap
                chunk_id += 1
        
        logger.info(f"Content chunked into {len(chunks)} pieces for LLM processing")
        return chunks
