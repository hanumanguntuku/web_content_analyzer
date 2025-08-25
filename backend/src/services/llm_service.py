
import os
import asyncio
from typing import Dict, Any, List
import logging
import json

class GeminiLLMService:
    """
    Asynchronous service to call LLMs for various content analysis tasks,
    using Gemini with an OpenAI fallback.
    """
    def __init__(self, gemini_api_key: str = None, openai_api_key: str = None, openai_model: str = "gpt-4o"):
        self.gemini_api_key = gemini_api_key or os.getenv("GEMINI_API_KEY")
        self.openai_api_key = openai_api_key or os.getenv("OPENAI_API_KEY")
        self.openai_model = openai_model
        
        if not self.gemini_api_key:
            logging.error("[LLMService] GEMINI_API_KEY is NOT loaded! Gemini calls will fail.")
        if not self.openai_api_key:
            logging.warning("[LLMService] OPENAI_API_KEY is NOT loaded! OpenAI fallback will fail.")
        
        try:
            import openai
            self.openai_client = openai.OpenAI(api_key=self.openai_api_key)
        except Exception as e:
            self.openai_client = None
            logging.error(f"[LLMService] Failed to initialize OpenAI client: {e}")

    async def _call_llm(self, prompt: str, is_json_output: bool = False) -> str:
        """Generic method to call the LLM, handling Gemini and OpenAI fallback."""
        loop = asyncio.get_event_loop()
        
        # Try Gemini API first
        if self.gemini_api_key:
            try:
                import requests
                url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent"
                headers = {"Content-Type": "application/json"}
                
                # For JSON output, instruct Gemini accordingly
                gemini_prompt = prompt
                if is_json_output:
                    gemini_prompt += "\n\nIMPORTANT: Respond with only a valid JSON object and nothing else."

                data = {"contents": [{"parts": [{"text": gemini_prompt}]}]}
                if is_json_output:
                    data["generationConfig"] = {"responseMimeType": "application/json"}

                params = {"key": self.gemini_api_key}
                
                def _gemini_call():
                    response = requests.post(url, headers=headers, params=params, json=data, timeout=20)
                    response.raise_for_status()
                    result = response.json()
                    return result["candidates"][0]["content"]["parts"][0]["text"]
                
                return await loop.run_in_executor(None, _gemini_call)
            except Exception as gemini_exc:
                logging.error(f"[LLMService] Gemini API failed: {gemini_exc}. Falling back to OpenAI.")

        # Fallback to OpenAI
        if not self.openai_client:
            raise RuntimeError("Both Gemini and OpenAI clients are unavailable.")
        
        try:
            def _openai_call():
                messages = [{"role": "system", "content": "You are an expert content analysis assistant."}]
                if is_json_output:
                    messages[0]["content"] += " You must respond in JSON format."
                
                messages.append({"role": "user", "content": prompt})

                response = self.openai_client.chat.completions.create(
                    model=self.openai_model,
                    messages=messages,
                    max_tokens=1024,
                    temperature=0.3,
                    response_format={"type": "json_object"} if is_json_output else None
                )
                return response.choices[0].message.content
            
            return await loop.run_in_executor(None, _openai_call)
        except Exception as openai_exc:
            logging.error(f"[LLMService] OpenAI fallback failed: {openai_exc}")
            raise RuntimeError(f"Both Gemini and OpenAI LLM calls failed: {openai_exc}")

    async def get_content_summary(self, text: str) -> str:
        """Generates a concise summary and key insights."""
        prompt = (
            "You are an expert content summarizer. Analyze the following text and provide:\n"
            "1. A concise, one-paragraph summary.\n"
            "2. A bulleted list of the top 3-5 key insights or takeaways.\n\n"
            f"Full Text:\n'''{text[:8000]}'''"  # Use a generous portion of text
        )
        return await self._call_llm(prompt)

    async def get_sentiment_and_tone(self, text: str) -> Dict[str, Any]:
        """Analyzes sentiment and identifies the tone of the content."""
        prompt = (
            "Analyze the sentiment and tone of the following text. Provide your answer in a JSON object "
            "with three keys: 'sentiment_score' (a float from -1.0 for very negative to 1.0 for very positive), "
            "'sentiment_label' (a string like 'Positive', 'Negative', 'Neutral'), and "
            "'detected_tones' (a list of 2-3 descriptive strings, e.g., 'Formal', 'Informative', 'Optimistic').\n\n"
            f"Text:\n'''{text[:4000]}'''"
        )
        response_str = await self._call_llm(prompt, is_json_output=True)
        return json.loads(response_str)

    async def get_seo_recommendations(self, text: str, title: str, keywords: List[str]) -> Dict[str, Any]:
        """Generates SEO recommendations based on content."""
        prompt = (
            "You are an SEO expert. Analyze the following content and provide actionable recommendations in a JSON object. "
            "The object should have two keys: 'overall_score' (a float from 0 to 100 assessing SEO-friendliness) and "
            "'recommendations' (a list of specific, actionable strings to improve SEO).\n\n"
            f"Page Title: '{title}'\n"
            f"Top Keywords: {', '.join(keywords)}\n"
            f"Text:\n'''{text[:6000]}'''"
        )
        response_str = await self._call_llm(prompt, is_json_output=True)
        return json.loads(response_str)

    async def get_readability_and_accessibility(self, text: str) -> Dict[str, Any]:
        """Scores readability and provides accessibility feedback."""
        prompt = (
            "You are a web accessibility and content expert. Analyze the following text and provide a JSON object with two keys:\n"
            "1. 'readability_score': A float from 0 to 100 (based on Flesch Reading Ease principles).\n"
            "2. 'accessibility_notes': A list of 2-3 actionable strings to improve content accessibility for users with disabilities "
            "(e.g., 'Use simpler sentence structures', 'Define acronyms', 'Ensure sufficient color contrast for links').\n\n"
            f"Text:\n'''{text[:6000]}'''"
        )
        response_str = await self._call_llm(prompt, is_json_output=True)
        return json.loads(response_str)
