import os

import openai
import asyncio
from typing import Dict, Any

class OpenAILLMService:
    """
    Asynchronous service to call OpenAI LLM for content analysis/summary.
    """
    def __init__(self, api_key: str = None, model: str = "gpt-4o"):
        import logging
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        self.model = model
        if self.api_key:
            logging.info(f"[OpenAILLMService] OPENAI_API_KEY loaded: {self.api_key[:8]}... (length: {len(self.api_key)})")
        else:
            logging.error("[OpenAILLMService] OPENAI_API_KEY is NOT loaded! LLM calls will fail.")
        self.client = openai.OpenAI(api_key=self.api_key)

    async def analyze_content(self, outline, key_phrases, summary, full_text) -> str:
        prompt = (
            "You are an expert content summarizer. "
            "Given the following structured data from a web page, provide a concise summary and key insights.\n"
            f"Outline: {outline}\n"
            f"Key Phrases: {key_phrases}\n"
            f"Summary: {summary}\n"
            f"Full Text: {full_text[:2000]}..."  # Truncate for token safety
        )
        loop = asyncio.get_event_loop()
        def _call():
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are an expert content summarizer."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=512,
                temperature=0.5
            )
            return response.choices[0].message.content
        return await loop.run_in_executor(None, _call)
