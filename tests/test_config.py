# tests/test_config.py
"""Tests for configuration management"""

import pytest
import os
from unittest.mock import patch
from pathlib import Path

# Add src to path for imports
import sys
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from src.utils.config import Config

class TestConfig:
    """Test cases for configuration management"""
    
    def test_default_values(self):
        """Test that default configuration values are set correctly"""
        assert Config.APP_NAME == "Technical Writing Assistant"
        assert Config.APP_VERSION == "1.0.0"
        assert Config.LOG_LEVEL == "INFO"
        assert Config.MAX_TOKENS_PER_REQUEST == 2000
    
    @patch.dict(os.environ, {
        'GROK_API_KEY': 'test_grok_key',
        'GEMINI_API_KEY': 'test_gemini_key',
        'DEFAULT_PROVIDER': 'grok',
        'LOG_LEVEL': 'DEBUG'
    })
    def test_environment_override(self):
        """Test that environment variables override defaults"""
        # Reload config with environment variables
        import importlib
        from src.utils import config
        importlib.reload(config)
        
        assert config.Config.GROK_API_KEY == 'test_grok_key'
        assert config.Config.GEMINI_API_KEY == 'test_gemini_key'
        assert config.Config.DEFAULT_PROVIDER == 'grok'
        assert config.Config.LOG_LEVEL == 'DEBUG'
    
    def test_config_validation_success(self):
        """Test successful configuration validation"""
        with patch.object(Config, 'GROK_API_KEY', 'test_key'):
            with patch.object(Config, 'DEFAULT_PROVIDER', 'grok'):
                with patch.object(Config, 'FALLBACK_PROVIDER', 'gemini'):
                    with patch.object(Config, 'LOG_FORMAT', 'console'):
                        errors = Config.validate_config()
                        assert errors == []
    
    def test_config_validation_missing_api_keys(self):
        """Test configuration validation with missing API keys"""
        with patch.object(Config, 'GROK_API_KEY', None):
            with patch.object(Config, 'GEMINI_API_KEY', None):
                errors = Config.validate_config()
                assert len(errors) > 0
                assert any("API key" in error for error in errors)
    
    def test_config_validation_invalid_provider(self):
        """Test configuration validation with invalid provider"""
        with patch.object(Config, 'GROK_API_KEY', 'test_key'):
            with patch.object(Config, 'DEFAULT_PROVIDER', 'invalid'):
                errors = Config.validate_config()
                assert len(errors) > 0
                assert any("DEFAULT_PROVIDER" in error for error in errors)