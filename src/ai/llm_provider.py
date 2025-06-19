# src/ai/llm_provider.py
"""LLM Provider interface for interacting with different LLMs"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List
import httpx
import time

from src.utils.config import Config
from src.utils.logger import LoggerMixin
from src.utils.decorators import log_api_call

class LLMProvider(ABC, LoggerMixin):
    """Abstract base class for LLM providers."""

    @abstractmethod
    def generate_response(
        self,
        prompt: str,
        max_tokens: Optional[int] = None,
        temperature: float = 0.7,
    ) -> str:
        """Generate a response from the LLM based on the provided prompt."""
        pass

    @abstractmethod
    def is_available(self) -> bool:
        """Check if the LLM provider is available."""
        pass

class GroqProvider(LLMProvider):
    """Groq API provider implementation."""
    def __init__(self):
        if not Config.GROQ_API_KEY:
            raise ValueError("GROQ_API_KEY is not set in the configuration.")

        self.client = httpx.Client(
            base_url="https://api.groq.com/openai/v1",
            headers={
                "Authorization": f"Bearer {Config.GROQ_API_KEY}",
                "Content-Type": "application/json"
            },
            timeout=60
        )
    @log_api_call(provider="groq")
    def generate_response(
        self,
        prompt: str,
        max_tokens: Optional[int] = None,
        temperature: float = 0.7,
    ) -> str:
        """Generate response using Groq API."""

        payload = {
            "model": "groq/groq-llama-3-70b",
            "messages": [{"role": "user", "content": prompt}],
            "max_tokens": max_tokens or Config.MAX_TOKENS_PER_REQUEST,
            "temperature": temperature
        }

        try:
            response = self.client.post("/chat/completions", json=payload)
            response.raise_for_status()

            result = response.json()

            if "choices" in result and len(result["choices"]) > 0:
                return result["choices"][0]["message"]["content"]
            else:
                self.logger.error("Unexpected response format from Groq API", response=result)
                return ""
            
        except httpx.HTTPStatusError as e:
            self.logger.error(
                "Groq API request failed",
                status_code=e.response.status_code,
                error=str(e)
            )
            raise
        except Exception as e:
            self.logger.error("Error during Groq API request", error=str(e))
            raise
    
    def is_available(self) -> bool:
        """Check if Groq API is available"""

        try:
            # Simple health check
            self.generate_response("Test", max_tokens=1)
            return True
        except Exception:
            return False
        
class GeminiProvider(LLMProvider):
    """Gemini API provider implementation"""
    
    def __init__(self):
        if not Config.GEMINI_API_KEY:
            raise ValueError("GEMINI_API_KEY is required")
        try:
            from google import genai
            self.client = genai.Client(api_key=Config.GEMINI_API_KEY)
        except ImportError:
            raise ImportError("google-genai package is required for Gemini")
    
    @log_api_call(provider="gemini")
    def generate_response(
        self, 
        prompt: str, 
        max_tokens: Optional[int] = None,
        temperature: float = 0.7
    ) -> str:
        """Generate response using Gemini API"""
        try:
            from google.genai import types
            response = self.client.models.generate_content(
                model="gemini-2.0-flash-001",
                contents=prompt,
                config=types.GenerateContentConfig(
                    max_output_tokens=max_tokens or Config.MAX_TOKENS_PER_REQUEST,
                    temperature=temperature
                )
            )
            return response.text or ""
        except Exception as e:
            self.logger.error("Gemini API request failed", error=str(e))
            raise
    
    def is_available(self) -> bool:
        """Check if Gemini API is available"""
        try:
            self.generate_response("Test", max_tokens=1)
            return True
        except Exception:
            return False
        

class LLMManager(LoggerMixin):
    """Manages LLM providers with fallback logic"""
    
    def __init__(self):
        self.providers: Dict[str, LLMProvider] = {}
        self.default_provider = Config.DEFAULT_PROVIDER
        self.fallback_provider = Config.FALLBACK_PROVIDER
        
        self._initialize_providers()
    
    def _initialize_providers(self):
        """Initialize available providers"""
        try:
            if Config.GROQ_API_KEY:
                self.providers["groq"] = GroqProvider()
                self.logger.info("Groq provider initialized")
        except Exception as e:
            self.logger.warning("Failed to initialize Groq provider", error=str(e))
        # Initialize Gemini provider if configured
        try:
            if Config.GEMINI_API_KEY:
                self.providers["gemini"] = GeminiProvider()
                self.logger.info("Gemini provider initialized")
        except Exception as e:
            self.logger.warning("Failed to initialize Gemini provider", error=str(e))
    
    def generate_response(
        self, 
        prompt: str, 
        max_tokens: Optional[int] = None,
        temperature: float = 0.7,
        provider: Optional[str] = None
    ) -> str:
        """
        Generate response with provider fallback
        
        Args:
            prompt: The prompt to send
            max_tokens: Maximum tokens to generate
            temperature: Generation temperature
            provider: Specific provider to use (optional)
            
        Returns:
            Generated response text
        """
        # Use specified provider or default
        provider_name = provider or self.default_provider
        
        # Try primary provider
        if provider_name in self.providers:
            try:
                return self.providers[provider_name].generate_response(
                    prompt, max_tokens, temperature
                )
            except Exception as e:
                self.logger.warning(
                    "Primary provider failed, trying fallback",
                    provider=provider_name,
                    error=str(e)
                )
        
        # Try fallback provider
        if (self.fallback_provider != provider_name and 
            self.fallback_provider in self.providers):
            try:
                return self.providers[self.fallback_provider].generate_response(
                    prompt, max_tokens, temperature
                )
            except Exception as e:
                self.logger.error(
                    "Fallback provider also failed",
                    provider=self.fallback_provider,
                    error=str(e)
                )
        
        raise RuntimeError("All LLM providers failed")
    
    def get_available_providers(self) -> List[str]:
        """Get list of available provider names"""
        available = []
        for name, provider in self.providers.items():
            if provider.is_available():
                available.append(name)
        return available