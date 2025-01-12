"""Utility functions and classes for notify-bridge.

This module provides utility functions and classes for HTTP clients and logging.
"""

# Import built-in modules
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


class HTTPClientConfig(BaseModel):
    """Configuration for HTTP clients.

    Attributes:
        timeout: Request timeout in seconds
        max_retries: Maximum number of retries
        retry_delay: Delay between retries in seconds
        verify_ssl: Whether to verify SSL certificates
        headers: Default headers
    """

    timeout: float = 30.0
    max_retries: int = 3
    retry_delay: float = 1.0
    verify_ssl: bool = True
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
    """HTTP client wrapper."""

    def __init__(self, config: HTTPClientConfig) -> None:
        """Initialize client.

        Args:
            config: HTTP client configuration
        """
        self._config = config
        self._client = httpx.Client(
            timeout=config.timeout,
            verify=config.verify_ssl,
            headers=config.headers,
        )

    def __enter__(self) -> "HTTPClient":
        """Enter context manager.

        Returns:
            HTTPClient: Self
        """
        return self

    def __exit__(
        self,
        exc_type: Optional[Type[BaseException]],
        exc_val: Optional[BaseException],
        exc_tb: Optional[TracebackType],
    ) -> None:
        """Exit context manager.

        Args:
            exc_type: Exception type
            exc_val: Exception value
            exc_tb: Exception traceback
        """
        self.close()

    def request(
        self,
        method: str,
        url: str,
        *,
        params: Optional[Dict[str, Any]] = None,
        json: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, Any]] = None,
        **kwargs: Any,
    ) -> httpx.Response:
        """Send HTTP request.

        Args:
            method: HTTP method.
            url: Request URL.
            params: Query parameters.
            json: JSON body.
            headers: Request headers.
            **kwargs: Additional arguments.

        Returns:
            httpx.Response: HTTP response.
        """
        method = method.upper()
        request_method = getattr(self._client, method.lower(), None)
        if request_method is None:
            raise ValueError(f"Unsupported HTTP method: {method}")
        return request_method(url, params=params, json=json, headers=headers, **kwargs)

    def get(self, *args: Any, **kwargs: Any) -> httpx.Response:
        """Send GET request."""
        return self._client.get(*args, **kwargs)

    def post(self, *args: Any, **kwargs: Any) -> httpx.Response:
        """Send POST request."""
        return self._client.post(*args, **kwargs)

    def put(self, *args: Any, **kwargs: Any) -> httpx.Response:
        """Send PUT request."""
        return self._client.put(*args, **kwargs)

    def delete(self, *args: Any, **kwargs: Any) -> httpx.Response:
        """Send DELETE request."""
        return self._client.delete(*args, **kwargs)

    def patch(self, *args: Any, **kwargs: Any) -> httpx.Response:
        """Send PATCH request."""
        return self._client.patch(*args, **kwargs)

    def close(self) -> None:
        """Close client."""
        self._client.close()


class AsyncHTTPClient:
    """Async HTTP client wrapper."""

    def __init__(self, config: HTTPClientConfig) -> None:
        """Initialize client.

        Args:
            config: HTTP client configuration
        """
        self._config = config
        self._client = httpx.AsyncClient(
            timeout=config.timeout,
            verify=config.verify_ssl,
            headers=config.headers,
        )

    async def __aenter__(self) -> "AsyncHTTPClient":
        """Enter async context manager.

        Returns:
            AsyncHTTPClient: Self
        """
        return self

    async def __aexit__(
        self,
        exc_type: Optional[Type[BaseException]],
        exc_val: Optional[BaseException],
        exc_tb: Optional[TracebackType],
    ) -> None:
        """Exit async context manager.

        Args:
            exc_type: Exception type
            exc_val: Exception value
            exc_tb: Exception traceback
        """
        await self.close()

    async def request(
        self,
        method: str,
        url: str,
        *,
        params: Optional[Dict[str, Any]] = None,
        json: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, Any]] = None,
        **kwargs: Any,
    ) -> httpx.Response:
        """Send HTTP request.

        Args:
            method: HTTP method.
            url: Request URL.
            params: Query parameters.
            json: JSON body.
            headers: Request headers.
            **kwargs: Additional arguments.

        Returns:
            httpx.Response: HTTP response.
        """
        method = method.upper()
        request_method = getattr(self._client, method.lower(), None)
        if request_method is None:
            raise ValueError(f"Unsupported HTTP method: {method}")
        return await request_method(url, params=params, json=json, headers=headers, **kwargs)

    async def get(self, *args: Any, **kwargs: Any) -> httpx.Response:
        """Send GET request."""
        return await self._client.get(*args, **kwargs)

    async def post(self, *args: Any, **kwargs: Any) -> httpx.Response:
        """Send POST request."""
        return await self._client.post(*args, **kwargs)

    async def put(self, *args: Any, **kwargs: Any) -> httpx.Response:
        """Send PUT request."""
        return await self._client.put(*args, **kwargs)

    async def delete(self, *args: Any, **kwargs: Any) -> httpx.Response:
        """Send DELETE request."""
        return await self._client.delete(*args, **kwargs)

    async def patch(self, *args: Any, **kwargs: Any) -> httpx.Response:
        """Send PATCH request."""
        return await self._client.patch(*args, **kwargs)

    async def close(self) -> None:
        """Close client."""
        await self._client.aclose()
