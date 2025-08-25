"""
API Client Service for Backend Communication
Handles all HTTP requests to the FastAPI backend
"""
import requests
import streamlit as st
from typing import Dict, Any, Optional, List
import logging
import time

logger = logging.getLogger(__name__)

class APIClient:
    """Client for communicating with the Web Content Analyzer backend API"""
    
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url.rstrip('/')
        self.timeout = 30
        self.session = requests.Session()
        
        # Set default headers
        self.session.headers.update({
            'Content-Type': 'application/json',
            'User-Agent': 'WebContentAnalyzer-Frontend/1.0.0'
        })
        
        logger.info(f"APIClient initialized with base_url: {self.base_url}")
    
    def _make_request(
        self, 
        method: str, 
        endpoint: str, 
        data: Optional[Dict] = None,
        params: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """Make HTTP request to the backend API"""
        url = f"{self.base_url}{endpoint}"
        
        try:
            logger.info(f"Making {method} request to {url}")
            
            response = self.session.request(
                method=method,
                url=url,
                json=data,
                params=params,
    # Entire file removed, replaced by enhanced_api_client.py
            )
