# web_content_analyzer - Backend

This folder contains a FastAPI backend skeleton for scraping, processing, AI analysis, and report generation.

Security considerations included:
- URL validation and SSRF prevention checks in `utils/validators.py`
- Basic sanitization in `utils/security.py`
- Max content size and request timeouts in `config/settings.py`

Scraping specifics:
- Uses `requests` + `beautifulsoup4` for fetching and parsing HTML
- Implements simple anti-detection tactics (rotating User-Agent, small randomized delays, retries)

AI analysis structured outputs:
- `models/data_models.AIAnalysisSchema` defines structured output for downstream AI components.

Run locally:

```powershell
python -m pip install -r requirements.txt
uvicorn src.main:app --reload
```
