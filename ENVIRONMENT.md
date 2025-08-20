# Environment Configuration

This application uses environment variables for configuration, following standard practices for web applications.

## Frontend Configuration

The frontend supports the following environment variables:

### BACKEND_URL
- **Description**: URL of the backend API server
- **Default**: `http://localhost:8000`
- **Example**: `export BACKEND_URL=https://api.myapp.com`

## Backend Configuration

The backend uses Pydantic Settings which automatically reads from environment variables:

### Server Configuration
- `HOST` - Server host (default: 0.0.0.0)
- `PORT` - Server port (default: 8000)
- `DEBUG` - Debug mode (default: False)

### Security Configuration
- `ALLOWED_ORIGINS` - CORS allowed origins
- `MAX_CONTENT_SIZE` - Maximum content size in bytes
- `REQUEST_TIMEOUT` - Request timeout in seconds

## Usage Examples

### Development (Default)
```bash
# Use defaults - no environment variables needed
python -m streamlit run app.py --server.port 8501
python -m uvicorn main:app --host 0.0.0.0 --port 8000
```

### Production
```bash
# Set environment variables
export BACKEND_URL=https://api.production.com
export DEBUG=false
export ALLOWED_ORIGINS=["https://app.production.com"]

# Run services
python -m streamlit run app.py --server.port 8501
python -m uvicorn main:app --host 0.0.0.0 --port 8000
```

### Docker
```yaml
# docker-compose.yml
services:
  frontend:
    environment:
      - BACKEND_URL=http://backend:8000
  backend:
    environment:
      - DEBUG=false
      - ALLOWED_ORIGINS=["http://frontend:8501"]
```

## Benefits

✅ **No secrets files required** - Works out of the box
✅ **Standard practice** - Uses environment variables like most web apps
✅ **Docker friendly** - Easy to configure in containers
✅ **Security** - Sensitive data stays out of source code
✅ **Flexibility** - Different configs for dev/staging/prod
