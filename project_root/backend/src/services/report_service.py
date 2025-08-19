from ..models.data_models import ScrapeResult, AnalysisResult, Report

async def generate_report(scrape: ScrapeResult, analysis: AnalysisResult) -> Report:
    """Compose a report object from scrape and analysis results."""
    report = Report(
        source_url=scrape.url,
        summary=analysis.summary,
        keywords=analysis.keywords,
        content_length=analysis.length,
    )
    return report
