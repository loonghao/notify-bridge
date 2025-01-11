"""Utility functions and classes for notify-bridge.

This module provides utility functions and classes for HTTP clients and logging.
"""

import asyncio
import logging
import logging.handlers
import os
import time
from functools import wraps
from typing import Any, Dict, Optional, Union

import httpx
from pydantic import BaseModel, field_validator

from .exceptions import NotificationError


class HTTPClientConfig(BaseModel):
    """Configuration for HTTP clients.
    
    Attributes:
        timeout: Request timeout in seconds
        max_retries: Maximum number of retries
        retry_delay: Delay between retries in seconds
        verify_ssl: Whether to verify SSL certificates
        proxies: Proxy configuration
        headers: Default headers
    """
    timeout: float = 30.0
    max_retries: int = 3
    retry_delay: float = 1.0
    verify_ssl: bool = True
    proxies: Optional[Dict[str, str]] = None
    headers: Dict[str, str] = {
        "User-Agent": "notify-bridge/1.0",
        "Accept": "application/json"
    }

    @field_validator("timeout")
    @classmethod
    def validate_timeout(cls, v: float) -> float:
        """Validate timeout value.
        
        Args:
            v: Timeout value
            
        Returns:
            Validated timeout value
            
        Raises:
            ValueError: If timeout is not positive
        """
        if v <= 0:
            raise ValueError("Timeout must be positive")
        return v

    @field_validator("max_retries")
    @classmethod
    def validate_max_retries(cls, v: int) -> int:
        """Validate max_retries value.
        
        Args:
            v: Max retries value
            
        Returns:
            Validated max retries value
            
        Raises:
            ValueError: If max_retries is negative
        """
        if v < 0:
            raise ValueError("Max retries cannot be negative")
        return v

    @field_validator("retry_delay")
    @classmethod
    def validate_retry_delay(cls, v: float) -> float:
        """Validate retry_delay value.
        
        Args:
            v: Retry delay value
            
        Returns:
            Validated retry delay value
            
        Raises:
            ValueError: If retry_delay is not positive
        """
        if v <= 0:
            raise ValueError("Retry delay must be positive")
        return v


class HTTPClient:
    """HTTP client with retries."""

    def __init__(self, config: HTTPClientConfig, client: Optional[httpx.Client] = None) -> None:
        """Initialize HTTP client.
        
        Args:
            config: HTTP client configuration
            client: Optional httpx client instance for testing
        """
        self._config = config
        self._client = None

    def __enter__(self):
        """Enter context manager."""
        if not self._client:
            client_kwargs = {
                "timeout": self._config.timeout,
                "verify": self._config.verify_ssl,
                "headers": self._config.headers,
            }
            if self._config.proxies:
                client_kwargs["proxy"] = next(iter(self._config.proxies.values()))

            self._client = httpx.Client(**client_kwargs)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Exit context manager."""
        self.close()

    def close(self):
        """Close the client."""
        if self._client:
            self._client.close()
            self._client = None

    def request(self, method: str, url: str, **kwargs: Any) -> httpx.Response:
        """Make HTTP request with retries.
        
        Args:
            method: HTTP method
            url: Request URL
            **kwargs: Additional arguments to pass to httpx.request
            
        Returns:
            Response object
            
        Raises:
            RequestError: If request fails after max retries
        """
        if not self._client:
            self.__enter__()

        last_error = None
        verify = kwargs.pop("verify", True)

        for _ in range(self._config.max_retries):
            try:
                with httpx.Client(
                    timeout=self._config.timeout,
                    verify=self._config.verify_ssl,
                    headers=self._config.headers,
                    proxies=self._config.proxies if self._config.proxies else None
                ) as client:
                    response = client.request(method, url, verify=verify, **kwargs)
                    response.raise_for_status()
                    return response
            except httpx.RequestError as e:
                last_error = e
                time.sleep(self._config.retry_delay)
                continue
            except Exception as e:
                raise NotificationError.from_exception(e, "http_client")

        if last_error:
            raise last_error


class AsyncHTTPClient:
    """Async HTTP client with retries."""

    def __init__(self, config: HTTPClientConfig, client: Optional[httpx.AsyncClient] = None) -> None:
        """Initialize async HTTP client.
        
        Args:
            config: HTTP client configuration
            client: Optional httpx async client instance for testing
        """
        self._config = config
        self._client = None

    async def __aenter__(self):
        """Enter async context manager."""
        if not self._client:
            client_kwargs = {
                "timeout": self._config.timeout,
                "verify": self._config.verify_ssl,
                "headers": self._config.headers,
            }
            if self._config.proxies:
                client_kwargs["proxy"] = next(iter(self._config.proxies.values()))

            self._client = httpx.AsyncClient(**client_kwargs)
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Exit async context manager."""
        await self.aclose()

    async def aclose(self):
        """Close the client."""
        if self._client:
            await self._client.aclose()
            self._client = None

    async def request(self, method: str, url: str, **kwargs: Any) -> httpx.Response:
        """Make async HTTP request with retries.
        
        Args:
            method: HTTP method
            url: Request URL
            **kwargs: Additional arguments to pass to httpx.request
            
        Returns:
            Response object
            
        Raises:
            RequestError: If request fails after max retries
        """
        if not self._client:
            await self.__aenter__()

        last_error = None

        for _ in range(self._config.max_retries):
            try:
                response = await self._client.request(method, url, **kwargs)
                response.raise_for_status()
                return response
            except httpx.RequestError as e:
                last_error = e
                await asyncio.sleep(self._config.retry_delay)
                continue
            except Exception as e:
                raise NotificationError.from_exception(e, "http_client")

        if last_error:
            raise last_error


