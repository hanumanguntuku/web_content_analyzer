# Milestone 1 Implementation Plan - Bottom-Up Approach

## Overview
**Milestone:** M1 - Web Scraping Foundation & Data Extraction  
**Approach:** Bottom-up development (Infrastructure → Data → Service → Presentation)  
**Timeline:** Day 1 of 2-day accelerated development  
**Architecture:** N-Tier with clean separation of concerns  

## Implementation Strategy

### Bottom-Up Sequence
1. **Infrastructure Layer** - Foundation setup, Docker, basic structure
2. **Data Layer** - Web scraping, content extraction, data models
3. **Security Layer** - SSRF prevention, validation, sanitization  
4. **Service Layer** - Business logic, API endpoints, error handling
5. **Presentation Layer** - UI components, user interaction
6. **Integration Layer** - End-to-end connectivity and testing

## Phase 1: Infrastructure Foundation (2-3 hours)

### Task M1-INFRA-01: Project Structure Creation
**Duration:** 2 hours | **Priority:** Critical | **Dependencies:** None

#### Implementation Steps:
1. **Create N-Tier Directory Structure**
```bash
project_root/
├── backend/                    # BACKEND APPLICATION (FastAPI)
│   ├── src/
│   │   ├── api/               # API LAYER (Presentation Tier)
│   │   │   ├── __init__.py
│   │   │   ├── routes.py      # API endpoints
│   │   │   └── middleware.py  # Request/response middleware
│   │   ├── services/          # SERVICE LAYER (Business Logic Tier)
│   │   │   ├── __init__.py
│   │   │   ├── analysis_service.py
│   │   │   ├── scraping_service.py
│   │   │   └── report_service.py
│   │   ├── scrapers/          # DATA LAYER - Web Scraping
│   │   │   ├── __init__.py
│   │   │   ├── web_scraper.py
│   │   │   └── content_extractor.py
│   │   ├── processors/        # DATA LAYER - Content Processing  
│   │   │   ├── __init__.py
│   │   │   ├── text_processor.py
│   │   │   └── content_cleaner.py
│   │   ├── models/            # DATA MODELS
│   │   │   ├── __init__.py
│   │   │   └── data_models.py
│   │   └── utils/             # UTILITIES & SECURITY
│   │       ├── validators.py  # URL validation & SSRF prevention
│   │       ├── security.py    # Content sanitization
│   │       ├── exceptions.py  # Custom exceptions
│   │       └── helpers.py     # Helper functions
│   ├── config/                # CONFIGURATION
│   │   └── settings.py
│   ├── tests/                 # BACKEND TESTS
│   │   ├── test_api.py
│   │   └── test_services.py
│   ├── main.py               # Main FastAPI app entry point
│   ├── requirements.txt      # Backend dependencies
│   └── Dockerfile           # Backend container definition
├── frontend/                 # FRONTEND APP (Streamlit)
│   ├── src/
│   │   ├── components/       # UI COMPONENTS
│   │   │   ├── url_input.py
│   │   │   ├── results_display.py
│   │   │   └── progress.py
│   │   ├── services/         # FRONTEND SERVICES
│   │   │   ├── api_client.py    # Backend API client
│   │   │   └── state_manager.py # Streamlit state management
│   │   └── utils/            # FRONTEND UTILITIES
│   │       ├── formatters.py    # Result formatting
│   │       └── validators.py    # Frontend input validation
│   ├── assets/               # STATIC ASSETS
│   │   └── styles.css       # Custom styling
│   ├── templates/            # REPORT TEMPLATES
│   │   └── report_template.html
│   ├── app.py               # Main Streamlit application
│   ├── requirements.txt     # Frontend dependencies
│   └── Dockerfile          # Frontend container definition
├── docker-compose.yml       # Orchestration
└── README.md               # Project documentation
```

2. **Create Base Configuration Files**
   - Setup backend/requirements.txt with core dependencies
   - Setup frontend/requirements.txt with Streamlit dependencies
   - Create basic settings.py for configuration management
   - Initialize all __init__.py files

#### Build & Test:
- **Build:** Verify directory structure creation (0.5h)
- **Test:** Ensure all files are properly initialized (0.5h)

---

### Task M1-INFRA-02: Docker Environment Setup
**Duration:** 1 hour | **Priority:** Critical | **Dependencies:** M1-INFRA-01

#### Implementation Steps:
1. **Backend Dockerfile**
```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
EXPOSE 8000
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

2. **Frontend Dockerfile**
```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
EXPOSE 8501
CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]
```

3. **Docker Compose Configuration**
```yaml
version: '3.8'
services:
  backend:
    build: ./backend
    ports:
      - "8000:8000"
    environment:
      - ENV=development
    volumes:
      - ./backend:/app
  
  frontend:
    build: ./frontend
    ports:
      - "8501:8501"
    depends_on:
      - backend
    environment:
      - BACKEND_URL=http://backend:8000
    volumes:
      - ./frontend:/app
```

#### Build & Test & Deploy:
- **Build:** Build Docker images (1h)
- **Test:** Test container startup (0.5h)
- **Deploy:** Setup local development environment (0.5h)

---

### Task M1-INFRA-03: FastAPI Backend Foundation
**Duration:** 1.5 hours | **Priority:** Critical | **Dependencies:** M1-INFRA-01

#### Implementation Steps:
1. **Main FastAPI Application (main.py)**
```python
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import uvicorn

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    print("Starting Web Content Analyzer API...")
    yield
    # Shutdown
    print("Shutting down Web Content Analyzer API...")

app = FastAPI(
    title="Web Content Analyzer API",
    description="API for analyzing web content",
    version="1.0.0",
    lifespan=lifespan
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8501"],  # Streamlit frontend
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Health check endpoint
@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "web-content-analyzer"}

