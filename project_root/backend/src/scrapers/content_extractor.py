from bs4 import BeautifulSoup
import re

class ContentExtractor:
    def extract(self, html: str) -> str:
        """Extract visible text content from HTML, removing scripts/styles."""
        try:
            # Debug: Check what we received
            print(f"DEBUG: HTML input type: {type(html)}")
            if html:
                preview = str(html)[:200] if len(str(html)) > 200 else str(html)
                print(f"DEBUG: HTML preview: {preview}")
            
            # Handle potential encoding issues in HTML
            if isinstance(html, bytes):
                html = html.decode('utf-8', errors='replace')
            
            # Additional check for garbled content
            if html and len(html) > 50:
                # If more than 50% of first 100 chars are non-printable, likely corrupted
                test_chunk = html[:100]
                non_printable_count = sum(1 for c in test_chunk if not c.isprintable() and c not in '\n\t\r ')
                if non_printable_count > len(test_chunk) * 0.5:
                    print("WARNING: Content appears to be corrupted/binary")
                    return "Error: Content appears to be corrupted or in binary format"
            
            soup = BeautifulSoup(html, 'html.parser')
            
            # Remove unwanted tags
            for tag in soup(['script', 'style', 'noscript', 'iframe', 'nav', 'header', 'footer', 'aside']):
                tag.decompose()
            
            # Get text content
            texts = soup.stripped_strings
            content = '\n'.join(texts)
            
            # Clean up the text
            content = self._clean_text(content)
            
            return content
            
        except Exception as e:
            print(f"DEBUG: Exception in extract: {e}")
            # Fallback to simple text extraction if BeautifulSoup fails
            return self._fallback_extract(html)
    
    def _clean_text(self, text: str) -> str:
        """Clean extracted text from common issues."""
        # Remove excessive whitespace
        text = re.sub(r'\s+', ' ', text)
        
        # Remove control characters except newlines and tabs
        text = re.sub(r'[\x00-\x08\x0b\x0c\x0e-\x1f\x7f-\x9f]', '', text)
        
        # Remove non-printable Unicode characters
        text = ''.join(char for char in text if char.isprintable() or char in '\n\t ')
        
        return text.strip()
    
    def _fallback_extract(self, html: str) -> str:
        """Fallback text extraction if BeautifulSoup fails."""
        try:
            # Simple regex to remove HTML tags
            text = re.sub(r'<[^>]+>', '', html)
            return self._clean_text(text)
        except Exception:
            return "Error: Could not extract content from this URL"
