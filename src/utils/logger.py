# src/utils/logger.py

"""Logging configuration and utilities."""

import sys
import logging
import structlog
from pathlib import Path
from typing import Any, Dict, Optional
from datetime import datetime
from rich.console import Console
from rich.logging import RichHandler

from .config import Config

# Initialize Rich console for pretty logging
console = Console()

def setup_logging():
    """Setup structured logging with Rich console output."""

    # Create logs directory if it doesn't exist
    Config.LOGS_DIR.mkdir(parents=True, exist_ok=True)

    # configure standard library logging
    logging.basicConfig(
        level=getattr(logging, Config.LOG_LEVEL.upper()),
        format="%(message)s",
        handlers=[
            RichHandler(console=console, rich_tracebacks=True, show_time=False),
            logging.FileHandler(Config.LOGS_DIR / "app.log"),
        ]
    )

    # configure structlog
    structlog.configure(
        processors=[
            structlog.stdlib.filter_by_level,
            structlog.stdlib.add_logger_name,
            structlog.stdlib.add_log_level,
            structlog.stdlib.PositionalArgumentsFormatter(),
            add_timestamp,
            add_context,
            structlog.processors.StackInfoRenderer(),
            structlog.processors.format_exc_info,
            structlog.processors.UnicodeDecoder(),
            structlog.processors.JSONRenderer() if Config.LOG_FORMAT == "json"
            else structlog.dev.ConsoleRenderer(colors=True)
        ],
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
        wrapper_class=structlog.stdlib.BoundLogger,
        cache_logger_on_first_use=True,
    )

    # Setup sentry if enabled
    if Config.ENABLE_SENTRY and Config.SENTRY_DSN:
        import sentry_sdk
        from sentry_sdk.integrations.logging import LoggingIntegration

        sentry_logging = LoggingIntegration(
            level=logging.INFO,  # Capture info and above as breadcrumbs
            event_level=logging.ERROR  # Send errors as events
        )

        sentry_sdk.init(
            dsn=Config.SENTRY_DSN,
            integrations=[sentry_logging],
            traces_sample_rate=0.1,
            environment="development" if Config.DEBUG else "production",
        )

def add_timestamp(logger, method_name, event_dict):
    """Add timestamp to log entries"""
    event_dict["timestamp"] = datetime.utcnow().isoformat()
    return event_dict

def add_context(logger, method_name, event_dict):
    """Add application context to log entries"""
    event_dict["app"] = Config.APP_NAME
    event_dict["version"] = Config.APP_VERSION
    return event_dict

def get_logger(name: Optional[str] = None) -> structlog.BoundLogger:
    """Get a configured logger instance"""
    return structlog.get_logger(name)

class LoggerMixin:
    """Mixin to add logging capabilities to classes."""

    @property
    def logger(self) -> structlog.BoundLogger:
        """Get logger for this class"""
        return get_logger(self.__class__.__name__)