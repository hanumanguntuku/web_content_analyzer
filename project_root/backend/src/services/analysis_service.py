from ..models.data_models import ScrapeResult, AnalysisResult
from ..processors.text_processor import TextProcessor

processor = TextProcessor()

async def analyze_content(scrape: ScrapeResult) -> AnalysisResult:
    """Run content processing and prepare structured AI analysis output.

    The AnalysisResult is structured for downstream AI models or report generation.
    """
    text = processor.extract_text(scrape.text)
    summary = processor.summarize(text)
    keywords = processor.extract_keywords(text)
    # Provide structured output suitable for AI models
    return AnalysisResult(summary=summary, keywords=keywords, length=len(text))
