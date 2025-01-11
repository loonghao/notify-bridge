"""Utility functions and classes for notify-bridge.

This module provides utility functions and classes for HTTP clients and logging.
"""

# Import built-in modules
import asyncio
import time
from types import TracebackType
from typing import Any
from typing import Dict
from typing import Optional
from typing import Type

# Import third-party modules
import httpx
from pydantic import BaseModel
from pydantic import Field
from pydantic import field_validator

# Import local modules
from notify_bridge.exceptions import NotificationError


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
    headers: Dict[str, str] = Field(
        default_factory=lambda: {"User-Agent": "notify-bridge/1.0", "Accept": "application/json"}
    )

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
    """HTTP client for making requests."""

    def __init__(self, config: HTTPClientConfig) -> None:
        """Initialize HTTP client.

        Args:
            config: HTTP client configuration
        """
        self._config = config
        self._client: Optional[httpx.Client] = None

    def __enter__(self) -> "HTTPClient":
        """Enter context manager."""
        self._client = httpx.Client(
            timeout=self._config.timeout, verify=self._config.verify_ssl, headers=self._config.headers
        )
        return self

    def __exit__(
        self, exc_type: Optional[Type[BaseException]], exc_val: Optional[BaseException], exc_tb: Optional[TracebackType]
    ) -> None:
        """Exit context manager."""
        if self._client:
            self._client.close()
            self._client = None

    def request(self, method: str, url: str, **kwargs: Any) -> httpx.Response:
        """Make HTTP request.

        Args:
            method: HTTP method
            url: Request URL
            **kwargs: Additional arguments passed to httpx.request

        Returns:
            Response object

        Raises:
            RequestError: If request fails after max retries
        """
        if not self._client:
            raise NotificationError("HTTP client not initialized")

        attempt = 0
        while attempt < self._config.max_retries:
            try:
                return self._client.request(method, url, **kwargs)
            except httpx.RequestError as e:
                attempt += 1
                if attempt == self._config.max_retries:
                    raise NotificationError(f"Request failed after {attempt} attempts: {str(e)}")
                time.sleep(self._config.retry_delay)


class AsyncHTTPClient:
    """Async HTTP client for making requests."""

    def __init__(self, config: HTTPClientConfig) -> None:
        """Initialize async HTTP client.

        Args:
            config: HTTP client configuration
        """
        self._config = config
        self._client: Optional[httpx.AsyncClient] = None

    async def __aenter__(self) -> "AsyncHTTPClient":
        """Enter async context manager."""
        self._client = httpx.AsyncClient(
            timeout=self._config.timeout, verify=self._config.verify_ssl, headers=self._config.headers
        )
        return self

    async def __aexit__(
        self, exc_type: Optional[Type[BaseException]], exc_val: Optional[BaseException], exc_tb: Optional[TracebackType]
    ) -> None:
        """Exit async context manager."""
        if self._client:
            await self._client.aclose()
            self._client = None

    async def request(self, method: str, url: str, **kwargs: Any) -> httpx.Response:
        """Make async HTTP request.

        Args:
            method: HTTP method
            url: Request URL
            **kwargs: Additional arguments passed to httpx.request

        Returns:
            Response object

        Raises:
            RequestError: If request fails after max retries
        """
        if not self._client:
            raise NotificationError("HTTP client not initialized")

        attempt = 0
        while attempt < self._config.max_retries:
            try:
                return await self._client.request(method, url, **kwargs)
            except httpx.RequestError as e:
                attempt += 1
                if attempt == self._config.max_retries:
                    raise NotificationError(f"Request failed after {attempt} attempts: {str(e)}")
                await asyncio.sleep(self._config.retry_delay)
