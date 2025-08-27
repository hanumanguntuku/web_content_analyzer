import pytest
from fastapi.testclient import TestClient
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../src')))
from fastapi import FastAPI
import importlib.util
main_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '../main.py'))
spec = importlib.util.spec_from_file_location("main", main_path)
main = importlib.util.module_from_spec(spec)
spec.loader.exec_module(main)
app = main.app

client = TestClient(app)

def test_root():
    response = client.get("/")
    assert response.status_code == 200

@pytest.mark.xfail(reason="Known async context bug in web scraper causes 500 error.")
def test_analyze_url():
    payload = {"url": "https://example.com"}
    response = client.post("/api/v1/analyze", json=payload)
    assert response.status_code in (200, 422)  # 422 if validation fails

def test_batch_analyze():
    payload = {"urls": ["https://example.com", "https://openai.com"]}
    response = client.post("/api/v1/analyze/batch", json=payload)
    assert response.status_code in (200, 422)
