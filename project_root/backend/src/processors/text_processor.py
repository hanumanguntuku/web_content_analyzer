import re
from collections import Counter
from .content_cleaner import ContentCleaner

class TextProcessor:
    def __init__(self):
        self.cleaner = ContentCleaner()

    def extract_text(self, raw_text: str) -> str:
        return self.cleaner.clean(raw_text)

    def summarize(self, text: str, max_chars: int = 400) -> str:
        # Naive summarization: first N characters. Replace with AI model later.
        return text[:max_chars].strip()

    def extract_keywords(self, text: str, top_k: int = 10):
        words = re.findall(r"\w{3,}", text.lower())
        stopwords = set(["the","and","for","with","that","this","from","are","was","were","will","shall"])  # minimal
        filtered = [w for w in words if w not in stopwords]
        most = Counter(filtered).most_common(top_k)
        return [w for w, _ in most]
