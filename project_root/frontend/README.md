# Web Content Analyzer - Frontend

A modular Streamlit-based frontend for the Web Content Analyzer application.

## Architecture

The frontend follows a modular architecture with clear separation of concerns:

```
frontend/
├── app.py                    # Main application entry point
├── src/                      # Source code
│   ├── components/          # UI Components
│   │   ├── url_input.py     # URL input and validation
│   │   ├── results_display.py # Results visualization
│   │   └── progress.py      # Progress indicators
│   ├── services/            # Frontend Services
│   │   ├── api_client.py    # Backend API client
│   │   └── state_manager.py # Streamlit state management
│   └── utils/               # Utilities
│       ├── formatters.py    # Content formatting
│       └── validators.py    # Input validation
├── assets/                  # Static assets
│   └── styles.css          # Custom CSS styles
├── templates/               # HTML templates
│   └── report_template.html # Report generation template
├── requirements.txt         # Python dependencies
└── Dockerfile              # Container configuration
```

## Features

### Components
- **URL Input Component**: Handles URL input, validation, and example URLs
- **Results Display Component**: Shows analysis results with metrics, keywords, and insights
- **Progress Component**: Provides visual feedback during analysis

### Services
- **API Client**: Manages communication with the backend API
- **State Manager**: Handles Streamlit session state management

### Utilities
- **Validators**: URL and input validation functions
- **Formatters**: Content formatting and visualization helpers

## Installation

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Run the application:**
   ```bash
   streamlit run app.py
   ```

3. **Or run on a specific port:**
   ```bash
   streamlit run app.py --server.port=8503
   ```

## Configuration

The frontend can be configured through the sidebar:

- **Backend URL**: Set the backend API endpoint (default: http://localhost:8000)
- **Connection Test**: Test connectivity to the backend

## Usage

1. **Enter a URL** in the input field
2. **Validate** - The system provides real-time URL validation
3. **Analyze** - Click "Analyze Content" to start the analysis
4. **View Results** - See detailed metrics, summary, and keywords
5. **Export** - Download results as JSON or copy summary

## API Integration

The frontend communicates with the backend through these endpoints:

- `GET /health` - Health check
- `POST /analyze` - Content analysis

## Error Handling

The application provides comprehensive error handling:

- **Connection errors** - Backend connectivity issues
- **Timeout errors** - Long-running analysis requests
- **Validation errors** - Invalid URL formats
- **HTTP errors** - Backend API errors

## Development

### Running in Development Mode

```bash
cd frontend
streamlit run app.py --server.port=8503
```

### Adding New Components

1. Create the component in `src/components/`
2. Import and use in `app.py`
3. Add any utilities to `src/utils/`

### Styling

Custom styles are defined in `assets/styles.css` and can be loaded into Streamlit components.

## Docker Deployment

Build and run with Docker:

```bash
docker build -t web-content-analyzer-frontend .
docker run -p 8501:8501 web-content-analyzer-frontend
```

## Testing

The modular architecture makes testing easier:

- **Components** can be tested independently
- **Services** can be mocked for testing
- **Utilities** have pure functions for easy testing

## Performance

- **Modular loading** - Only necessary components are loaded
- **State management** - Efficient session state handling
- **Progress indicators** - User feedback during long operations

## Browser Compatibility

Tested on:
- Chrome 115+
- Firefox 115+
- Safari 16+
- Edge 115+

## Contributing

1. Follow the modular architecture
2. Add new components to appropriate directories
3. Include type hints and docstrings
4. Test components independently

## Troubleshooting

### Common Issues

1. **Import errors**: Ensure all `__init__.py` files are present
2. **Backend connection**: Check backend URL in sidebar
3. **Port conflicts**: Use different port with `--server.port`

### Debug Mode

Enable debug mode in development:

```bash
streamlit run app.py --logger.level=debug
```
