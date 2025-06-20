# src/utils/config.py
"""Configuration management for the application."""

import os
import secrets
from pathlib import Path
from typing import Optional
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Config:
    """Application configuration class."""

    # App Info
    APP_NAME = os.getenv("APP_NAME", "Technical Writing Assistant")
    APP_VERSION = os.getenv("APP_VERSION", "1.0.0")
    DEBUG = os.getenv("DEBUG", "false").lower() == "true"

    # Phase 1: Mistral API for OCR
    MISTRAL_API_KEY = os.getenv("MISTRAL_API_KEY")
    MISTRAL_BASE_URL = os.getenv("MISTRAL_BASE_URL", "https://api.mistral.ai/v1")
    MISTRAL_MODEL = os.getenv("MISTRAL_MODEL", "pixtral-12b-2409")

    # Phase 2: AI Agents API Configuration
    GROQ_API_KEY = os.getenv("GROQ_API_KEY")
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
    DEFAULT_PROVIDER = os.getenv("DEFAULT_PROVIDER", "groq")
    FALLBACK_PROVIDER = os.getenv("FALLBACK_PROVIDER", "gemini")

    # AI Features Toggle
    ENABLE_AI_AGENTS = os.getenv("ENABLE_AI_AGENTS", "true").lower() == "true"

    # OCR Settings
    OCR_MAX_IMAGE_SIZE = int(os.getenv("OCR_MAX_IMAGE_SIZE", "2048"))  # Max width/height in pixels
    OCR_DPI = int(os.getenv("OCR_DPI", "300"))  # DPI for PDF to image conversion
    OCR_TIMEOUT = int(os.getenv("OCR_TIMEOUT", "30"))  # Request timeout in seconds

    # Model Settings
    MAX_TOKENS_PER_REQUEST = int(os.getenv("MAX_TOKENS_PER_REQUEST", "2000"))
    ENABLE_RESPONSE_CACHE = os.getenv("ENABLE_RESPONSE_CACHE", "true").lower() == "true"
    CACHE_TTL_HOURS = int(os.getenv("CACHE_TTL_HOURS", "24"))

    # Logging
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
    LOG_FORMAT = os.getenv("LOG_FORMAT", "console") # or json
    ENABLE_SENTRY = os.getenv("ENABLE_SENTRY", "false").lower() == "true"
    SENTRY_DSN = os.getenv("SENTRY_DSN")
    LOG_RETENTION_DAYS = int(os.getenv("LOG_RETENTION_DAYS", "30"))

    # Security
    JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", secrets.token_urlsafe(32))
    JWT_ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")
    JWT_EXPIRATION_HOURS = int(os.getenv("JWT_EXPIRATION_HOURS", "8"))
    ENCRYPTION_KEY = os.getenv("ENCRYPTION_KEY", secrets.token_urlsafe(32))
    SESSION_TIMEOUT_MINUTES = int(os.getenv("SESSION_TIMEOUT_MINUTES", "30"))
    MAX_LOGIN_ATTEMPTS = int(os.getenv("MAX_LOGIN_ATTEMPTS", "3"))
    PASSWORD_MIN_LENGTH = int(os.getenv("PASSWORD_MIN_LENGTH", "8"))

    # Paths
    BASE_DIR = Path(__file__).parent.parent.parent
    DATA_DIR = BASE_DIR / "data"
    LOGS_DIR = BASE_DIR / "logs"
    REVIEWS_DIR = BASE_DIR / "reviews"
    TEMPLATES_DIR = BASE_DIR / "templates"
    KNOWLEDGE_DIR = BASE_DIR / "knowledge"

    @classmethod
    def validate_config(cls) -> list[str]:
        """Validate configuration and return list of errors"""
        errors = []

        # Phase 1: OCR validation (optional)
        if cls.MISTRAL_API_KEY and not cls.MISTRAL_BASE_URL:
            errors.append("MISTRAL_BASE_URL must be provided when MISTRAL_API_KEY is set.")

        # Phase 2: AI agents validation (only if enabled)
        if cls.ENABLE_AI_AGENTS:
            if not cls.GROQ_API_KEY and not cls.GEMINI_API_KEY:
                errors.append("At least one AI API key (GROQ_API_KEY or GEMINI_API_KEY) must be provided when AI agents are enabled.")

            if cls.DEFAULT_PROVIDER not in ["groq", "gemini"]:
                errors.append("DEFAULT_PROVIDER must be either 'groq' or 'gemini'.")

            if cls.FALLBACK_PROVIDER not in ["groq", "gemini"]:
                errors.append("FALLBACK_PROVIDER must be either 'groq' or 'gemini'.")

            # Validate that the default provider has an API key
            if cls.DEFAULT_PROVIDER == "groq" and not cls.GROQ_API_KEY:
                errors.append("GROQ_API_KEY is required when DEFAULT_PROVIDER is 'groq'.")
            
            if cls.DEFAULT_PROVIDER == "gemini" and not cls.GEMINI_API_KEY:
                errors.append("GEMINI_API_KEY is required when DEFAULT_PROVIDER is 'gemini'.")

        # General validation
        if cls.LOG_FORMAT not in ["console", "json"]:
            errors.append("LOG_FORMAT must be either 'console' or 'json'.")

        if cls.OCR_DPI < 150 or cls.OCR_DPI > 600:
            errors.append("OCR_DPI must be between 150 and 600 for optimal results.")

        if cls.MAX_TOKENS_PER_REQUEST < 100 or cls.MAX_TOKENS_PER_REQUEST > 8000:
            errors.append("MAX_TOKENS_PER_REQUEST must be between 100 and 8000.")

        return errors
    
    @classmethod
    def create_directories(cls):
        """Create necessary directories if they do not exist"""
        directories = [
            cls.DATA_DIR,
            cls.LOGS_DIR,
            cls.REVIEWS_DIR,
            cls.TEMPLATES_DIR,
            cls.KNOWLEDGE_DIR,
            cls.LOGS_DIR / "archive"
        ]

        for directory in directories:
            directory.mkdir(parents=True, exist_ok=True)

    @classmethod
    def get_ai_status(cls) -> dict:
        """Get AI configuration status"""
        return {
            "ai_enabled": cls.ENABLE_AI_AGENTS,
            "groq_configured": bool(cls.GROQ_API_KEY),
            "gemini_configured": bool(cls.GEMINI_API_KEY),
            "default_provider": cls.DEFAULT_PROVIDER,
            "fallback_provider": cls.FALLBACK_PROVIDER,
            "has_any_ai_key": bool(cls.GROQ_API_KEY or cls.GEMINI_API_KEY)
        }