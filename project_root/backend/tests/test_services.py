import pytest
from src.processors.text_processor import TextProcessor

# Note: lightweight tests to validate structure; expand later

def test_text_processor_keywords():
    tp = TextProcessor()
    text = "This is a test. Test content with python python testing."
    kws = tp.extract_keywords(text, top_k=3)
    assert 'python' in kws
