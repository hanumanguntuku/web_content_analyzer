from pydantic import BaseModel, HttpUrl
from typing import List, Optional

class ScrapeResult(BaseModel):
    url: HttpUrl
    html: str
    text: str

class AnalysisResult(BaseModel):
    summary: str
    keywords: List[str]
    length: int

class Report(BaseModel):
    source_url: HttpUrl
    summary: str
    keywords: List[str]
    content_length: int

# Structured AI analysis output format (example schema)
class AIAnalysisSchema(BaseModel):
    id: Optional[str]
    summary: str
    topics: List[str]
    sentiment: Optional[str]
    entities: Optional[List[str]]
