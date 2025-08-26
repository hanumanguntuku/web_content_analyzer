import os
import pytest
import asyncio
from unittest.mock import patch, MagicMock
from services.llm_service import GeminiLLMService

@pytest.fixture
def llm_service():
    return GeminiLLMService(gemini_api_key="fake-gemini-key", openai_api_key="fake-openai-key", openai_model="gpt-4o")

@pytest.mark.asyncio
async def test_init_with_keys(monkeypatch):
    monkeypatch.setenv("GEMINI_API_KEY", "env-gemini-key")
    monkeypatch.setenv("OPENAI_API_KEY", "env-openai-key")
    service = GeminiLLMService()
    assert service.gemini_api_key == "env-gemini-key"
    assert service.openai_api_key == "env-openai-key"
    assert service.openai_model == "gpt-4o"

@pytest.mark.asyncio
async def test_gemini_success(monkeypatch, llm_service):
    # Patch requests.post to simulate Gemini API response
    fake_response = MagicMock()
    fake_response.json.return_value = {
        "candidates": [{"content": {"parts": [{"text": "Gemini response"}]}}]
    }
    fake_response.raise_for_status = lambda: None
    with patch("services.llm_service.requests.post", return_value=fake_response):
        result = await llm_service._call_llm("Test prompt")
        assert result == "Gemini response"

@pytest.mark.asyncio
async def test_gemini_failure_openai_success(monkeypatch, llm_service):
    # Patch Gemini to fail, OpenAI to succeed
    with patch("services.llm_service.requests.post", side_effect=Exception("Gemini fail")):
        fake_openai_client = MagicMock()
        fake_openai_client.chat.completions.create.return_value.choices = [
            MagicMock(message=MagicMock(content="OpenAI response"))
        ]
        llm_service.openai_client = fake_openai_client
        result = await llm_service._call_llm("Test prompt")
        assert result == "OpenAI response"

@pytest.mark.asyncio
async def test_both_llm_fail(monkeypatch, llm_service):
    # Patch Gemini and OpenAI to both fail
    with patch("services.llm_service.requests.post", side_effect=Exception("Gemini fail")):
        llm_service.openai_client = None
        with pytest.raises(RuntimeError):
            await llm_service._call_llm("Test prompt")

@pytest.mark.asyncio
async def test_get_content_summary(monkeypatch, llm_service):
    with patch.object(llm_service, "_call_llm", return_value=asyncio.Future()) as mock_call:
        mock_call.return_value.set_result("summary")
        result = await llm_service.get_content_summary("text")
        assert result == "summary"

@pytest.mark.asyncio
async def test_get_sentiment_and_tone(monkeypatch, llm_service):
    with patch.object(llm_service, "_call_llm", return_value=asyncio.Future()) as mock_call:
        mock_call.return_value.set_result('{"sentiment_score": 0.5, "sentiment_label": "Positive", "detected_tones": ["Formal"]}')
        result = await llm_service.get_sentiment_and_tone("text")
        assert result["sentiment_score"] == 0.5
        assert result["sentiment_label"] == "Positive"
        assert result["detected_tones"] == ["Formal"]

@pytest.mark.asyncio
async def test_get_seo_recommendations(monkeypatch, llm_service):
    with patch.object(llm_service, "_call_llm", return_value=asyncio.Future()) as mock_call:
        mock_call.return_value.set_result('{"overall_score": 90, "recommendations": ["Use more keywords"]}')
        result = await llm_service.get_seo_recommendations("text", "title", ["keyword"])
        assert result["overall_score"] == 90
        assert result["recommendations"] == ["Use more keywords"]

@pytest.mark.asyncio
async def test_get_readability_and_accessibility(monkeypatch, llm_service):
    with patch.object(llm_service, "_call_llm", return_value=asyncio.Future()) as mock_call:
        mock_call.return_value.set_result('{"readability_score": 80, "accessibility_notes": ["Use simpler sentences"]}')
        result = await llm_service.get_readability_and_accessibility("text")
        assert result["readability_score"] == 80
        assert result["accessibility_notes"] == ["Use simpler sentences"]