class LogConfig(BaseModel):
    """Configuration for logging.

    Attributes:
        level: Log level
        format: Log format
        date_format: Date format
        filename: Log file name
        max_bytes: Maximum bytes per file
        backup_count: Number of backup files
    """
    level: Union[str, int] = logging.INFO
    format: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    date_format: str = "%Y-%m-%d %H:%M:%S"
    filename: Optional[str] = None
    max_bytes: int = 10 * 1024 * 1024  # 10MB
    backup_count: int = 5

    @field_validator("level")
    @classmethod
    def validate_level(cls, v: Union[str, int]) -> Union[str, int]:
        """Validate log level.

        Args:
            v: Log level

        Returns:
            Validated log level

        Raises:
            ValueError: If level is invalid
        """
        if isinstance(v, str):
            v = v.upper()
            if v not in logging._nameToLevel:
                raise ValueError(f"Invalid log level: {v}")
        elif isinstance(v, int):
            if v not in logging._levelToName:
                raise ValueError(f"Invalid log level: {v}")
        else:
            raise ValueError(f"Invalid log level type: {type(v)}")
        return v


def setup_logging(config: Optional[LogConfig] = None) -> None:
    """Setup logging configuration.

    Args:
        config: Logging configuration
    """
    config = config or LogConfig()

    # Convert string level to int if needed
    if isinstance(config.level, str):
        config.level = getattr(logging, config.level.upper())

    # Create formatter
    formatter = logging.Formatter(
        fmt=config.format,
        datefmt=config.date_format
    )

    # Setup handlers
    handlers = []

    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    handlers.append(console_handler)

    # File handler if filename is provided
    if config.filename:
        os.makedirs(os.path.dirname(config.filename), exist_ok=True)
        file_handler = logging.handlers.RotatingFileHandler(
            filename=config.filename,
            maxBytes=config.max_bytes,
            backupCount=config.backup_count
        )
        file_handler.setFormatter(formatter)
        handlers.append(file_handler)

    # Configure root logger
    logging.basicConfig(
        level=config.level,
        handlers=handlers,
        force=True
    )


def log_call(logger: Optional[logging.Logger] = None):
    """Decorator to log function calls.

    Args:
        logger: Logger to use, defaults to module logger
    """
    def decorator(func):
        nonlocal logger
        if logger is None:
            logger = logging.getLogger(func.__module__)

        @wraps(func)
        def wrapper(*args, **kwargs):
            logger.debug(
                f"Calling {func.__name__} with args={args}, kwargs={kwargs}"
            )
            try:
                result = func(*args, **kwargs)
                logger.debug(f"{func.__name__} returned {result}")
                return result
            except Exception:
                logger.exception(f"{func.__name__} raised an exception")
                raise

        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            logger.debug(
                f"Calling {func.__name__} with args={args}, kwargs={kwargs}"
            )
            try:
                result = await func(*args, **kwargs)
                logger.debug(f"{func.__name__} returned {result}")
                return result
            except Exception:
                logger.exception(f"{func.__name__} raised an exception")
                raise

        return async_wrapper if asyncio.iscoroutinefunction(func) else wrapper
    return decorator
