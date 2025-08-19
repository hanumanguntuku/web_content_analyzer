import asyncio
from ..scrapers.web_scraper import WebScraper
from ..models.data_models import ScrapeResult

scraper = WebScraper()

async def scrape_url(url: str) -> ScrapeResult:
    """Async wrapper around the scraper. Returns a ScrapeResult dataclass."""
    loop = asyncio.get_event_loop()
    html, final_url = await loop.run_in_executor(None, scraper.fetch, url)
    content = scraper.extract_content(html)
    return ScrapeResult(url=final_url, html=html, text=content)
