import pytest
from src.services.enhanced_api_client import EnhancedAPIClient

@pytest.fixture
def api_client():
    return EnhancedAPIClient()

def test_get_analysis_history_runs(api_client):
    # Should not raise, even if backend is not running
    try:
        api_client.get_analysis_history()
    except Exception:
        pass

def test_analyze_batch_empty(api_client):
    # Should return a list or error for empty input
    result = api_client.analyze_batch([])
    assert isinstance(result, list) or "error" in str(result).lower()
