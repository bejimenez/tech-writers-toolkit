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
        self.logger.info("Groq provider initialized")
    
    @log_api_call(provider="groq")
    def generate_response(
        self,
        prompt: str,
        max_tokens: Optional[int] = None,
        temperature: float = 0.7,
    ) -> str:
        """Generate response using Groq API."""

        payload = {
            "model": "llama3-70b-8192",  # Updated to working model
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
            response = self.generate_response("Hello", max_tokens=10)
            return len(response) > 0
        except Exception:
            return False
        
class GeminiProvider(LLMProvider):
    """Gemini API provider implementation"""
    
    def __init__(self):
        if not Config.GEMINI_API_KEY:
            raise ValueError("GEMINI_API_KEY is required")
        
        self.api_key = Config.GEMINI_API_KEY
        self.client = httpx.Client(timeout=60)
        self.logger.info("Gemini provider initialized")
    
    @log_api_call(provider="gemini")
    def generate_response(
        self, 
        prompt: str, 
        max_tokens: Optional[int] = None,
        temperature: float = 0.7
    ) -> str:
        """Generate response using Gemini REST API"""
        
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={self.api_key}"
        
        payload = {
            "contents": [
                {
                    "parts": [
                        {"text": prompt}
                    ]
                }
            ],
            "generationConfig": {
                "temperature": temperature,
                "maxOutputTokens": max_tokens or Config.MAX_TOKENS_PER_REQUEST,
            }
        }
        
        try:
            response = self.client.post(url, json=payload)
            response.raise_for_status()
            
            result = response.json()
            
            if ("candidates" in result and 
                len(result["candidates"]) > 0 and
                "content" in result["candidates"][0] and
                "parts" in result["candidates"][0]["content"] and
                len(result["candidates"][0]["content"]["parts"]) > 0):
                
                return result["candidates"][0]["content"]["parts"][0]["text"]
            else:
                self.logger.error("Unexpected response format from Gemini API", response=result)
                return ""
                
        except httpx.HTTPStatusError as e:
            self.logger.error(
                "Gemini API request failed",
                status_code=e.response.status_code,
                error=str(e)
            )
            raise
        except Exception as e:
            self.logger.error("Gemini API request failed", error=str(e))
            raise
    
    def is_available(self) -> bool:
        """Check if Gemini API is available"""
        try:
            response = self.generate_response("Hello", max_tokens=10)
            return len(response) > 0
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
        # Initialize Groq provider if configured
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
            try:
                if provider.is_available():
                    available.append(name)
            except Exception:
                pass  # Provider not available
        return available
    
    def test_connection(self, provider: Optional[str] = None) -> Dict[str, Any]:
        """
        Test connection to LLM providers
        
        Args:
            provider: Specific provider to test, or None for all
            
        Returns:
            Dictionary with test results
        """
        results = {}
        
        providers_to_test = [provider] if provider else list(self.providers.keys())
        
        for provider_name in providers_to_test:
            if provider_name not in self.providers:
                results[provider_name] = {
                    "available": False,
                    "error": "Provider not configured"
                }
                continue
            
            try:
                start_time = time.time()
                response = self.providers[provider_name].generate_response(
                    "Say 'Hello' if you can understand this message.",
                    max_tokens=50,
                    temperature=0.1
                )
                response_time = time.time() - start_time
                
                results[provider_name] = {
                    "available": True,
                    "response_time": f"{response_time:.2f}s",
                    "response": response[:100]  # First 100 chars
                }
                
            except Exception as e:
                results[provider_name] = {
                    "available": False,
                    "error": str(e)
                }
        
        return results