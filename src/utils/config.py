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

    # API Configuration
    GROK_API_KEY = os.getenv("GROK_API_KEY")
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
    DEFAULT_PROVIDER = os.getenv("DEFAULT_PROVIDER", "grok")
    FALLBACK_PROVIDER = os.getenv("FALLBACK_PROVIDER", "gemini")

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

        if not cls.GROK_API_KEY and not cls.GEMINI_API_KEY:
            errors.append("At least one API key (Grok or Gemini) must be provided.")

        if cls.DEFAULT_PROVIDER not in ["grok", "gemini"]:
            errors.append("DEFAULT_PROVIDER must be either 'grok' or 'gemini'.")

        if cls.FALLBACK_PROVIDER not in ["grok", "gemini"]:
            errors.append("FALLBACK_PROVIDER must be either 'grok' or 'gemini'.")

        if cls.LOG_FORMAT not in ["console", "json"]:
            errors.append("LOG_FORMAT must be either 'console' or 'json'.")

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