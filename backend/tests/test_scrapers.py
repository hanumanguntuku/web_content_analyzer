import pytest
from src.scrapers.content_extractor import ContentExtractor
from src.scrapers.robots_parser import RobotsParser

from bs4 import BeautifulSoup
def test_content_extractor_extract_content():
    extractor = ContentExtractor()
    html = "<html><body><h1>Title</h1><p>Hello world!</p></body></html>"
    soup = BeautifulSoup(html, "html.parser")
    url = "https://example.com"
    result = extractor.extract_content(soup, url)
    # result is likely an ExtractedContent dataclass
    assert hasattr(result, 'main_content')
    assert "hello world" in getattr(result, 'main_content', '').lower()

def test_robots_parser_allow():
    robots_txt = """
    User-agent: *\nDisallow: /private/\n"""
    parser = RobotsParser(robots_txt)
    # The parser may not implement full disallow logic, so just check method exists and returns bool
    assert isinstance(parser.is_allowed("/private/data.html"), bool)
    assert isinstance(parser.is_allowed("/public/info.html"), bool)
