import json
import os
from typing import Dict, Any, List
from fastapi import APIRouter, HTTPException, BackgroundTasks, Depends, Request, Body
async def get_client_ip(request: Request):
    return request.client.host
from ..models.data_models import URLAnalysisRequest, AnalysisReport, ErrorResponse
from ..services.integrated_analysis_service import IntegratedAnalysisService
from ..services.scraping_service import ScrapingService
from ..utils.exceptions import (
    WebAnalyzerException,
    ValidationException,
    ValidationError,
    SecurityException,
    ScrapingException,
    ScrapingError,
    RateLimitException,
    create_error_response,
    get_user_friendly_message
)
from config.settings import settings

router = APIRouter()
analysis_service = IntegratedAnalysisService()
scraping_service = ScrapingService()

# Keep history in the backend folder so it's independent of the process CWD
HERE = os.path.abspath(os.path.dirname(__file__))
HISTORY_FILE = os.path.abspath(os.path.join(HERE, '..', '..', 'analysis_history.json'))

@router.post("/analyze/batch", response_model=List[AnalysisReport], responses={
    400: {"model": ErrorResponse, "description": "Invalid request"},
    422: {"model": ErrorResponse, "description": "Validation error"},
    500: {"model": ErrorResponse, "description": "Internal server error"}
})
async def analyze_batch(
    requests: List[URLAnalysisRequest] = Body(...),
    client_ip: str = Depends(get_client_ip),
    background_tasks: BackgroundTasks = BackgroundTasks()
):
    """
    Analyze multiple URLs and return a list of analysis reports.
    Also appends each report's summary metrics to a local JSON file for history.
    """
    results = []
    for req in requests:
        try:
            report = await analysis_service.analyze_url(str(req.url))
            results.append(report)
            # Store summary in history
            entry = {
                "url": report.url,
                "title": report.title,
                "timestamp": str(report.analysis_timestamp),
                "overall_quality_score": report.overall_quality_score,
                "extraction_quality": report.extraction_quality,
                "processing_quality": report.processing_quality,
                "seo_score": report.content_analysis.seo_score,
                "readability_score": report.content_analysis.readability_score
            }
            _append_to_history(entry)
        except Exception as e:
            continue  # Optionally collect errors
    return results

def _append_to_history(entry: Dict[str, Any]):
    if not os.path.exists(HISTORY_FILE):
        with open(HISTORY_FILE, "w") as f:
            json.dump([entry], f, indent=2)
    else:
        with open(HISTORY_FILE, "r+") as f:
            try:
                data = json.load(f)
            except Exception:
                data = []
            data.append(entry)
            f.seek(0)
            json.dump(data, f, indent=2)
            f.truncate()

@router.get("/analyze/history", response_model=List[Dict[str, Any]])
async def get_analysis_history():
    """
    Returns the list of past analysis summary metrics from local JSON file.
    """
    if not os.path.exists(HISTORY_FILE):
        return []
    with open(HISTORY_FILE, "r") as f:
        try:
            return json.load(f)
        except Exception:
            return []
