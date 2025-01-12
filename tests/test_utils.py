"""Tests for utility functions and classes."""

# Import built-in modules
from unittest.mock import AsyncMock
from unittest.mock import patch

# Import third-party modules
import pytest
import pytest_asyncio

# Import local modules
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
        headers={"User-Agent": "test"},
    )

    assert config.timeout == 5.0
    assert config.max_retries == 2
    assert config.retry_delay == 0.1
    assert config.verify_ssl is False
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
