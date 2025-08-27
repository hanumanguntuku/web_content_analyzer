import re
from typing import List
from collections import Counter

class SimpleKeyPhraseExtractor:
    """
    SimpleKeyPhraseExtractor extracts key phrases from text using n-gram frequency heuristics.
    For production, consider using spaCy, RAKE, or KeyBERT.
    """
    def __init__(self, min_len: int = 2, max_len: int = 5, top_n: int = 15):
        self.min_len = min_len
        self.max_len = max_len
        self.top_n = top_n

    def extract(self, text: str) -> List[str]:
        """
        Extract keyphrases from the input text using n-gram frequency heuristics.
        Args:
            text (str): Input text to extract keyphrases from.
        Returns:
            List[str]: List of extracted keyphrases.
        """
        # Lowercase and remove non-alphanumeric except spaces
        clean_text = re.sub(r'[^\w\s]', '', text.lower())
        words = clean_text.split()
        phrases = []
        # Extract n-grams (2-5 words)
        for n in range(self.min_len, self.max_len + 1):
            for i in range(len(words) - n + 1):
                phrase = ' '.join(words[i:i+n])
                phrases.append(phrase)
        # Count and return most common
        counter = Counter(phrases)
        return [phrase for phrase, _ in counter.most_common(self.top_n)]
