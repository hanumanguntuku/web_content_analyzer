# 🌐 Web Content Analyzer

<div align="center">

![Python](https://img.shields.io/badge/Python-3.8%2B-blue?style=flat-square&logo=python)
![FastAPI](https://img.shields.io/badge/FastAPI-0.104%2B-green?style=flat-square&logo=fastapi)
![Streamlit](https://img.shields.io/badge/Streamlit-1.28%2B-red?style=flat-square&logo=streamlit)
![Docker](https://img.shields.io/badge/Docker-Supported-blue?style=flat-square&logo=docker)
![License](https://img.shields.io/badge/License-MIT-yellow?style=flat-square)

**Intelligent web content extraction and analysis platform with comprehensive security and performance monitoring.**

[🚀 Quick Start](#-quick-start) • [📖 Documentation](#-documentation) • [🧪 Testing](#-testing) • [🐳 Docker](#-docker-deployment) • [🤝 Contributing](#-contributing)

</div>

---

## 📋 Table of Contents

- [🎯 Overview](#-overview)
- [✨ Features](#-features)
- [🏗️ Architecture](#️-architecture)
- [🚀 Quick Start](#-quick-start)
- [📦 Installation](#-installation)
- [⚙️ Configuration](#️-configuration)
- [🏃‍♂️ Usage](#️-usage)
- [🧪 Testing](#-testing)
- [🐳 Docker Deployment](#-docker-deployment)
- [📊 API Documentation](#-api-documentation)
- [🔧 Development](#-development)
- [📝 Project Structure](#-project-structure)
- [🤝 Contributing](#-contributing)
- [📄 License](#-license)

---

## 🎯 Overview

The Web Content Analyzer is a sophisticated platform that extracts, processes, and analyzes web content with enterprise-grade security and performance monitoring. Built with **FastAPI** backend and **Streamlit** frontend, it provides intelligent content extraction, comprehensive analysis, and real-time insights.

### 🎨 Key Capabilities

- **🔍 Intelligent Content Extraction**: Advanced scraping with CMS pattern recognition
- **🛡️ Security-First Design**: SSRF prevention, XSS protection, and content sanitization
- **📊 Deep Content Analysis**: NLP-powered text processing with sentiment analysis
- **⚡ Performance Monitoring**: Real-time metrics and resource monitoring
- **🎯 User-Friendly Interface**: Interactive Streamlit frontend with visualizations
- **🏭 Production-Ready**: Docker deployment with monitoring and health checks

---

## ✨ Features

### 🔐 Security Features
- ✅ **SSRF Prevention**: Blocks access to private IP ranges and localhost
- ✅ **XSS Protection**: Comprehensive content sanitization
- ✅ **Rate Limiting**: Multi-tier rate limiting (per minute/hour/day)
- ✅ **Content Validation**: Size limits and malicious content detection
- ✅ **Input Sanitization**: URL validation and content filtering

### 🧠 Analysis Capabilities
- ✅ **Content Extraction**: Multi-strategy content extraction
- ✅ **Text Processing**: NLP analysis with keyword extraction
- ✅ **Sentiment Analysis**: Emotional tone detection
- ✅ **Quality Scoring**: Content quality assessment
- ✅ **Metadata Analysis**: Technical metadata extraction
- ✅ **Media Detection**: Image and media asset analysis

### 📈 Performance & Monitoring
- ✅ **Real-time Metrics**: Processing time and performance tracking
- ✅ **Resource Monitoring**: Memory and CPU usage tracking
- ✅ **Health Checks**: Service health monitoring
- ✅ **Error Handling**: Comprehensive error management
- ✅ **Logging**: Structured logging with multiple levels

### 🎨 User Interface
- ✅ **Interactive Dashboard**: Streamlit-based frontend
- ✅ **Real-time Progress**: Live progress tracking
- ✅ **Data Visualization**: Charts and metrics display
- ✅ **Export Options**: PDF and Excel report generation
- ✅ **Sample URLs**: Pre-configured test URLs

---

## 🏗️ Architecture

### **System Overview**
```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                           WEB CONTENT ANALYZER                                 │
│                          Full-Stack Architecture                               │
└─────────────────────────────────────────────────────────────────────────────────┘

┌──────────────────┐    HTTP/REST     ┌─────────────────┐    Internal      ┌──────────────────┐
│   Streamlit      │◄─────────────────►│   FastAPI       │◄─────────────────►│   Processing     │
│   Frontend       │     API Calls    │   Backend       │    Service       │   Engine         │
│   (Port 8501)    │                  │   (Port 8000)   │    Calls         │                  │
│                  │                  │                 │                  │                  │
│ ┌──────────────┐ │                  │ ┌─────────────┐ │                  │ ┌──────────────┐ │
│ │ Enhanced UI  │ │     JSON/HTTP    │ │ API Routes  │ │   Function       │ │ Web Scraper  │ │
│ │ Components   │ │ ◄─────────────── │ │ & Endpoints │ │   Calls          │ │ Service      │ │
│ └──────────────┘ │                  │ └─────────────┘ │                  │ └──────────────┘ │
│                  │                  │                 │                  │                  │
│ ┌──────────────┐ │                  │ ┌─────────────┐ │                  │ ┌──────────────┐ │
│ │ API Client   │ │     Progress     │ │ Security    │ │   Data           │ │ Content      │ │
│ │ with Retry   │ │ ◄─────────────── │ │ Layer       │ │   Processing     │ │ Extractor    │ │
│ └──────────────┘ │                  │ └─────────────┘ │                  │ └──────────────┘ │
│                  │                  │                 │                  │                  │
│ ┌──────────────┐ │                  │ ┌─────────────┐ │                  │ ┌──────────────┐ │
│ │ Progress     │ │     Real-time    │ │ Integrated  │ │   Pipeline       │ │ Text         │ │
│ │ Tracking     │ │ ◄─────────────── │ │ Analysis    │ │   Processing     │ │ Processor    │ │
│ └──────────────┘ │                  │ └─────────────┘ │                  │ └──────────────┘ │
│                  │                  │                 │                  │                  │
│ ┌──────────────┐ │                  │ ┌─────────────┐ │                  │ ┌──────────────┐ │
│ │ Results      │ │     Formatted    │ │ Response    │ │   Analyzed       │ │ Security     │ │
│ │ Visualization│ │ ◄─────────────── │ │ Handler     │ │   Data           │ │ Validator    │ │
│ └──────────────┘ │                  │ └─────────────┘ │                  │ └──────────────┘ │
└──────────────────┘                  └─────────────────┘                  └──────────────────┘
```

### **Connection Details**

#### **1. Frontend-Backend Connection**
- **Protocol**: HTTP/HTTPS REST API
- **Communication**: JSON request/response
- **Client**: Enhanced API client with retry logic
- **CORS**: Configured for cross-origin requests
- **Endpoints**: `/api/v1/analyze`, `/api/v1/status`, `/api/v1/health`

#### **2. Data Flow Architecture**
```
User Input → Frontend Validation → API Request → Security Layer → Content Processing → Response
```

#### **3. Service Communication**
- **Async Processing**: All operations are asynchronous
- **Error Handling**: Comprehensive error propagation
- **Progress Tracking**: Real-time status updates
- **Resource Management**: Rate limiting and resource monitoring

---

## 🔄 Request Flow Diagram

### **Complete Request Processing Flow**

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                              REQUEST FLOW                                      │
└─────────────────────────────────────────────────────────────────────────────────┘

FRONTEND (Streamlit)                 BACKEND (FastAPI)                PROCESSING ENGINE
┌────────────────┐                  ┌─────────────────┐               ┌─────────────────┐
│ 1. User Input  │                  │                 │               │                 │
│   - URL Entry  │                  │                 │               │                 │
│   - Options    │                  │                 │               │                 │
└────────┬───────┘                  │                 │               │                 │
         │                          │                 │               │                 │
┌────────▼───────┐                  │                 │               │                 │
│ 2. Frontend    │                  │                 │               │                 │
│   Validation   │                  │                 │               │                 │
│   - URL Format │                  │                 │               │                 │
│   - Security   │                  │                 │               │                 │
└────────┬───────┘                  │                 │               │                 │
         │                          │                 │               │                 │
┌────────▼───────┐     HTTP POST    │                 │               │                 │
│ 3. API Client  │ ─────────────────┤ 4. API Route    │               │                 │
│   - Build Req  │                  │   - /analyze    │               │                 │
│   - Add Headers│                  │   - Validation  │               │                 │
│   - Retry Logic│                  │   - IP Extract  │               │                 │
└────────────────┘                  └────────┬────────┘               │                 │
                                             │                        │                 │
                                    ┌────────▼────────┐               │                 │
                                    │ 5. Security     │               │                 │
                                    │   - SSRF Check  │               │                 │
                                    │   - Rate Limit  │               │                 │
                                    │   - Validation  │               │                 │
                                    └────────┬────────┘               │                 │
                                             │                        │                 │
                                    ┌────────▼────────┐   Service     │                 │
                                    │ 6. Analysis     │   Call        │                 │
                                    │   Service       │ ─────────────┤ 7. Web Scraper  │
                                    │   - Route Req   │               │   - HTTP Req    │
                                    │   - Orchestrate │               │   - Parse HTML  │
                                    └─────────────────┘               │   - Extract     │
                                                                      └────────┬────────┘
                                                                               │
                                                                      ┌────────▼────────┐
                                                                      │ 8. Content      │
                                                                      │   Processing    │
                                                                      │   - Clean Text  │
                                                                      │   - Keywords    │
                                                                      │   - Sentiment   │
                                                                      └────────┬────────┘
                                                                               │
                                                                      ┌────────▼────────┐
                                                                      │ 9. Security     │
                                                                      │   Sanitization  │
                                                                      │   - XSS Remove  │
                                                                      │   - Content Val │
                                                                      └────────┬────────┘
                                                                               │
┌────────────────┐    JSON Response │                               ┌────────▼────────┐
│ 12. Results    │ ◄────────────────┼──────────────────────────────┤ 10. Response    │
│    Display     │                  │                               │    Generation   │
│   - Charts     │                  │                               │   - Format JSON│
│   - Metrics    │                  │                               │   - Add Metrics│
│   - Export     │                  │                               │   - Error Handle│
└────────────────┘                  │                               └─────────────────┘
         ▲                          │                                         │
         │                          │                               ┌─────────▼─────────┐
┌────────┴───────┐    HTTP Response │                               │ 11. API Response  │
│ 11. Response   │ ◄────────────────┘                               │    - Send JSON    │
│    Processing  │                                                  │    - Status Code  │
│   - Parse JSON │                                                  │    - Headers      │
│   - Handle Err │                                                  │    - Timing       │
│   - Progress   │                                                  └───────────────────┘
└────────────────┘
```

---

## 🚀 Quick Start

### Prerequisites

- **Python 3.8+** 
- **Git**
- **Docker & Docker Compose** (optional, for containerized deployment)

### ⚡ 30-Second Setup

```bash
# Clone the repository
git clone https://github.com/hanumanguntuku/web_content_analyzer.git
cd web_content_analyzer

# Install dependencies
pip install -r requirements.txt

# Quick start with Python script
python start.py

# OR start manually:
# Terminal 1 - Backend
cd backend
python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000

# Terminal 2 - Frontend  
streamlit run frontend/enhanced_app.py --server.port 8501

# Access the application
# Frontend: http://localhost:8501
# Backend API: http://localhost:8000/docs
```

---

## 📦 Installation

### Option 1: Standard Installation

```bash
# 1. Clone the repository
git clone https://github.com/hanumanguntuku/web_content_analyzer.git
cd web_content_analyzer

# 2. Create virtual environment (recommended)
python -m venv venv

# Windows
.\venv\Scripts\activate

# macOS/Linux
source venv/bin/activate

# 3. Install dependencies
pip install --upgrade pip
pip install -r requirements.txt

# 4. Install development dependencies (optional)
pip install -r requirements-dev.txt
```

### Option 2: Docker Installation

```bash
# Clone and start with Docker
git clone https://github.com/hanumanguntuku/web_content_analyzer.git
cd web_content_analyzer

# Development environment
docker-compose up -d

# Production environment
docker-compose -f docker-compose.prod.yml up -d
```

### Option 3: Windows PowerShell Deployment

```powershell
# Use the automated deployment script
.\deploy.ps1 start

# Available commands:
# .\deploy.ps1 start     - Start all services
# .\deploy.ps1 stop      - Stop all services
# .\deploy.ps1 restart   - Restart services
# .\deploy.ps1 status    - Check service status
# .\deploy.ps1 logs      - View service logs
# .\deploy.ps1 test      - Run tests
# .\deploy.ps1 backup    - Create backup
```

---

## ⚙️ Configuration

### Environment Variables

Create a `.env` file in the project root:

```bash
# Application Settings
ENVIRONMENT=development
DEBUG=true
LOG_LEVEL=INFO

# API Configuration
API_HOST=0.0.0.0
API_PORT=8000
FRONTEND_PORT=8501

# Security Settings
RATE_LIMIT_REQUESTS=100
RATE_LIMIT_WINDOW=3600
MAX_CONTENT_SIZE=10485760
REQUEST_TIMEOUT=30

# Processing Settings
ENABLE_DEEP_ANALYSIS=true
MAX_CONCURRENT_REQUESTS=5
CACHE_ENABLED=true
CACHE_TTL=3600

# Monitoring
ENABLE_METRICS=true
HEALTH_CHECK_INTERVAL=30
```

### Advanced Configuration

```python
# backend/src/config.py
class Settings:
    # Security
    ssrf_protection: bool = True
    xss_protection: bool = True
    rate_limiting: bool = True
    
    # Performance
    max_workers: int = 5
    timeout_seconds: int = 30
    
    # Analysis
    deep_analysis: bool = True
    sentiment_analysis: bool = True
    keyword_extraction: bool = True
```

---

## 🏃‍♂️ Usage

### Web Interface

1. **Open the application**: Navigate to `http://localhost:8501`
2. **Enter URL**: Input the website URL you want to analyze
3. **Configure options**: Select analysis depth and features
4. **Start analysis**: Click "Analyze Content" button
5. **View results**: Explore the comprehensive analysis report

### API Usage

```python
import requests

# Analyze a URL
response = requests.post(
    "http://localhost:8000/api/v1/analyze",
    json={
        "url": "https://example.com",
        "deep_analysis": True,
        "include_metadata": True
    }
)

result = response.json()
print(f"Title: {result['title']}")
print(f"Summary: {result['summary']}")
print(f"Keywords: {result['keywords']}")
```

### Command Line Usage

```bash
# Run analysis via API
curl -X POST "http://localhost:8000/api/v1/analyze" \
     -H "Content-Type: application/json" \
     -d '{"url": "https://example.com", "deep_analysis": true}'

# Check service health
curl http://localhost:8000/api/v1/health

# Get API documentation
curl http://localhost:8000/docs
```

---

## 🧪 Testing

### Run All Tests

```bash
# Run comprehensive test suite
python test_milestone1_integration.py

# Run with coverage
pytest --cov=backend --cov=frontend --cov-report=html

# Run specific test categories
python -m pytest tests/test_security.py
python -m pytest tests/test_performance.py
```

### Test Categories

- **🔒 Security Tests**: SSRF, XSS, rate limiting
- **⚡ Performance Tests**: Load testing, memory usage
- **🧩 Integration Tests**: End-to-end workflows
- **🎯 Unit Tests**: Individual component testing
- **🔧 API Tests**: Endpoint validation

### Manual Testing

```bash
# Test URLs for validation
python -c "
from backend.src.services.integrated_analysis_service import IntegratedAnalysisService
import asyncio

async def test():
    service = IntegratedAnalysisService()
    result = await service.analyze_content('https://httpbin.org/html', '127.0.0.1')
    print(f'Analysis completed: {result.title}')

asyncio.run(test())
"

# OR test the API directly
curl -X POST http://localhost:8000/api/v1/analyze \
  -H "Content-Type: application/json" \
  -d '{"url": "https://httpbin.org/html", "deep_analysis": true}'
```

---

## 🐳 Docker Deployment

### Development Deployment

```bash
# Start development environment
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

### Production Deployment

```bash
# Production with monitoring
docker-compose -f docker-compose.prod.yml up -d

# Includes:
# - Nginx reverse proxy
# - Redis caching
# - Prometheus monitoring
# - Health checks
```

### Docker Services

| Service | Port | Description |
|---------|------|-------------|
| `frontend` | 8501 | Streamlit web interface |
| `backend` | 8000 | FastAPI REST API |
| `nginx` | 80, 443 | Reverse proxy (production) |
| `redis` | 6379 | Caching layer (production) |
| `prometheus` | 9090 | Metrics monitoring (production) |

---

## 📊 API Documentation

### Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/api/v1/analyze` | Analyze web content |
| `GET` | `/api/v1/health` | Service health check |
| `GET` | `/api/v1/stats` | Usage statistics |
| `GET` | `/docs` | Interactive API documentation |
| `GET` | `/redoc` | Alternative API documentation |

### Request Example

```json
{
  "url": "https://example.com",
  "deep_analysis": true,
  "include_metadata": true,
  "extract_keywords": true,
  "sentiment_analysis": true
}
```

### Response Example

```json
{
  "url": "https://example.com",
  "title": "Example Website",
  "summary": "Content summary...",
  "keywords": ["web", "content", "analysis"],
  "sentiment": {
    "score": 0.75,
    "label": "positive"
  },
  "metadata": {
    "word_count": 1250,
    "processing_time": 2.34,
    "quality_score": 0.85
  },
  "status": "completed"
}
```

---

## 🔧 Development

### Setup Development Environment

```bash
# Install development dependencies
pip install -r requirements-dev.txt

# Install pre-commit hooks
pre-commit install

# Run code formatting
black .
isort .
flake8 .
```

### Development Workflow

1. **Create feature branch**: `git checkout -b feature/new-feature`
2. **Write tests**: Add tests for new functionality
3. **Implement feature**: Write code following style guidelines
4. **Run tests**: Ensure all tests pass
5. **Submit PR**: Create pull request for review

### Code Style

- **Python**: Black formatting, isort imports, flake8 linting
- **Documentation**: Google-style docstrings
- **Testing**: pytest with >90% coverage
- **Security**: Bandit security scanning

---

## 📝 Project Structure

```
web_content_analyzer/
├── 📁 backend/                    # FastAPI Backend
│   ├── 📁 src/
│   │   ├── 📁 api/               # API routes and endpoints
│   │   ├── 📁 services/          # Business logic services
│   │   ├── 📁 models/            # Data models and schemas
│   │   ├── 📁 utils/             # Utility functions
│   │   ├── 📁 scrapers/          # Web scraping components
│   │   └── 📁 processors/        # Content processing
│   └── 📄 requirements.txt       # Backend dependencies
│
├── 📁 frontend/                   # Streamlit Frontend
│   ├── 📁 src/
│   │   ├── 📁 components/        # UI components
│   │   └── 📁 services/          # Frontend services
│   ├── 📄 enhanced_app.py        # Main Streamlit app (enhanced)
│   └── 📄 requirements.txt       # Frontend dependencies
│
├── 📁 tests/                     # Test suite
│   ├── 📄 test_milestone1_integration.py
│   └── 📁 unit/                  # Unit tests
│
├── 📁 nginx/                     # Nginx configuration
├── 📁 assets/                    # Static assets
├── 📁 requirements/              # Documentation
│
├── 📄 docker-compose.yml         # Development Docker setup
├── 📄 docker-compose.prod.yml    # Production Docker setup
├── 📄 deploy.ps1                 # Windows deployment script
├── 📄 requirements.txt           # Complete dependencies
├── 📄 requirements-dev.txt       # Development dependencies
├── 📄 .env.example              # Environment template
└── 📄 README.md                 # This file
```

---

## 🚨 Troubleshooting

### Common Issues

#### 🔍 **Port Already in Use**
```bash
# Find and kill process using port
netstat -ano | findstr :8501
taskkill /PID <process_id> /F
```

#### 🔍 **Dependencies Issues**
```bash
# Clean install
pip uninstall -r requirements.txt -y
pip install -r requirements.txt
```

#### 🔍 **Docker Issues**
```bash
# Clean Docker environment
docker-compose down -v
docker system prune -f
docker-compose up -d --build
```

#### 🔍 **Permission Issues**
```bash
# Windows: Run as Administrator
# Linux/macOS: Check file permissions
chmod +x deploy.ps1
```

### Performance Optimization

- **Increase worker processes**: Modify `MAX_WORKERS` in configuration
- **Enable caching**: Set `CACHE_ENABLED=true`
- **Optimize memory**: Adjust `MAX_CONTENT_SIZE`
- **Monitor resources**: Use built-in monitoring dashboard

---

## 📈 Monitoring & Metrics

### Health Checks
- **Backend**: `http://localhost:8000/health`
- **Frontend**: `http://localhost:8501`
- **System**: Resource monitoring dashboard

### Key Metrics
- **Response Time**: Average processing time
- **Success Rate**: Successful analysis percentage
- **Resource Usage**: CPU and memory consumption
- **Error Rate**: Failed request percentage

---

## 🎯 Roadmap

### ✅ Milestone 1: Intelligent Content Processing (Completed)
- Content extraction and analysis
- Security implementation
- Frontend interface
- Testing and deployment

### 🚧 Milestone 2: AI Integration (Planned)
- LLM integration for content analysis
- Advanced NLP processing
- Semantic analysis
- Content classification

### 🔮 Milestone 3: Advanced Features (Future)
- Multi-language support
- Batch processing
- API key management
- Advanced analytics

---

## 🤝 Contributing

We welcome contributions! Please follow these guidelines:

### How to Contribute

1. **Fork the repository**
2. **Create feature branch**: `git checkout -b feature/amazing-feature`
3. **Write tests** for your changes
4. **Commit changes**: `git commit -m "Add amazing feature"`
5. **Push to branch**: `git push origin feature/amazing-feature`
6. **Open Pull Request**

### Contribution Guidelines

- ✅ Write comprehensive tests
- ✅ Follow code style guidelines
- ✅ Update documentation
- ✅ Add security considerations
- ✅ Include performance impact analysis

### Development Standards

- **Code Coverage**: Minimum 90%
- **Documentation**: All public APIs documented
- **Security**: Security review required
- **Performance**: No significant performance regression

---

## 📞 Support

### Getting Help

- **📖 Documentation**: Check this README and inline documentation
- **🐛 Issues**: Create GitHub issue for bugs
- **💡 Features**: Discuss feature requests in issues
- **💬 Questions**: Use GitHub discussions

### Contact

- **Repository**: [web_content_analyzer](https://github.com/hanumanguntuku/web_content_analyzer)
- **Issues**: [GitHub Issues](https://github.com/hanumanguntuku/web_content_analyzer/issues)
- **Discussions**: [GitHub Discussions](https://github.com/hanumanguntuku/web_content_analyzer/discussions)

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 🙏 Acknowledgments

- **FastAPI**: High-performance web framework
- **Streamlit**: Excellent frontend framework
- **BeautifulSoup**: Powerful HTML parsing
- **NLTK**: Natural language processing
- **Docker**: Containerization platform

---

<div align="center">

**🌟 Star this repository if you find it helpful! 🌟**

[![Stars](https://img.shields.io/github/stars/hanumanguntuku/web_content_analyzer?style=social)](https://github.com/hanumanguntuku/web_content_analyzer/stargazers)
[![Forks](https://img.shields.io/github/forks/hanumanguntuku/web_content_analyzer?style=social)](https://github.com/hanumanguntuku/web_content_analyzer/network/members)
[![Issues](https://img.shields.io/github/issues/hanumanguntuku/web_content_analyzer)](https://github.com/hanumanguntuku/web_content_analyzer/issues)

---

**Made with ❤️ by the Web Content Analyzer Team**

*Empowering intelligent content analysis with security and performance in mind.*

</div> 
