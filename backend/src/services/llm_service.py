
import os
import asyncio
from typing import Dict, Any

import logging

class GeminiLLMService:
    """
    Asynchronous service to call Gemini LLM for content analysis/summary, with OpenAI fallback.
    """
    def __init__(self, gemini_api_key: str = None, openai_api_key: str = None, openai_model: str = "gpt-4o"):
        self.gemini_api_key = gemini_api_key or os.getenv("GEMINI_API_KEY")
        self.openai_api_key = openai_api_key or os.getenv("OPENAI_API_KEY")
        self.openai_model = openai_model
        if self.gemini_api_key:
            logging.info(f"[GeminiLLMService] GEMINI_API_KEY loaded: {self.gemini_api_key[:8]}... (length: {len(self.gemini_api_key)})")
        else:
            logging.error("[GeminiLLMService] GEMINI_API_KEY is NOT loaded! Gemini calls will fail.")
        if self.openai_api_key:
            logging.info(f"[GeminiLLMService] OPENAI_API_KEY loaded: {self.openai_api_key[:8]}... (length: {len(self.openai_api_key)})")
        else:
            logging.warning("[GeminiLLMService] OPENAI_API_KEY is NOT loaded! OpenAI fallback will fail if needed.")
        try:
            import openai
            self.openai_client = openai.OpenAI(api_key=self.openai_api_key)
        except Exception as e:
            self.openai_client = None
            logging.error(f"[GeminiLLMService] Failed to initialize OpenAI client: {e}")

    async def analyze_content(self, outline, key_phrases, summary, full_text) -> str:
        prompt = (
            "You are an expert content summarizer. "
            "Given the following structured data from a web page, provide a concise summary and key insights.\n"
            f"Outline: {outline}\n"
            f"Key Phrases: {key_phrases}\n"
            f"Summary: {summary}\n"
            f"Full Text: {full_text[:2000]}..."  # Truncate for token safety
        )
        # Try Gemini API first
        try:
            import requests
            url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent"
            headers = {"Content-Type": "application/json"}
            data = {
                "contents": [
                    {"parts": [{"text": prompt}]}
                ]
            }
            params = {"key": self.gemini_api_key}
            loop = asyncio.get_event_loop()
            def _gemini_call():
                response = requests.post(url, headers=headers, params=params, json=data, timeout=15)
                response.raise_for_status()
                result = response.json()
                # Gemini returns candidates[0].content.parts[0].text
                return result["candidates"][0]["content"]["parts"][0]["text"]
            return await loop.run_in_executor(None, _gemini_call)
        except Exception as gemini_exc:
            logging.error(f"[GeminiLLMService] Gemini API failed: {gemini_exc}")
            # Fallback to OpenAI
            if not self.openai_client:
                raise RuntimeError("Both Gemini and OpenAI clients are unavailable.")
            try:
                def _openai_call():
                    response = self.openai_client.chat.completions.create(
                        model=self.openai_model,
                        messages=[
                            {"role": "system", "content": "You are an expert content summarizer."},
                            {"role": "user", "content": prompt}
                        ],
                        max_tokens=512,
                        temperature=0.5
                    )
                    return response.choices[0].message.content
                return await loop.run_in_executor(None, _openai_call)
            except Exception as openai_exc:
                logging.error(f"[GeminiLLMService] OpenAI fallback failed: {openai_exc}")
                raise RuntimeError(f"Both Gemini and OpenAI LLM calls failed: {openai_exc}")
