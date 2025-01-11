"""Tests for utility functions and classes."""

import logging
from unittest.mock import AsyncMock, Mock

import httpx
import pytest

from notify_bridge.utils import AsyncHTTPClient, HTTPClient, HTTPClientConfig, LogConfig, log_call, setup_logging


def test_http_client_config():
    """Test HTTP client configuration."""
    config = HTTPClientConfig(
        timeout=5.0,
        max_retries=2,
        retry_delay=0.1,
        verify_ssl=False,
        proxies={"http": "http://proxy"},
        headers={"User-Agent": "test"}
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
    return HTTPClientConfig()


@pytest.fixture
def http_client(http_client_config: HTTPClientConfig) -> HTTPClient:
    """Create HTTP client fixture."""
    client = Mock()
    client.request.return_value = Mock(
        raise_for_status=Mock(),
        json=Mock(return_value={"success": True})
    )
    return HTTPClient(http_client_config, client=client)


@pytest.fixture
def async_http_client(http_client_config: HTTPClientConfig) -> AsyncHTTPClient:
    """Create async HTTP client fixture."""
    client = AsyncMock()
    client.request.return_value = Mock(
        raise_for_status=Mock(),
        json=Mock(return_value={"success": True})
    )
    return AsyncHTTPClient(http_client_config, client=client)


def test_http_client_request_success(http_client: HTTPClient) -> None:
    """Test successful HTTP request."""
    response = http_client.request(
        method="GET",
        url="https://example.com",
        headers={"Content-Type": "application/json"},
        json={"test": "data"}
    )
    assert response == {"success": True}
    http_client._client.request.assert_called_once_with(
        "GET",
        "https://example.com",
        headers={"Content-Type": "application/json"},
        json={"test": "data"}
    )


def test_http_client_request_retry(http_client: HTTPClient) -> None:
    """Test HTTP request retry."""
    http_client._client.request.side_effect = [
        httpx.RequestError("Connection error"),
        Mock(
            raise_for_status=Mock(),
            json=Mock(return_value={"success": True})
        )
    ]
    response = http_client.request("GET", "https://example.com")
    assert response == {"success": True}
    assert http_client._client.request.call_count == 2


def test_http_client_request_max_retries_exceeded(http_client: HTTPClient) -> None:
    """Test HTTP request max retries exceeded."""
    http_client._client.request.side_effect = httpx.RequestError("Connection error")
    with pytest.raises(httpx.RequestError):
        http_client.request("GET", "https://example.com")
    assert http_client._client.request.call_count == http_client._config.max_retries


@pytest.mark.asyncio
async def test_async_http_client_request_success(async_http_client: AsyncHTTPClient) -> None:
    """Test successful async HTTP request."""
    response = await async_http_client.request(
        method="GET",
        url="https://example.com",
        headers={"Content-Type": "application/json"},
        json={"test": "data"}
    )
    assert response == {"success": True}
    async_http_client._client.request.assert_called_once_with(
        "GET",
        "https://example.com",
        headers={"Content-Type": "application/json"},
        json={"test": "data"}
    )


@pytest.mark.asyncio
async def test_async_http_client_request_retry(async_http_client: AsyncHTTPClient) -> None:
    """Test async HTTP request retry."""
    async_http_client._client.request.side_effect = [
        httpx.RequestError("Connection error"),
        Mock(
            raise_for_status=Mock(),
            json=Mock(return_value={"success": True})
        )
    ]
    response = await async_http_client.request("GET", "https://example.com")
    assert response == {"success": True}
    assert async_http_client._client.request.call_count == 2


@pytest.mark.asyncio
async def test_async_http_client_request_max_retries_exceeded(async_http_client: AsyncHTTPClient) -> None:
    """Test async HTTP request max retries exceeded."""
    async_http_client._client.request.side_effect = httpx.RequestError("Connection error")
    with pytest.raises(httpx.RequestError):
        await async_http_client.request("GET", "https://example.com")
    assert async_http_client._client.request.call_count == async_http_client._config.max_retries


def test_log_config():
    """Test log configuration."""
    config = LogConfig(
        level="DEBUG",
        format="%(message)s",
        date_format="%Y-%m-%d",
        filename="test.log",
        max_bytes=1024,
        backup_count=3
    )

    assert config.level == "DEBUG"
    assert config.format == "%(message)s"
    assert config.date_format == "%Y-%m-%d"
    assert config.filename == "test.log"
    assert config.max_bytes == 1024
    assert config.backup_count == 3


def test_setup_logging(tmp_path):
    """Test logging setup."""
    log_file = tmp_path / "test.log"
    config = LogConfig(
        level="DEBUG",
        filename=str(log_file)
    )

    setup_logging(config)
    logger = logging.getLogger()

    assert logger.level == logging.DEBUG
    assert len(logger.handlers) == 2  # Console + File handler
    assert isinstance(logger.handlers[0], logging.StreamHandler)
    assert isinstance(logger.handlers[1], logging.handlers.RotatingFileHandler)


def test_log_call_sync():
    """Test log_call decorator with synchronous function."""
    logger = logging.getLogger("test")
    logger.debug = Mock()

    @log_call(logger)
    def test_func(arg1, arg2=None):
        return arg1 + str(arg2)

    result = test_func("test", arg2=123)
    assert result == "test123"

    # Check debug logs
    assert logger.debug.call_count == 2
    logger.debug.assert_any_call(
        "Calling test_func with args=('test',), kwargs={'arg2': 123}"
    )
    logger.debug.assert_any_call("test_func returned test123")


@pytest.mark.asyncio
async def test_log_call_async():
    """Test log_call decorator with asynchronous function."""
    logger = logging.getLogger("test")
    logger.debug = Mock()

    @log_call(logger)
    async def test_func(arg1, arg2=None):
        return arg1 + str(arg2)

    result = await test_func("test", arg2=123)
    assert result == "test123"

    # Check debug logs
    assert logger.debug.call_count == 2
    logger.debug.assert_any_call(
        "Calling test_func with args=('test',), kwargs={'arg2': 123}"
    )
    logger.debug.assert_any_call("test_func returned test123")
