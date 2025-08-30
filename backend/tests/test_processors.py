import pytest
from src.processors.keyphrase_extractor import SimpleKeyPhraseExtractor
from src.processors.outline_generator import DocumentOutlineGenerator
from src.processors.text_processor import TextProcessor

def test_keyphrase_extractor_basic():
    extractor = SimpleKeyPhraseExtractor()
    text = "Python is a popular programming language. AI is transforming the world."
    result = extractor.extract(text)
    assert isinstance(result, list)
    assert any("python" in k.lower() for k in result)

def test_outline_generator_basic():
    generator = DocumentOutlineGenerator()
    html = "<h1>Introduction</h1><h2>Methods</h2><h2>Results</h2>"
    outline = generator.generate_outline(html)
    assert isinstance(outline, list)
    assert any("introduction" in o['heading'].lower() for o in outline)

def test_text_processor_deep_clean_text():
    processor = TextProcessor()
    text = "Hello   world! This is a test.\n\n"
    cleaned = processor.deep_clean_text(text)
    assert isinstance(cleaned, str)
    assert "hello" in cleaned.lower()
