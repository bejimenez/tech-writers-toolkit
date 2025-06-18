# src/utils/decorators.py
"""Useful decorators for logging and error handling."""

import time
import functools
from typing import Callable, Any, Optional
from src.utils.logger import get_logger

logger = get_logger(__name__)

def log_execution_time(func: Callable) -> Callable:
    """Decorator to log function execution time"""
    @functools.wraps(func)
    def wrapper(*args, **kwargs) -> Any:
        start_time = time.time()
        try:
            result = func(*args, **kwargs)
            execution_time = time.time() - start_time
            logger.info(
                "Function executed successfully",
                function=func.__name__,
                execution_time=f"{execution_time:.3f}s"
            )
            return result
        except Exception as e:
            execution_time = time.time() - start_time
            logger.error(
                "Function execution failed",
                function=func.__name__,
                execution_time=f"{execution_time:.3f}s",
                error=str(e)
            )
            raise
    return wrapper

def log_api_call(provider: Optional[str] = None):
    """Decorator to log API calls with provider information"""

    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            start_time = time.time()
            call_provider = provider or kwargs.get('provider', 'unknown')

            logger.info(
                "API call started",
                function=func.__name__,
                provider=call_provider,
            )

            try:
                result = func(*args, **kwargs)
                execution_time = time.time() - start_time
                logger.info(
                    "API call completed",
                    function=func.__name__,
                    provider=call_provider,
                    execution_time=f"{execution_time:.3f}s"
                )
                return result
            except Exception as e:
                execution_time = time.time() - start_time
                logger.error(
                    "API call failed",
                    function=func.__name__,
                    provider=call_provider,
                    execution_time=f"{execution_time:.3f}s",
                    error=str(e)
                )
                raise
        return wrapper
    return decorator

def handle_exceptions(default_return=None, reraise=True):
    """Decorator to handle exceptions and log them"""
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            try:
                return func(*args, **kwargs)
            except Exception as e:
                logger.exception(
                    "Exception occurred in function",
                    function=func.__name__,
                    error=str(e)
                )
                if reraise:
                    raise
                return default_return
            
        return wrapper
    return decorator