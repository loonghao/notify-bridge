"""Tests for utility functions and classes."""

# Import built-in modules
from unittest.mock import AsyncMock
from unittest.mock import Mock
from unittest.mock import patch

# Import third-party modules
import httpx
import pytest
import pytest_asyncio

# Import local modules
from notify_bridge.exceptions import NotificationError
from notify_bridge.utils import AsyncHTTPClient
from notify_bridge.utils import HTTPClient
from notify_bridge.utils import HTTPClientConfig


def test_http_client_config():
    """Test HTTP client configuration."""
    config = HTTPClientConfig(
        timeout=5.0,
        max_retries=2,
        retry_delay=0.1,
        verify_ssl=False,
        proxies={"http": "http://proxy"},
        headers={"User-Agent": "test"},
    )

    assert config.timeout == 5.0
    assert config.max_retries == 2
    assert config.retry_delay == 0.1
    assert config.verify_ssl is False
    assert config.proxies == {"http": "http://proxy"}
    assert config.headers == {"User-Agent": "test"}


@pytest.fixture
def http_client_config() -> HTTPClientConfig:
    """Create HTTP client config fixture."""
    return HTTPClientConfig(timeout=5, max_retries=3, retry_delay=0.1, verify_ssl=False, headers={"User-Agent": "Test"})


@pytest.fixture
def http_client(http_client_config: HTTPClientConfig) -> HTTPClient:
    """Create HTTP client fixture."""
    with patch("httpx.Client") as mock_client:
        client = HTTPClient(http_client_config)
        mock_client.return_value.__enter__.return_value = mock_client.return_value
        with client as c:
            yield c


@pytest_asyncio.fixture
async def async_http_client(http_client_config: HTTPClientConfig) -> AsyncHTTPClient:
    """Create async HTTP client fixture."""
    with patch("httpx.AsyncClient") as mock_client:
        client = AsyncHTTPClient(http_client_config)
        mock_client.return_value = AsyncMock()
        mock_client.return_value.__aenter__.return_value = mock_client.return_value
        mock_client.return_value.aclose = AsyncMock()
        async with client as c:
            yield c


def test_http_client_request_retry(http_client: HTTPClient) -> None:
    """Test HTTP request retry."""
    mock_response = Mock()
    mock_response.raise_for_status = Mock()
    mock_response.json.return_value = {"success": True}
    http_client._client.request.side_effect = [httpx.RequestError("Connection error"), mock_response]
    response = http_client.request("GET", "https://example.com")
    assert response.json() == {"success": True}
    assert http_client._client.request.call_count == 2


def test_http_client_request_max_retries_exceeded(http_client: HTTPClient) -> None:
    """Test HTTP request max retries exceeded."""
    http_client._client.request.side_effect = httpx.RequestError("Connection error")
    with pytest.raises(NotificationError) as exc_info:
        http_client.request("GET", "https://example.com")
    assert "Connection error" in str(exc_info.value)
    assert http_client._client.request.call_count == http_client._config.max_retries


@pytest.mark.asyncio
async def test_async_http_client_request_retry(async_http_client: AsyncHTTPClient) -> None:
    """Test async HTTP request retry."""
    mock_response = AsyncMock()
    mock_response.raise_for_status = AsyncMock()
    mock_response.json = AsyncMock(return_value={"success": True})
    async_http_client._client.request = AsyncMock(side_effect=[httpx.RequestError("Connection error"), mock_response])
    response = await async_http_client.request("GET", "https://example.com")
    assert await response.json() == {"success": True}
    assert async_http_client._client.request.call_count == 2


@pytest.mark.asyncio
async def test_async_http_client_request_max_retries_exceeded(async_http_client: AsyncHTTPClient) -> None:
    """Test async HTTP request max retries exceeded."""
    async_http_client._client.request = AsyncMock(side_effect=httpx.RequestError("Connection error"))
    with pytest.raises(NotificationError) as exc_info:
        await async_http_client.request("GET", "https://example.com")
    assert "Connection error" in str(exc_info.value)
    assert async_http_client._client.request.call_count == async_http_client._config.max_retries
