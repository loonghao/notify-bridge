"""HTTP request utilities."""

# Import built-in modules
import json
import logging
from typing import Any, Optional

# Import third-party modules
import httpx

logger = logging.getLogger(__name__)


class RequestsHelper:
    """Helper class for making HTTP requests with both sync and async support."""

    def __init__(self, timeout: float = 30.0, verify: bool = True) -> None:
        """Initialize the request helper.

        Args:
            timeout: Request timeout in seconds
            verify: Whether to verify SSL certificates
        """
        self.timeout = timeout
        self.verify = verify
        self._async_client: Optional[httpx.AsyncClient] = None
        self._sync_client: Optional[httpx.Client] = None

    @property
    def sync_client(self) -> httpx.Client:
        """Get or create a synchronous HTTP client.

        Returns:
            httpx.Client: The synchronous HTTP client
        """
        if self._sync_client is None:
            self._sync_client = httpx.Client(timeout=self.timeout, verify=self.verify)
        return self._sync_client

    @property
    def async_client(self) -> httpx.AsyncClient:
        """Get or create an asynchronous HTTP client.

        Returns:
            httpx.AsyncClient: The asynchronous HTTP client
        """
        if self._async_client is None:
            self._async_client = httpx.AsyncClient(timeout=self.timeout, verify=self.verify)
        return self._async_client

    def _log_request(self, method: str, url: str, **kwargs: Any) -> None:
        """Log request details.

        Args:
            method: HTTP method
            url: Request URL
            **kwargs: Additional request arguments
        """
        logger.debug(f"Making {method} request to {url}")
        if "json" in kwargs:
            logger.debug(f"Request JSON: {json.dumps(kwargs['json'], ensure_ascii=False)}")
        elif "data" in kwargs:
            logger.debug(f"Request data: {kwargs['data']}")

    def _log_response(self, response: httpx.Response) -> None:
        """Log response details.

        Args:
            response: HTTP response
        """
        logger.debug(f"Response status: {response.status_code}")
        try:
            logger.debug(f"Response JSON: {json.dumps(response.json(), ensure_ascii=False)}")
        except ValueError:
            logger.debug(f"Response text: {response.text}")

    def request(self, method: str, url: str, **kwargs: Any) -> httpx.Response:
        """Make a synchronous HTTP request.

        Args:
            method: HTTP method
            url: Request URL
            **kwargs: Additional request arguments

        Returns:
            httpx.Response: The HTTP response
        """
        self._log_request(method, url, **kwargs)
        response = self.sync_client.request(method, url, **kwargs)
        self._log_response(response)
        return response

    async def arequest(self, method: str, url: str, **kwargs: Any) -> httpx.Response:
        """Make an asynchronous HTTP request.

        Args:
            method: HTTP method
            url: Request URL
            **kwargs: Additional request arguments

        Returns:
            httpx.Response: The HTTP response
        """
        self._log_request(method, url, **kwargs)
        response = await self.async_client.request(method, url, **kwargs)
        self._log_response(response)
        return response

    def get(self, url: str, **kwargs: Any) -> httpx.Response:
        """Make a synchronous GET request.

        Args:
            url: Request URL
            **kwargs: Additional request arguments

        Returns:
            httpx.Response: The HTTP response
        """
        return self.request("GET", url, **kwargs)

    async def aget(self, url: str, **kwargs: Any) -> httpx.Response:
        """Make an asynchronous GET request.

        Args:
            url: Request URL
            **kwargs: Additional request arguments

        Returns:
            httpx.Response: The HTTP response
        """
        return await self.arequest("GET", url, **kwargs)

    def post(self, url: str, **kwargs: Any) -> httpx.Response:
        """Make a synchronous POST request.

        Args:
            url: Request URL
            **kwargs: Additional request arguments

        Returns:
            httpx.Response: The HTTP response
        """
        return self.request("POST", url, **kwargs)

    async def apost(self, url: str, **kwargs: Any) -> httpx.Response:
        """Make an asynchronous POST request.

        Args:
            url: Request URL
            **kwargs: Additional request arguments

        Returns:
            httpx.Response: The HTTP response
        """
        return await self.arequest("POST", url, **kwargs)

    def close(self) -> None:
        """Close all HTTP clients."""
        if self._sync_client is not None:
            self._sync_client.close()
            self._sync_client = None

        if self._async_client is not None:
            self._async_client.aclose()
            self._async_client = None

    async def aclose(self) -> None:
        """Close all HTTP clients asynchronously."""
        if self._sync_client is not None:
            self._sync_client.close()
            self._sync_client = None

        if self._async_client is not None:
            await self._async_client.aclose()
            self._async_client = None

    def __del__(self) -> None:
        """Clean up resources when the object is deleted."""
        self.close()
