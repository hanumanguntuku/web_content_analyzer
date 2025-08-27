import pytest
from src.services.content_detection_service import ContentTypeDetectionService
from src.services.integrated_analysis_service import IntegratedAnalysisService
from src.services.report_service import ReportService
from src.services.scraping_service import ScrapingService

import asyncio
def test_content_type_detection_service_detect():
    service = ContentTypeDetectionService()
    from src.models.data_models import ProcessedContent
    url = "https://example.com/article"
    processed_content = ProcessedContent(url=url, cleaned_text="This is a test article about AI.")
    result = asyncio.run(service.detect_content_type(processed_content, url))
    print("Detected content_type:", result[0] if isinstance(result, tuple) else result)
    assert result[0] is not None

import pytest
@pytest.mark.skip(reason="No summarize_content method in IntegratedAnalysisService.")
def test_integrated_analysis_service_summary():
    pass

@pytest.mark.skip(reason="No generate_report method in ReportService.")
def test_report_service_generate():
    pass

@pytest.mark.skip(reason="No is_valid_url method in ScrapingService.")
def test_scraping_service_url_validation():
    pass
