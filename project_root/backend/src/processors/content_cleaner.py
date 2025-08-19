import re
from ..utils.security import sanitize_text

class ContentCleaner:
    def clean(self, text: str) -> str:
        # Remove long whitespace runs and control chars
        text = re.sub(r"[\r\t\x0b\x0c]", " ", text)
        text = re.sub(r"\s+", " ", text).strip()
        # Basic sanitization
        text = sanitize_text(text)
        return text
