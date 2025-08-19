# Web Content Analyzer

A complete web content analysis system with FastAPI backend and Streamlit frontend that extracts content from any website URL and generates comprehensive analysis reports.

## Project Structure

```
project_root/
├── backend/                      # FastAPI Backend
│   ├── src/
│   │   ├── api/                  # API endpoints
│   │   ├── services/             # Business logic
│   │   ├── scrapers/             # Web scraping
│   │   ├── processors/           # Content processing
│   │   ├── models/               # Data models
│   │   └── utils/                # Utilities & security
│   ├── config/                   # Configuration
│   ├── tests/                    # Backend tests
│   ├── requirements.txt
│   └── Dockerfile
└── frontend/                     # Streamlit Frontend
    ├── streamlit_app.py          # Main UI application
    ├── requirements.txt
    └── README.md
```

## Features

### Backend (FastAPI)
- 🕷️ **Web Scraping**: BeautifulSoup + requests with anti-detection
- 🔒 **Security**: SSRF prevention, content sanitization
- 🤖 **AI-Ready**: Structured output formats for AI analysis
- 📊 **Content Processing**: Text extraction, summarization, keywords
- 🐳 **Docker Ready**: Container support

### Frontend (Streamlit)
- 🖥️ **User Interface**: Clean, intuitive web interface
- 📊 **Results Visualization**: Formatted display of analysis results
- 🏷️ **Keyword Tags**: Visual keyword representation
- ⚙️ **Configuration**: Backend connection settings
- 📱 **Responsive**: Works on desktop and mobile

## Quick Start

### Prerequisites
- Python 3.8+ installed
- Git (optional, for cloning)

### Option 1: Quick Setup (Recommended)

1. **Clone or Download the Project**:
```powershell
# If using git
git clone <repository-url>
cd web_content_analyzer

# Or download and extract the ZIP file
```

2. **Create Virtual Environment** (Recommended):
```powershell
python -m venv .venv
.venv\Scripts\activate  # Windows
# source .venv/bin/activate  # Linux/Mac
```

3. **Install Backend Dependencies**:
```powershell
cd project_root\backend
pip install -r requirements.txt
```

4. **Install Frontend Dependencies**:
```powershell
cd ..\frontend
pip install -r requirements.txt
```

5. **Start the Application**:

**Terminal 1 - Backend**:
```powershell
cd project_root\backend
uvicorn src.main:app --reload
```

**Terminal 2 - Frontend**:
```powershell
cd project_root\frontend
streamlit run streamlit_app.py
```

6. **Access the Application**:
   - **Frontend UI**: http://localhost:8501
   - **Backend API**: http://localhost:8000
   - **API Documentation**: http://localhost:8000/docs

### Option 2: Step-by-Step Setup

#### Backend Setup
1. **Navigate to Backend**:
```powershell
cd project_root\backend
```

2. **Create Virtual Environment** (Optional):
```powershell
python -m venv backend_venv
backend_venv\Scripts\activate
```

3. **Install Dependencies**:
```powershell
pip install -r requirements.txt
```

4. **Start Backend Server**:
```powershell
uvicorn src.main:app --reload
```

5. **Verify Backend** (Open http://localhost:8000/docs):
```json
GET /health → {"status": "ok"}
```

#### Frontend Setup
1. **Open New Terminal** and navigate to Frontend:
```powershell
cd project_root\frontend
```

2. **Install Dependencies**:
```powershell
pip install -r requirements.txt
```

3. **Start Frontend**:
```powershell
streamlit run streamlit_app.py
```

4. **Access Frontend**: http://localhost:8501

### Troubleshooting

#### Common Issues

**❌ "Module not found" errors**:
```powershell
# Ensure you're in the correct directory
cd project_root\backend  # for backend
cd project_root\frontend  # for frontend

# Reinstall dependencies
pip install -r requirements.txt

# If still having issues, try upgrading pip first
python -m pip install --upgrade pip
pip install -r requirements.txt
```

**❌ "Port already in use"**:
```powershell
# Backend (port 8000)
uvicorn src.main:app --reload --port 8001

# Frontend (port 8501)
streamlit run streamlit_app.py --server.port 8502
```

**❌ Backend connection failed**:
1. Ensure backend is running on http://localhost:8000
2. Check backend terminal for errors
3. Use "Test Connection" button in frontend sidebar

**❌ Virtual environment issues**:
```powershell
# Deactivate and recreate
deactivate
rmdir /s .venv
python -m venv .venv
.venv\Scripts\activate
```

#### Development Mode

**Backend with auto-reload**:
```powershell
cd project_root\backend
uvicorn src.main:app --reload --host 0.0.0.0 --port 8000
```

**Frontend with auto-reload**:
```powershell
cd project_root\frontend
streamlit run streamlit_app.py --server.runOnSave true
```

### Testing the Installation

1. **Backend Test**:
```powershell
curl http://localhost:8000/health
# Expected: {"status":"ok"}
```

2. **Frontend Test**:
   - Open http://localhost:8501
   - Enter URL: `https://www.bbc.com/news`
   - Click "Analyze Content"
   - Should see progress bar and results

3. **Integration Test**:
   - Use frontend sidebar "Test Connection"
   - Should show "✅ Backend connected!"

### Docker Setup (Optional)

**Backend Docker**:
```powershell
cd project_root\backend
docker build -t web-analyzer-backend .
docker run -p 8000:8000 web-analyzer-backend
```

### Project Structure
```
web_content_analyzer/
├── project_root/
│   ├── backend/                 # FastAPI Backend
│   │   ├── src/                # Source code
│   │   ├── requirements.txt    # Backend dependencies
│   │   └── Dockerfile         # Container definition
│   └── frontend/              # Streamlit Frontend
│       ├── streamlit_app.py   # Main UI application
│       └── requirements.txt   # Frontend dependencies
└── README.md                  # This file
```

## Usage

1. Open the Streamlit interface at http://localhost:8501
2. Enter a URL in the input field
3. Click "Analyze Content"
4. View results including summary, keywords, and metrics

## API Usage

Direct API calls to the backend:

```bash
curl -X POST "http://localhost:8000/analyze" \
     -H "Content-Type: application/json" \
     -d '{"url": "https://example.com"}'
``` 