# Include API routes
from src.api.routes import router as api_router
app.include_router(api_router, prefix="/api/v1")

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
```

2. **Basic API Routes (src/api/routes.py)**
```python
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import logging

router = APIRouter()
logger = logging.getLogger(__name__)

class URLAnalysisRequest(BaseModel):
    url: str
    options: dict = {}

@router.post("/analyze")
async def analyze_url(request: URLAnalysisRequest):
    """Analyze a website URL and return content analysis"""
    try:
        # Placeholder for M1 - will implement scraping logic
        return {
            "status": "success",
            "url": request.url,
            "message": "Analysis endpoint ready - scraping logic to be implemented"
        }
    except Exception as e:
        logger.error(f"Analysis failed: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/status")
async def get_status():
    """Get service status"""
    return {"status": "running", "version": "1.0.0"}
```

3. **Settings Configuration (config/settings.py)**
```python
from pydantic_settings import BaseSettings
from typing import List

class Settings(BaseSettings):
    # API Configuration
    api_title: str = "Web Content Analyzer"
    api_version: str = "1.0.0"
    
    # Security Configuration
    allowed_domains: List[str] = ["*"]  # Will restrict in production
    max_content_size: int = 10 * 1024 * 1024  # 10MB
    request_timeout: int = 30  # seconds
    
    # Scraping Configuration
    user_agents: List[str] = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"
    ]
    
    class Config:
        env_file = ".env"

settings = Settings()
```

#### Build & Test:
- **Build:** Setup FastAPI application (0.5h)
- **Test:** Test API startup and health endpoints (1h)

---

### Task M1-INFRA-04: Streamlit Frontend Foundation
**Duration:** 1 hour | **Priority:** Critical | **Dependencies:** M1-INFRA-01

#### Implementation Steps:
1. **Main Streamlit Application (app.py)**
```python
import streamlit as st
import requests
import asyncio
from src.services.api_client import APIClient
from src.components.url_input import render_url_input
from src.components.results_display import render_results

