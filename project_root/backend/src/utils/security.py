import re
import html

def sanitize_text(text: str) -> str:
    """Very small sanitizer: unescape HTML entities and remove control characters."""
    text = html.unescape(text)
    # Remove remaining tags (if any)
    text = re.sub(r"<[^>]+>", "", text)
    # Strip unusual control codes
    text = re.sub(r"[\x00-\x08\x0b-\x0c\x0e-\x1f]", "", text)
    return text
