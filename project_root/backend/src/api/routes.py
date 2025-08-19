from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, HttpUrl
from ..services import scraping_service, analysis_service, report_service

router = APIRouter()

class AnalyzeRequest(BaseModel):
    url: HttpUrl

@router.post("/analyze")
async def analyze(req: AnalyzeRequest):
    """High-level endpoint: scrape, process, analyze, and return a report."""
    try:
        scrape_result = await scraping_service.scrape_url(str(req.url))
        analysis = await analysis_service.analyze_content(scrape_result)
        report = await report_service.generate_report(scrape_result, analysis)
        return report.dict()
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))
