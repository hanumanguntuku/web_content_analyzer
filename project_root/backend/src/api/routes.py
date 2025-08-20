from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, HttpUrl
from ..services.scraping_service import WebScraperService
from ..services import analysis_service, report_service

router = APIRouter()

class AnalyzeRequest(BaseModel):
    url: HttpUrl

# Initialize the scraping service
scraper_service = WebScraperService()

@router.post("/analyze")
async def analyze(req: AnalyzeRequest):
    """High-level endpoint: scrape, process, analyze, and return a report."""
    try:
        # Use the new service pattern
        scraped_content = await scraper_service.scrape_url(str(req.url))
        
        # Check if scraping was successful
        if not scraped_content.success:
            raise HTTPException(
                status_code=400, 
                detail=f"Failed to scrape URL: {scraped_content.error_message}"
            )
        
        # Convert to legacy format for analysis service compatibility
        from ..models.data_models import ScrapeResult
        scrape_result = ScrapeResult(
            url=scraped_content.final_url,
            html=scraped_content.html,
            text=scraped_content.text
        )
        
        analysis = await analysis_service.analyze_content(scrape_result)
        report = await report_service.generate_report(scrape_result, analysis)
        return report.dict()
        
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))

@router.post("/scrape")
async def scrape(req: AnalyzeRequest):
    """Direct scraping endpoint for testing the WebScraperService."""
    try:
        scraped_content = await scraper_service.scrape_url(str(req.url))
        return scraped_content.dict()
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))