# Page configuration
st.set_page_config(
    page_title="Web Content Analyzer",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize API client
@st.cache_resource
def get_api_client():
    return APIClient(base_url="http://backend:8000")

def main():
    st.title("🔍 Web Content Analyzer")
    st.markdown("Extract and analyze content from any website")
    
    # Initialize session state
    if 'analysis_results' not in st.session_state:
        st.session_state.analysis_results = None
    
    # Sidebar for settings
    with st.sidebar:
        st.header("Settings")
        st.info("Advanced settings will be available in later milestones")
    
    # Main content area
    col1, col2 = st.columns([1, 2])
    
    with col1:
        st.subheader("URL Input")
        url = render_url_input()
        
        if st.button("Analyze Website", type="primary"):
            if url:
                with st.spinner("Analyzing website..."):
                    api_client = get_api_client()
                    try:
                        results = api_client.analyze_url(url)
                        st.session_state.analysis_results = results
                        st.success("Analysis completed!")
                    except Exception as e:
                        st.error(f"Analysis failed: {str(e)}")
            else:
                st.warning("Please enter a valid URL")
    
    with col2:
        st.subheader("Analysis Results")
        if st.session_state.analysis_results:
            render_results(st.session_state.analysis_results)
        else:
            st.info("Enter a URL and click 'Analyze Website' to see results")

if __name__ == "__main__":
    main()
```

2. **API Client Service (src/services/api_client.py)**
```python
import requests
import streamlit as st
from typing import Dict, Any

class APIClient:
    def __init__(self, base_url: str):
        self.base_url = base_url.rstrip('/')
    
    def analyze_url(self, url: str, options: Dict = None) -> Dict[str, Any]:
        """Send URL for analysis to the backend API"""
        endpoint = f"{self.base_url}/api/v1/analyze"
        payload = {
            "url": url,
            "options": options or {}
        }
        
        try:
            response = requests.post(
                endpoint,
                json=payload,
                timeout=30
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            raise Exception(f"API request failed: {str(e)}")
    
    def get_status(self) -> Dict[str, Any]:
        """Get API status"""
        endpoint = f"{self.base_url}/api/v1/status"
        response = requests.get(endpoint, timeout=10)
        response.raise_for_status()
        return response.json()
```

#### Build & Test:
- **Build:** Setup Streamlit application (0.5h)
- **Test:** Test frontend startup and basic navigation (0.5h)

---

## Phase 2: Data Layer Implementation (6-8 hours)

### Task M1-DATA-01: Web Scraper Service Core
**Duration:** 3 hours | **Priority:** Critical | **Dependencies:** M1-INFRA-03

#### Implementation Steps:
1. **Core Web Scraper (src/scrapers/web_scraper.py)**
```python
import aiohttp
import asyncio
from bs4 import BeautifulSoup
from typing import Dict, Any, Optional
import logging
from urllib.parse import urlparse, urljoin
import time
import random

from ..utils.validators import URLValidator
from ..utils.exceptions import ScrapingError, InvalidURLError
from ..models.data_models import ScrapedContent
from ..config.settings import settings

logger = logging.getLogger(__name__)

class WebScraperService:
    def __init__(self):
        self.timeout = aiohttp.ClientTimeout(total=settings.request_timeout)
        self.user_agents = settings.user_agents
        self.session = None
    
    async def __aenter__(self):
        self.session = aiohttp.ClientSession(
            timeout=self.timeout,
            headers=self._get_headers()
        )
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    def _get_headers(self) -> Dict[str, str]:
        """Generate request headers with rotating user agents"""
        return {
            'User-Agent': random.choice(self.user_agents),
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'DNT': '1',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        }
    
    async def scrape_url(self, url: str) -> ScrapedContent:
        """Scrape content from a URL with comprehensive error handling"""
        try:
            # Validate URL first
            validator = URLValidator()
            if not validator.validate_url(url):
                raise InvalidURLError(f"Invalid or forbidden URL: {url}")
            
            logger.info(f"Starting scrape for URL: {url}")
            
            # Perform the request
            async with self.session.get(url) as response:
                # Check response status
                if response.status != 200:
                    raise ScrapingError(f"HTTP {response.status}: {response.reason}")
                
                # Check content type
                content_type = response.headers.get('content-type', '').lower()
                if 'text/html' not in content_type:
                    raise ScrapingError(f"Unsupported content type: {content_type}")
                
                # Check content size
                content_length = response.headers.get('content-length')
                if content_length and int(content_length) > settings.max_content_size:
                    raise ScrapingError(f"Content too large: {content_length} bytes")
                
                # Read content with size limit
                content = await response.text()
                if len(content.encode('utf-8')) > settings.max_content_size:
                    raise ScrapingError("Content exceeds size limit")
                
                # Parse with BeautifulSoup
                soup = BeautifulSoup(content, 'html.parser')
                
                # Extract basic information
                scraped_data = ScrapedContent(
                    url=url,
                    title=self._extract_title(soup),
                    meta_description=self._extract_meta_description(soup),
                    raw_html=content,
                    status_code=response.status,
                    content_type=content_type,
                    scraped_at=time.time()
                )
                
                logger.info(f"Successfully scraped URL: {url}")
                return scraped_data
                
        except aiohttp.ClientError as e:
            logger.error(f"HTTP client error for {url}: {str(e)}")
            raise ScrapingError(f"Network error: {str(e)}")
        except Exception as e:
            logger.error(f"Unexpected error scraping {url}: {str(e)}")
            raise ScrapingError(f"Scraping failed: {str(e)}")
    
    def _extract_title(self, soup: BeautifulSoup) -> str:
        """Extract page title"""
        title_tag = soup.find('title')
        return title_tag.get_text().strip() if title_tag else "No title found"
    
    def _extract_meta_description(self, soup: BeautifulSoup) -> str:
        """Extract meta description"""
        meta_desc = soup.find('meta', attrs={'name': 'description'})
        if meta_desc and meta_desc.get('content'):
            return meta_desc['content'].strip()
        return "No description found"
```

2. **Request Retry Logic & Rate Limiting**
```python
    async def scrape_with_retry(self, url: str, max_retries: int = 3) -> ScrapedContent:
        """Scrape with retry logic and exponential backoff"""
        for attempt in range(max_retries):
            try:
                # Add delay between requests for rate limiting
                if attempt > 0:
                    delay = 2 ** attempt + random.uniform(0, 1)
                    await asyncio.sleep(delay)
                    logger.info(f"Retry attempt {attempt + 1} for {url}")
                
                return await self.scrape_url(url)
                
            except ScrapingError as e:
                if attempt == max_retries - 1:
                    raise e
                logger.warning(f"Attempt {attempt + 1} failed for {url}: {str(e)}")
        
        raise ScrapingError(f"Failed to scrape {url} after {max_retries} attempts")
```

#### Build & Test:
- **Build:** Integrate with FastAPI service layer (0.5h)
- **Test:** Test scraping with various website types (1.5h)

---

### Task M1-DATA-02: Content Extractor Engine
**Duration:** 2 hours | **Priority:** Critical | **Dependencies:** M1-DATA-01

#### Implementation Steps:
1. **Intelligent Content Extraction (src/scrapers/content_extractor.py)**
```python
from bs4 import BeautifulSoup, Tag
from typing import List, Dict, Any, Optional
import re
import logging
from ..models.data_models import ExtractedContent, ContentSection

logger = logging.getLogger(__name__)

class ContentExtractor:
    def __init__(self):
        # Common navigation and advertisement selectors to remove
        self.noise_selectors = [
            'nav', 'header', 'footer', 'aside', '.sidebar', '.navigation',
            '.ads', '.advertisement', '.social', '.comments', '.breadcrumb',
            'script', 'style', 'noscript', '.popup', '.modal'
        ]
        
        # Likely main content selectors (ordered by priority)
        self.content_selectors = [
            'main', 'article', '.content', '.main-content', '.post-content',
            '.entry-content', '.article-body', '#content', '#main'
        ]
    
    def extract_content(self, soup: BeautifulSoup, url: str) -> ExtractedContent:
        """Extract meaningful content from HTML soup"""
        try:
            # Remove noise elements
            cleaned_soup = self._remove_noise(soup)
            
            # Extract main content
            main_content = self._extract_main_content(cleaned_soup)
            
            # Extract structured data
            headings = self._extract_headings(cleaned_soup)
            links = self._extract_links(cleaned_soup, url)
            images = self._extract_images(cleaned_soup, url)
            
            # Extract metadata
            metadata = self._extract_metadata(soup)
            
            extracted = ExtractedContent(
                url=url,
                main_content=main_content,
                headings=headings,
                links=links,
                images=images,
                metadata=metadata,
                word_count=len(main_content.split()) if main_content else 0,
                sections=self._identify_sections(cleaned_soup)
            )
            
            logger.info(f"Extracted {extracted.word_count} words from {url}")
            return extracted
            
        except Exception as e:
            logger.error(f"Content extraction failed for {url}: {str(e)}")
            raise
    
    def _remove_noise(self, soup: BeautifulSoup) -> BeautifulSoup:
        """Remove navigation, ads, and other noise elements"""
        # Create a copy to avoid modifying original
        cleaned_soup = BeautifulSoup(str(soup), 'html.parser')
        
        for selector in self.noise_selectors:
            elements = cleaned_soup.select(selector)
            for element in elements:
                element.decompose()
        
        return cleaned_soup
    
    def _extract_main_content(self, soup: BeautifulSoup) -> str:
        """Extract the main content text"""
        # Try specific content selectors first
        for selector in self.content_selectors:
            elements = soup.select(selector)
            if elements:
                # Use the first match or largest by text length
                content_element = max(elements, key=lambda x: len(x.get_text()))
                return self._clean_text(content_element.get_text())
        
        # Fallback: use body content
        body = soup.find('body')
        if body:
            return self._clean_text(body.get_text())
        
        # Last resort: all text
        return self._clean_text(soup.get_text())
    
    def _clean_text(self, text: str) -> str:
        """Clean and normalize text content"""
        if not text:
            return ""
        
        # Remove extra whitespace and normalize
        text = re.sub(r'\s+', ' ', text)
        text = text.strip()
        
        # Remove common boilerplate phrases
        boilerplate_patterns = [
            r'cookie policy',
            r'privacy policy',
            r'terms of service',
            r'subscribe to newsletter',
            r'follow us on',
        ]
        
        for pattern in boilerplate_patterns:
            text = re.sub(pattern, '', text, flags=re.IGNORECASE)
        
        return text
    
    def _extract_headings(self, soup: BeautifulSoup) -> List[Dict[str, Any]]:
        """Extract heading hierarchy"""
        headings = []
        for level in range(1, 7):  # h1 to h6
            for heading in soup.find_all(f'h{level}'):
                headings.append({
                    'level': level,
                    'text': self._clean_text(heading.get_text()),
                    'id': heading.get('id', ''),
                })
        return headings
    
    def _extract_links(self, soup: BeautifulSoup, base_url: str) -> List[Dict[str, str]]:
        """Extract and categorize links"""
        links = []
        for link in soup.find_all('a', href=True):
            href = link['href']
            text = self._clean_text(link.get_text())
            
            if text and href:
                # Resolve relative URLs
                if href.startswith('http'):
                    full_url = href
                else:
                    from urllib.parse import urljoin
                    full_url = urljoin(base_url, href)
                
                links.append({
                    'url': full_url,
                    'text': text,
                    'type': self._categorize_link(href)
                })
        return links
    
    def _categorize_link(self, href: str) -> str:
        """Categorize link type"""
        href_lower = href.lower()
        if href_lower.startswith('mailto:'):
            return 'email'
        elif href_lower.startswith('tel:'):
            return 'phone'
        elif any(social in href_lower for social in ['twitter', 'facebook', 'linkedin', 'instagram']):
            return 'social'
        elif href_lower.startswith('#'):
            return 'anchor'
        else:
            return 'external' if href.startswith('http') else 'internal'
    
    def _extract_images(self, soup: BeautifulSoup, base_url: str) -> List[Dict[str, str]]:
        """Extract image information"""
        images = []
        for img in soup.find_all('img', src=True):
            src = img['src']
            alt = img.get('alt', '')
            
            # Resolve relative URLs
            if src.startswith('http'):
                full_url = src
            else:
                from urllib.parse import urljoin
                full_url = urljoin(base_url, src)
            
            images.append({
                'url': full_url,
                'alt': alt,
                'title': img.get('title', '')
            })
        return images
    
    def _extract_metadata(self, soup: BeautifulSoup) -> Dict[str, Any]:
        """Extract page metadata"""
        metadata = {}
        
        # Meta tags
        for meta in soup.find_all('meta'):
            name = meta.get('name') or meta.get('property')
            content = meta.get('content')
            if name and content:
                metadata[name] = content
        
        # Structured data (JSON-LD)
        json_ld_scripts = soup.find_all('script', type='application/ld+json')
        if json_ld_scripts:
            import json
            structured_data = []
            for script in json_ld_scripts:
                try:
                    data = json.loads(script.string)
                    structured_data.append(data)
                except json.JSONDecodeError:
                    continue
            if structured_data:
                metadata['structured_data'] = structured_data
        
        return metadata
    
    def _identify_sections(self, soup: BeautifulSoup) -> List[ContentSection]:
        """Identify content sections based on structure"""
        sections = []
        
        # Look for semantic sections
        for section in soup.find_all(['section', 'article', 'div']):
            if section.find(['h1', 'h2', 'h3']):  # Has heading
                heading = section.find(['h1', 'h2', 'h3'])
                content = self._clean_text(section.get_text())
                
                if len(content) > 100:  # Minimum content length
                    sections.append(ContentSection(
                        title=self._clean_text(heading.get_text()) if heading else "Untitled Section",
                        content=content,
                        type="section"
                    ))
        
        return sections
```

#### Build & Test:
- **Build:** Integrate content extraction with scraper service (0.5h)  
- **Test:** Test extraction accuracy on different website layouts (1h)

---

### Task M1-DATA-03: Content Cleaning Pipeline
**Duration:** 2 hours | **Priority:** High | **Dependencies:** M1-DATA-02

#### Implementation Steps:
1. **Text Processing Pipeline (src/processors/text_processor.py)**
```python
import re
import html
from typing import List, Dict, Any
import logging
from ..models.data_models import ProcessedContent, ExtractedContent

logger = logging.getLogger(__name__)

class TextProcessor:
    def __init__(self):
        # Regex patterns for cleaning
        self.email_pattern = re.compile(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b')
        self.phone_pattern = re.compile(r'(\+?\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}')
        self.url_pattern = re.compile(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+')
        
        # Stop words for keyword extraction
        self.stop_words = {
            'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by',
            'this', 'that', 'these', 'those', 'is', 'are', 'was', 'were', 'be', 'been', 'being',
            'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would', 'could', 'should'
        }
    
    def process_content(self, extracted_content: ExtractedContent) -> ProcessedContent:
        """Process extracted content into clean, structured format"""
        try:
            # Clean main content
            cleaned_text = self._clean_text_content(extracted_content.main_content)
            
            # Extract key information
            keywords = self._extract_keywords(cleaned_text)
            contact_info = self._extract_contact_info(cleaned_text)
            
            # Process sections
            processed_sections = []
            for section in extracted_content.sections:
                processed_sections.append({
                    'title': section.title,
                    'content': self._clean_text_content(section.content),
                    'word_count': len(section.content.split()),
                    'type': section.type
                })
            
            processed = ProcessedContent(
                url=extracted_content.url,
                title=self._clean_text_content(extracted_content.metadata.get('title', '')),
                description=self._clean_text_content(extracted_content.metadata.get('description', '')),
                cleaned_content=cleaned_text,
                keywords=keywords,
                contact_info=contact_info,
                sections=processed_sections,
                word_count=len(cleaned_text.split()),
                language=self._detect_language(cleaned_text),
                readability_score=self._calculate_readability(cleaned_text)
            )
            
            logger.info(f"Processed content for {extracted_content.url}: {processed.word_count} words")
            return processed
            
        except Exception as e:
            logger.error(f"Content processing failed for {extracted_content.url}: {str(e)}")
            raise
    
    def _clean_text_content(self, text: str) -> str:
        """Deep clean text content"""
        if not text:
            return ""
        
        # Decode HTML entities
        text = html.unescape(text)
        
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text)
        
        # Remove special characters but keep punctuation
        text = re.sub(r'[^\w\s\.,!?;:()-]', '', text)
        
        # Remove repeated punctuation
        text = re.sub(r'([.!?]){2,}', r'\1', text)
        
        # Clean up spacing around punctuation
        text = re.sub(r'\s+([.!?;:,])', r'\1', text)
        text = re.sub(r'([.!?;:,])\s*([.!?;:,])', r'\1 \2', text)
        
        return text.strip()
    
    def _extract_keywords(self, text: str, max_keywords: int = 20) -> List[str]:
        """Extract important keywords from text"""
        if not text:
            return []
        
        # Tokenize and clean
        words = re.findall(r'\b[a-zA-Z]{3,}\b', text.lower())
        
        # Remove stop words
        words = [word for word in words if word not in self.stop_words]
        
        # Count frequency
        word_freq = {}
        for word in words:
            word_freq[word] = word_freq.get(word, 0) + 1
        
        # Sort by frequency and return top keywords
        sorted_words = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)
        return [word for word, freq in sorted_words[:max_keywords]]
    
    def _extract_contact_info(self, text: str) -> Dict[str, List[str]]:
        """Extract contact information from text"""
        contact_info = {
            'emails': [],
            'phones': [],
            'urls': []
        }
        
        # Extract emails
        emails = self.email_pattern.findall(text)
        contact_info['emails'] = list(set(emails))
        
        # Extract phone numbers
        phones = self.phone_pattern.findall(text)
        contact_info['phones'] = list(set(phones))
        
        # Extract URLs
        urls = self.url_pattern.findall(text)
        contact_info['urls'] = list(set(urls))
        
        return contact_info
    
    def _detect_language(self, text: str) -> str:
        """Simple language detection (placeholder for more sophisticated detection)"""
        if not text:
            return "unknown"
        
        # Simple heuristic - count common English words
        english_indicators = ['the', 'and', 'is', 'in', 'to', 'of', 'a', 'that', 'it', 'with']
        words = text.lower().split()
        english_count = sum(1 for word in words if word in english_indicators)
        
        if english_count > len(words) * 0.1:  # 10% threshold
            return "en"
        else:
            return "unknown"
    
    def _calculate_readability(self, text: str) -> float:
        """Calculate simple readability score (Flesch Reading Ease approximation)"""
        if not text:
            return 0.0
        
        sentences = len(re.findall(r'[.!?]+', text))
        words = len(text.split())
        syllables = sum(self._count_syllables(word) for word in text.split())
        
        if sentences == 0 or words == 0:
            return 0.0
        
        # Simplified Flesch Reading Ease
        score = 206.835 - (1.015 * (words / sentences)) - (84.6 * (syllables / words))
        return max(0.0, min(100.0, score))  # Clamp between 0-100
    
    def _count_syllables(self, word: str) -> int:
        """Count syllables in a word (simplified)"""
        word = word.lower()
        vowels = 'aeiouy'
        syllable_count = 0
        prev_was_vowel = False
        
        for char in word:
            is_vowel = char in vowels
            if is_vowel and not prev_was_vowel:
                syllable_count += 1
            prev_was_vowel = is_vowel
        
        # Adjust for silent 'e'
        if word.endswith('e'):
            syllable_count -= 1
        
        return max(1, syllable_count)  # At least 1 syllable
```

#### Build & Test:
- **Build:** Integrate with content extraction pipeline (0.5h)
- **Test:** Test processing accuracy and performance (1h)

---

### Task M1-DATA-04: Data Models & Validation
**Duration:** 1.5 hours | **Priority:** High | **Dependencies:** M1-DATA-01

#### Implementation Steps:
1. **Comprehensive Data Models (src/models/data_models.py)**
```python
from pydantic import BaseModel, Field, validator, HttpUrl
from typing import List, Dict, Any, Optional, Union
from datetime import datetime
import re

class URLAnalysisRequest(BaseModel):
    """Request model for URL analysis"""
    url: HttpUrl = Field(..., description="URL to analyze")
    options: Dict[str, Any] = Field(default_factory=dict, description="Analysis options")
    
    @validator('url')
    def validate_url_string(cls, v):
        """Additional URL validation"""
        url_str = str(v)
        if len(url_str) > 2048:
            raise ValueError("URL too long")
        return v

class ScrapedContent(BaseModel):
    """Raw scraped content from a website"""
    url: str
    title: str
    meta_description: str
    raw_html: str
    status_code: int
    content_type: str
    scraped_at: float
    headers: Dict[str, str] = Field(default_factory=dict)
    
    class Config:
        # Don't include raw_html in JSON output by default (too large)
        fields = {'raw_html': {'exclude': True}}

class ContentSection(BaseModel):
    """Individual content section"""
    title: str
    content: str
    type: str = "section"
    word_count: int = 0
    
    @validator('word_count', always=True)
    def calculate_word_count(cls, v, values):
        if 'content' in values:
            return len(values['content'].split())
        return v

class ExtractedContent(BaseModel):
    """Extracted and structured content"""
    url: str
    main_content: str
    headings: List[Dict[str, Any]] = Field(default_factory=list)
    links: List[Dict[str, str]] = Field(default_factory=list)
    images: List[Dict[str, str]] = Field(default_factory=list)
    metadata: Dict[str, Any] = Field(default_factory=dict)
    word_count: int = 0
    sections: List[ContentSection] = Field(default_factory=list)
    extracted_at: float = Field(default_factory=lambda: datetime.now().timestamp())

class ProcessedContent(BaseModel):
    """Cleaned and processed content"""
    url: str
    title: str
    description: str
    cleaned_content: str
    keywords: List[str] = Field(default_factory=list)
    contact_info: Dict[str, List[str]] = Field(default_factory=dict)
    sections: List[Dict[str, Any]] = Field(default_factory=list)
    word_count: int = 0
    language: str = "unknown"
    readability_score: float = 0.0
    processed_at: float = Field(default_factory=lambda: datetime.now().timestamp())

class AnalysisReport(BaseModel):
    """Final analysis report"""
    url: str
    title: str
    summary: str
    content_type: str
    word_count: int
    readability_score: float
    language: str
    keywords: List[str]
    key_sections: List[Dict[str, Any]]
    contact_information: Dict[str, List[str]]
    metadata: Dict[str, Any]
    analysis_timestamp: float = Field(default_factory=lambda: datetime.now().timestamp())
    processing_time: float = 0.0
    
    class Config:
        schema_extra = {
            "example": {
                "url": "https://example.com",
                "title": "Example Website",
                "summary": "This is an example website...",
                "content_type": "company_website",
                "word_count": 1250,
                "readability_score": 65.5,
                "language": "en",
                "keywords": ["technology", "innovation", "solutions"],
                "key_sections": [
                    {"title": "About Us", "content": "We are a technology company...", "word_count": 150}
                ],
                "contact_information": {
                    "emails": ["contact@example.com"],
                    "phones": ["+1-555-123-4567"],
                    "urls": ["https://example.com/contact"]
                },
                "metadata": {"og:title": "Example Website"},
                "analysis_timestamp": 1692547200.0,
                "processing_time": 3.5
            }
        }

class ErrorResponse(BaseModel):
    """Standard error response"""
    error: str
    detail: str
    url: Optional[str] = None
    timestamp: float = Field(default_factory=lambda: datetime.now().timestamp())

class ValidationError(BaseModel):
    """Validation error details"""
    field: str
    message: str
    invalid_value: Any
```

#### Build & Test:
- **Build:** Integrate models throughout the application (0.5h)
- **Test:** Test data validation and serialization (1h)

---

## Phase 3: Security Implementation (4-5 hours)

### Task M1-SEC-01: URL Validation & SSRF Prevention
**Duration:** 2 hours | **Priority:** Critical | **Dependencies:** M1-DATA-01

#### Implementation Steps:
1. **Comprehensive URL Validator (src/utils/validators.py)**
```python
import re
import ipaddress
from urllib.parse import urlparse
from typing import List, Set
import logging

logger = logging.getLogger(__name__)

class URLValidator:
    def __init__(self):
        # Blocked private IP ranges (RFC 1918, RFC 4193, etc.)
        self.blocked_ip_ranges = [
            ipaddress.ip_network('10.0.0.0/8'),
            ipaddress.ip_network('172.16.0.0/12'),
            ipaddress.ip_network('192.168.0.0/16'),
            ipaddress.ip_network('127.0.0.0/8'),
            ipaddress.ip_network('169.254.0.0/16'),
            ipaddress.ip_network('::1/128'),
            ipaddress.ip_network('fc00::/7'),
            ipaddress.ip_network('fe80::/10'),
        ]
        
        # Blocked domains/hosts
        self.blocked_hosts = {
            'localhost',
            'metadata.google.internal',
            '169.254.169.254',  # AWS metadata
            'metadata.azure.com',  # Azure metadata
        }
        
        # Allowed schemes
        self.allowed_schemes = {'http', 'https'}
        
        # URL pattern validation
        self.url_pattern = re.compile(
            r'^https?://'  # http or https
            r'(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?'  # domain
            r'(?:/?|[/?]\S+)$', re.IGNORECASE)
    
    def validate_url(self, url: str) -> bool:
        """Comprehensive URL validation with SSRF prevention"""
        try:
            # Basic format validation
            if not self._validate_format(url):
                logger.warning(f"Invalid URL format: {url}")
                return False
            
            # Parse URL
            parsed = urlparse(url)
            
            # Validate scheme
            if not self._validate_scheme(parsed.scheme):
                logger.warning(f"Invalid scheme: {parsed.scheme}")
                return False
            
            # Validate host
            if not self._validate_host(parsed.hostname):
                logger.warning(f"Invalid or blocked host: {parsed.hostname}")
                return False
            
            # Check for blocked IPs
            if self._is_blocked_ip(parsed.hostname):
                logger.warning(f"Blocked IP address: {parsed.hostname}")
                return False
            
            # Additional security checks
            if not self._security_checks(url):
                logger.warning(f"Failed security checks: {url}")
                return False
            
            logger.info(f"URL validation passed: {url}")
            return True
            
        except Exception as e:
            logger.error(f"URL validation error for {url}: {str(e)}")
            return False
    
    def _validate_format(self, url: str) -> bool:
        """Validate basic URL format"""
        if not url or len(url) > 2048:
            return False
        
        # Check against regex pattern
        return bool(self.url_pattern.match(url))
    
    def _validate_scheme(self, scheme: str) -> bool:
        """Validate URL scheme"""
        return scheme.lower() in self.allowed_schemes
    
    def _validate_host(self, hostname: str) -> bool:
        """Validate hostname"""
        if not hostname:
            return False
        
        # Check blocked hosts
        if hostname.lower() in self.blocked_hosts:
            return False
        
        # Basic hostname format validation
        if len(hostname) > 253:
            return False
        
        # Check for obvious bypasses
        suspicious_patterns = [
            'localhost',
            '127.',
            '0.',
            '192.168.',
            '10.',
            '172.',
            'metadata',
            '[::]',
            '[::1]'
        ]
        
        hostname_lower = hostname.lower()
        for pattern in suspicious_patterns:
            if pattern in hostname_lower:
                return False
        
        return True
    
    def _is_blocked_ip(self, hostname: str) -> bool:
        """Check if hostname resolves to blocked IP"""
        try:
            # Try to parse as IP address directly
            ip = ipaddress.ip_address(hostname)
            
            # Check against blocked ranges
            for blocked_range in self.blocked_ip_ranges:
                if ip in blocked_range:
                    return True
                    
            return False
            
        except ValueError:
            # Not a direct IP address, would need DNS resolution
            # For security, we'll skip DNS resolution in validation
            # and rely on hostname checks
            return False
    
    def _security_checks(self, url: str) -> bool:
        """Additional security checks"""
        url_lower = url.lower()
        
        # Check for URL encoding bypasses
        suspicious_encoded = [
            '%7f',  # DEL character
            '%00',  # NULL byte
            '%0a',  # Line feed
            '%0d',  # Carriage return
            'localhost',
            '127.0.0.1',
            '::1',
        ]
        
        for encoded in suspicious_encoded:
            if encoded in url_lower:
                return False
        
        # Check for redirect bypasses
        if url_lower.count('://') > 1:
            return False
        
        return True

class InputValidator:
    """General input validation utilities"""
    
    @staticmethod
    def sanitize_text(text: str) -> str:
        """Sanitize text input"""
        if not text:
            return ""
        
        # Remove null bytes and control characters
        text = ''.join(char for char in text if ord(char) >= 32 or char in '\t\n\r')
        
        # Limit length
        return text[:10000]  # Max 10k characters
    
    @staticmethod
    def validate_options(options: dict) -> dict:
        """Validate and sanitize options dictionary"""
        if not isinstance(options, dict):
            return {}
        
        # Whitelist allowed option keys
        allowed_keys = {
            'timeout', 'user_agent', 'follow_redirects', 
            'max_content_size', 'extract_images'
        }
        
        sanitized = {}
        for key, value in options.items():
            if key in allowed_keys:
                # Type validation
                if key == 'timeout' and isinstance(value, (int, float)) and 0 < value <= 60:
                    sanitized[key] = value
                elif key == 'max_content_size' and isinstance(value, int) and 0 < value <= 50*1024*1024:
                    sanitized[key] = value
                elif key in ['follow_redirects', 'extract_images'] and isinstance(value, bool):
                    sanitized[key] = value
                elif key == 'user_agent' and isinstance(value, str) and len(value) <= 200:
                    sanitized[key] = InputValidator.sanitize_text(value)
        
        return sanitized
```

#### Build & Test:
- **Build:** No additional build steps needed (-)
- **Test:** Comprehensive security testing including SSRF attempts (1.5h)

---

### Task M1-SEC-02: Input Sanitization
**Duration:** 1 hour | **Priority:** Critical | **Dependencies:** M1-SEC-01

#### Implementation Steps:
1. **Content Sanitization (src/utils/security.py)**
```python
import html
import re
from typing import Any, Dict, List
import logging

logger = logging.getLogger(__name__)

class ContentSanitizer:
    def __init__(self):
        # Dangerous HTML tags to strip
        self.dangerous_tags = {
            'script', 'style', 'iframe', 'object', 'embed', 'form',
            'input', 'textarea', 'button', 'select', 'option'
        }
        
        # Dangerous attributes
        self.dangerous_attrs = {
            'onclick', 'onload', 'onerror', 'onmouseover', 'onfocus',
            'onblur', 'onchange', 'onsubmit', 'javascript:'
        }
    
    def sanitize_html_content(self, content: str) -> str:
        """Sanitize HTML content to prevent XSS"""
        if not content:
            return ""
        
        try:
            # Remove dangerous tags and their content
            for tag in self.dangerous_tags:
                pattern = rf'<{tag}\b[^>]*>.*?</{tag}>'
                content = re.sub(pattern, '', content, flags=re.IGNORECASE | re.DOTALL)
                # Also remove self-closing versions
                pattern = rf'<{tag}\b[^>]*/?>'
                content = re.sub(pattern, '', content, flags=re.IGNORECASE)
            
            # Remove dangerous attributes
            for attr in self.dangerous_attrs:
                pattern = rf'{attr}\s*=\s*["\'][^"\']*["\']'
                content = re.sub(pattern, '', content, flags=re.IGNORECASE)
            
            # Remove javascript: URLs
            content = re.sub(r'javascript:', '', content, flags=re.IGNORECASE)
            
            # Decode HTML entities
            content = html.unescape(content)
            
            return content
            
        except Exception as e:
            logger.error(f"Content sanitization failed: {str(e)}")
            return ""
    
    def sanitize_text_content(self, text: str) -> str:
        """Sanitize plain text content"""
        if not text:
            return ""
        
        # Remove control characters except common whitespace
        text = ''.join(char for char in text if ord(char) >= 32 or char in '\t\n\r')
        
        # Normalize whitespace
        text = re.sub(r'\s+', ' ', text)
        
        # Remove potentially dangerous patterns
        dangerous_patterns = [
            r'<script\b[^>]*>.*?</script>',
            r'javascript:',
            r'data:text/html',
            r'vbscript:',
        ]
        
        for pattern in dangerous_patterns:
            text = re.sub(pattern, '', text, flags=re.IGNORECASE | re.DOTALL)
        
        return text.strip()
    
    def validate_and_sanitize_metadata(self, metadata: Dict[str, Any]) -> Dict[str, Any]:
        """Validate and sanitize metadata dictionary"""
        if not isinstance(metadata, dict):
            return {}
        
        sanitized = {}
        for key, value in metadata.items():
            # Sanitize key
            if isinstance(key, str) and len(key) <= 100:
                clean_key = self.sanitize_text_content(key)
                
                # Sanitize value
                if isinstance(value, str):
                    clean_value = self.sanitize_text_content(value)
                    if len(clean_value) <= 1000:  # Limit metadata value length
                        sanitized[clean_key] = clean_value
                elif isinstance(value, (int, float, bool)):
                    sanitized[clean_key] = value
                elif isinstance(value, list):
                    # Sanitize list items
                    clean_list = []
                    for item in value[:10]:  # Limit list length
                        if isinstance(item, str):
                            clean_item = self.sanitize_text_content(item)
                            if clean_item and len(clean_item) <= 500:
                                clean_list.append(clean_item)
                    if clean_list:
                        sanitized[clean_key] = clean_list
        
        return sanitized

class SecurityHeaders:
    """Security-related HTTP headers management"""
    
    @staticmethod
    def get_security_headers() -> Dict[str, str]:
        """Get security headers for HTTP responses"""
        return {
            'X-Content-Type-Options': 'nosniff',
            'X-Frame-Options': 'DENY',
            'X-XSS-Protection': '1; mode=block',
            'Strict-Transport-Security': 'max-age=31536000; includeSubDomains',
            'Content-Security-Policy': "default-src 'self'; script-src 'none'; object-src 'none';",
            'Referrer-Policy': 'strict-origin-when-cross-origin'
        }
    
    @staticmethod
    def get_safe_request_headers() -> Dict[str, str]:
        """Get safe headers for outgoing requests"""
        return {
            'User-Agent': 'WebContentAnalyzer/1.0',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'DNT': '1',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1'
        }
```

#### Build & Test:
- **Build:** No additional build steps needed (-)
- **Test:** Test content sanitization with malicious inputs (1h)

---

### Task M1-SEC-03: Content Size Limits
**Duration:** 1 hour | **Priority:** High | **Dependencies:** M1-SEC-01

#### Implementation Steps:
1. **Size Limit Enforcement (src/utils/helpers.py)**
```python
import asyncio
from typing import Optional
import logging

logger = logging.getLogger(__name__)

class ContentSizeLimiter:
    def __init__(self):
        self.max_content_size = 10 * 1024 * 1024  # 10MB
        self.max_text_size = 5 * 1024 * 1024      # 5MB for text
        self.max_metadata_size = 100 * 1024       # 100KB for metadata
    
    async def check_response_size(self, response) -> bool:
        """Check if response size is within limits"""
        content_length = response.headers.get('content-length')
        if content_length:
            try:
                size = int(content_length)
                if size > self.max_content_size:
                    logger.warning(f"Content too large: {size} bytes")
                    return False
            except ValueError:
                pass
        return True
    
    def truncate_text_content(self, text: str, max_size: Optional[int] = None) -> str:
        """Truncate text content to size limit"""
        if not text:
            return ""
        
        limit = max_size or self.max_text_size
        
        # Convert to bytes to check actual size
        text_bytes = text.encode('utf-8')
        if len(text_bytes) <= limit:
            return text
        
        # Truncate at character boundary
        truncated_bytes = text_bytes[:limit]
        
        # Find last complete character
        while len(truncated_bytes) > 0:
            try:
                truncated_text = truncated_bytes.decode('utf-8')
                return truncated_text + "... [Content truncated]"
            except UnicodeDecodeError:
                truncated_bytes = truncated_bytes[:-1]
        
        return "[Content too large to display]"
    
    def validate_content_size(self, content: str) -> bool:
        """Validate if content is within size limits"""
        if not content:
            return True
        
        content_size = len(content.encode('utf-8'))
        return content_size <= self.max_content_size

class RateLimiter:
    """Simple rate limiting for requests"""
    
    def __init__(self, max_requests: int = 10, time_window: int = 60):
        self.max_requests = max_requests
        self.time_window = time_window
        self.requests = []
    
    async def check_rate_limit(self) -> bool:
        """Check if request is within rate limits"""
        import time
        now = time.time()
        
        # Remove old requests outside time window
        self.requests = [req_time for req_time in self.requests if now - req_time < self.time_window]
        
        # Check if under limit
        if len(self.requests) < self.max_requests:
            self.requests.append(now)
            return True
        
        logger.warning("Rate limit exceeded")
        return False

class ResourceMonitor:
    """Monitor system resources during processing"""
    
    @staticmethod
    def check_memory_usage() -> bool:
        """Check if memory usage is within acceptable limits"""
        try:
            import psutil
            memory = psutil.virtual_memory()
            if memory.percent > 90:  # 90% memory usage
                logger.warning(f"High memory usage: {memory.percent}%")
                return False
            return True
        except ImportError:
            # psutil not available, skip check
            return True
    
    @staticmethod
    async def timeout_handler(coro, timeout: int):
        """Handle timeouts for async operations"""
        try:
            return await asyncio.wait_for(coro, timeout=timeout)
        except asyncio.TimeoutError:
            logger.error(f"Operation timed out after {timeout} seconds")
            raise TimeoutError(f"Operation timed out after {timeout} seconds")
```

#### Build & Test:
- **Build:** No additional build steps needed (-)
- **Test:** Test size limits and resource monitoring (0.5h)

---

*This completes the detailed implementation plan for Milestone 1. The next phases (Service Layer, Presentation Layer, and Integration) would follow similar detailed breakdowns. Would you like me to continue with the remaining phases or would you prefer to start implementing based on this foundation?*
