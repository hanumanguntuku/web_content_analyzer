# 🤝 Contributing to Web Content Analyzer

Thank you for your interest in contributing to the Web Content Analyzer! This document provides guidelines and information for contributors.

## 📋 Table of Contents

- [🎯 Ways to Contribute](#-ways-to-contribute)
- [🚀 Getting Started](#-getting-started)
- [🔧 Development Setup](#-development-setup)
- [📝 Code Style Guidelines](#-code-style-guidelines)
- [🧪 Testing Requirements](#-testing-requirements)
- [🔒 Security Guidelines](#-security-guidelines)
- [📖 Documentation Standards](#-documentation-standards)
- [🚢 Pull Request Process](#-pull-request-process)
- [🐛 Bug Reports](#-bug-reports)
- [💡 Feature Requests](#-feature-requests)
- [👥 Community Guidelines](#-community-guidelines)

## 🎯 Ways to Contribute

### 🐛 Bug Fixes
- Report bugs through GitHub issues
- Fix existing bugs in the issue tracker
- Improve error handling and edge cases

### ✨ New Features
- Implement features from the roadmap
- Propose and implement new functionality
- Enhance existing features

### 📚 Documentation
- Improve README and documentation
- Add code comments and docstrings
- Create tutorials and examples

### 🧪 Testing
- Add unit tests for new features
- Improve test coverage
- Add integration tests

### 🎨 UI/UX Improvements
- Enhance the Streamlit frontend
- Improve user experience
- Add visualizations and charts

### ⚡ Performance
- Optimize processing algorithms
- Improve memory usage
- Enhance caching strategies

## 🚀 Getting Started

### Prerequisites
- Python 3.8+
- Git
- Basic knowledge of FastAPI and Streamlit
- Understanding of web scraping concepts

### First Contribution
1. **Look for "good first issue" labels** in the issue tracker
2. **Read the codebase** to understand the architecture
3. **Join discussions** in GitHub Discussions
4. **Ask questions** if you need clarification

## 🔧 Development Setup

### 1. Fork and Clone
```bash
# Fork the repository on GitHub
# Clone your fork
git clone https://github.com/YOUR_USERNAME/web_content_analyzer.git
cd web_content_analyzer

# Add upstream remote
git remote add upstream https://github.com/hanumanguntuku/web_content_analyzer.git
```

### 2. Environment Setup
```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows
.\venv\Scripts\activate
# macOS/Linux
source venv/bin/activate

# Install dependencies
pip install -r requirements-dev.txt

# Install pre-commit hooks
pre-commit install
```

### 3. Development Environment
```bash
# Start backend
cd backend
python -m uvicorn src.main:app --reload --host 0.0.0.0 --port 8000

# Start frontend (in new terminal)
cd frontend
streamlit run app.py --server.port 8501
```

### 4. Verify Setup
```bash
# Run tests
python test_milestone1_integration.py

# Check code style
black --check .
flake8 .
isort --check-only .
```

## 📝 Code Style Guidelines

### Python Code Style
We follow **PEP 8** with some modifications:

```python
# Use Black for formatting (line length: 88)
black .

# Use isort for import sorting
isort .

# Use flake8 for linting
flake8 .
```

### Naming Conventions
```python
# Classes: PascalCase
class ContentAnalyzer:
    pass

# Functions and variables: snake_case
def analyze_content():
    pass

user_input = "example"

# Constants: UPPER_SNAKE_CASE
MAX_CONTENT_SIZE = 10485760

# Private methods: leading underscore
def _private_method():
    pass
```

### Documentation Style
```python
def analyze_content(url: str, deep_analysis: bool = True) -> AnalysisReport:
    """
    Analyze web content from the given URL.
    
    Args:
        url: The URL to analyze
        deep_analysis: Whether to perform deep analysis
        
    Returns:
        AnalysisReport: Comprehensive analysis results
        
    Raises:
        ValidationError: If URL is invalid
        ScrapingException: If content cannot be retrieved
        
    Example:
        >>> analyzer = ContentAnalyzer()
        >>> result = analyzer.analyze_content("https://example.com")
        >>> print(result.title)
    """
    pass
```

## 🧪 Testing Requirements

### Test Coverage
- **Minimum coverage**: 90%
- **New features**: Must include tests
- **Bug fixes**: Must include regression tests

### Test Types

#### Unit Tests
```python
# tests/unit/test_content_processor.py
import pytest
from backend.src.processors.text_processor import TextProcessor

def test_extract_keywords():
    processor = TextProcessor()
    text = "This is a sample text for keyword extraction"
    keywords = processor.extract_keywords(text)
    assert len(keywords) > 0
    assert isinstance(keywords, list)
```

#### Integration Tests
```python
# tests/integration/test_api.py
import pytest
from fastapi.testclient import TestClient
from backend.src.main import app

client = TestClient(app)

def test_analyze_endpoint():
    response = client.post(
        "/api/v1/analyze",
        json={"url": "https://httpbin.org/html"}
    )
    assert response.status_code == 200
    assert "title" in response.json()
```

#### Security Tests
```python
# tests/security/test_ssrf_protection.py
def test_ssrf_prevention():
    # Test that private IPs are blocked
    dangerous_urls = [
        "http://localhost:8080",
        "http://127.0.0.1",
        "http://192.168.1.1"
    ]
    for url in dangerous_urls:
        with pytest.raises(SecurityException):
            validator.validate_url(url)
```

### Running Tests
```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=backend --cov=frontend --cov-report=html

# Run specific test file
pytest tests/unit/test_content_processor.py

# Run tests with markers
pytest -m "security"
pytest -m "integration"
```

## 🔒 Security Guidelines

### Security First Approach
- **Validate all inputs** before processing
- **Sanitize outputs** to prevent XSS
- **Implement rate limiting** for all endpoints
- **Use HTTPS** in production
- **Never log sensitive data**

### Security Checklist
- [ ] Input validation implemented
- [ ] SSRF protection in place
- [ ] XSS protection applied
- [ ] Rate limiting configured
- [ ] Error messages don't leak information
- [ ] Dependencies scanned for vulnerabilities

### Security Testing
```python
# Example security test
def test_xss_protection():
    malicious_content = "<script>alert('xss')</script>"
    sanitized = content_sanitizer.sanitize(malicious_content)
    assert "<script>" not in sanitized
    assert "alert" not in sanitized
```

## 📖 Documentation Standards

### Code Documentation
- **All public functions** must have docstrings
- **Complex algorithms** need inline comments
- **API endpoints** must be documented
- **Configuration options** need descriptions

### README Updates
When adding features:
- Update feature list
- Add usage examples
- Update installation instructions if needed
- Add troubleshooting steps if applicable

### API Documentation
```python
from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter()

class AnalysisRequest(BaseModel):
    """Request model for content analysis."""
    url: str = Field(..., description="URL to analyze")
    deep_analysis: bool = Field(default=True, description="Enable deep analysis")

@router.post("/analyze", response_model=AnalysisReport)
async def analyze_content(request: AnalysisRequest):
    """
    Analyze web content from the specified URL.
    
    - **url**: The website URL to analyze
    - **deep_analysis**: Whether to perform comprehensive analysis
    
    Returns comprehensive analysis including:
    - Content extraction
    - Keyword analysis
    - Sentiment analysis
    - Technical metadata
    """
    pass
```

## 🚢 Pull Request Process

### Before Submitting
1. **Sync with upstream**
   ```bash
   git fetch upstream
   git checkout main
   git merge upstream/main
   ```

2. **Create feature branch**
   ```bash
   git checkout -b feature/your-feature-name
   ```

3. **Make changes**
   - Write code following style guidelines
   - Add tests for new functionality
   - Update documentation

4. **Test your changes**
   ```bash
   # Run tests
   pytest
   
   # Check code style
   black --check .
   flake8 .
   
   # Run security checks
   bandit -r backend/
   ```

### Pull Request Template
When creating a PR, include:

```markdown
## 📝 Description
Brief description of changes

## 🎯 Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Documentation update
- [ ] Performance improvement
- [ ] Refactoring

## 🧪 Testing
- [ ] Unit tests added/updated
- [ ] Integration tests added/updated
- [ ] Manual testing completed

## 📋 Checklist
- [ ] Code follows style guidelines
- [ ] Self-review completed
- [ ] Documentation updated
- [ ] No breaking changes (or properly documented)

## 🔗 Related Issues
Fixes #123
```

### Review Process
1. **Automated checks** must pass
2. **Code review** by maintainers
3. **Testing** on multiple environments
4. **Documentation review**
5. **Security review** (if applicable)

## 🐛 Bug Reports

### Before Reporting
1. **Search existing issues** for duplicates
2. **Test with latest version**
3. **Check documentation** for solutions

### Bug Report Template
```markdown
## 🐛 Bug Description
Clear description of the bug

## 🔄 Steps to Reproduce
1. Go to '...'
2. Click on '...'
3. See error

## 🎯 Expected Behavior
What should happen

## 📊 Actual Behavior
What actually happens

## 🌍 Environment
- OS: [e.g. Windows 10, macOS, Ubuntu]
- Python version: [e.g. 3.9.5]
- Browser: [e.g. Chrome 91.0]

## 📷 Screenshots
If applicable, add screenshots

## 📋 Additional Context
Any other context about the problem
```

## 💡 Feature Requests

### Feature Request Template
```markdown
## 🚀 Feature Description
Clear description of the requested feature

## 🎯 Problem Statement
What problem does this solve?

## 💡 Proposed Solution
How should this feature work?

## 🔄 Alternatives Considered
Other solutions you've considered

## 📊 Additional Context
Screenshots, mockups, examples
```

## 👥 Community Guidelines

### Code of Conduct
- **Be respectful** and inclusive
- **Provide constructive feedback**
- **Help newcomers** get started
- **Follow GitHub's community guidelines**

### Communication
- **Use clear, descriptive titles** for issues and PRs
- **Provide context** and examples
- **Be patient** with review process
- **Ask questions** when unclear

### Recognition
Contributors will be recognized in:
- README acknowledgments
- Release notes
- Contributor spotlight

## 🏆 Development Milestones

### Milestone 1: ✅ Intelligent Content Processing (Completed)
- Basic content extraction
- Security implementation
- Frontend interface

### Milestone 2: 🚧 AI Integration (In Progress)
- LLM integration
- Advanced NLP
- Content classification

### Milestone 3: 🔮 Advanced Features (Planned)
- Multi-language support
- Batch processing
- Advanced analytics

## 📞 Getting Help

### Resources
- **Documentation**: README.md and inline docs
- **Discussions**: GitHub Discussions
- **Issues**: GitHub Issues
- **Code examples**: tests/ directory

### Contact
- **Questions**: Use GitHub Discussions
- **Bugs**: Create GitHub Issues
- **Security**: Email maintainers privately

---

## 🙏 Thank You!

Your contributions make this project better for everyone. Whether you're fixing bugs, adding features, improving documentation, or helping others, every contribution is valuable and appreciated!

**Happy coding! 🚀**
