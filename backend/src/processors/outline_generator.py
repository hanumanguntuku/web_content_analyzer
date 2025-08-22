import re
from typing import List, Dict, Any

class DocumentOutlineGenerator:
    """
    Generates a hierarchical outline from HTML headings for LLM or downstream processing.
    """
    def __init__(self):
        self.heading_pattern = re.compile(r'<h([1-6])[^>]*>(.*?)</h\1>', re.IGNORECASE | re.DOTALL)

    def generate_outline(self, html: str) -> List[Dict[str, Any]]:
        # Extract all headings with their level and text
        headings = [
            {'level': int(m.group(1)), 'text': self._clean_text(m.group(2))}
            for m in self.heading_pattern.finditer(html)
        ]
        # Build a nested outline
        outline = []
        stack = []
        for heading in headings:
            node = {'heading': heading['text'], 'level': heading['level'], 'children': []}
            while stack and stack[-1]['level'] >= heading['level']:
                stack.pop()
            if stack:
                stack[-1]['children'].append(node)
            else:
                outline.append(node)
            stack.append(node)
        return outline

    def _clean_text(self, text: str) -> str:
        # Remove HTML tags and extra whitespace
        return re.sub(r'<[^>]+>', '', text).strip()
