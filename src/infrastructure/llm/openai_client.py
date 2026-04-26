import json
from typing import Dict, Any
from openai import OpenAI
from core.settings import settings
from core.logger import logger
from domain.interfaces.llm_interface import ILLMInterface

class OpenAIClient(ILLMInterface):
    def __init__(self, model_name: str = None):
        if not settings.OPENAI_API_KEY:
            raise ValueError("OPENAI_API_KEY is not set.")
        client_kwargs = {"api_key": settings.OPENAI_API_KEY}
        if settings.OPENAI_BASE_URL:
            client_kwargs["base_url"] = settings.OPENAI_BASE_URL
        self.client = OpenAI(**client_kwargs)
        self.model_name = model_name or settings.OPENAI_MODEL_NAME

    def generate_response(self, prompt: str, system_prompt: str = None) -> str:
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})
        
        response = self.client.chat.completions.create(
            model=self.model_name,
            messages=messages,
            temperature=0.1
        )
        return response.choices[0].message.content

    def evaluate_json(self, prompt: str, system_prompt: str = None) -> Dict[str, Any]:
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})
        
        response = self.client.chat.completions.create(
            model=self.model_name,
            messages=messages,
            temperature=0.1,
            response_format={ "type": "json_object" }
        )
        
        content = response.choices[0].message.content
        try:
            return json.loads(content)
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse JSON response: {e}")
            return {}
