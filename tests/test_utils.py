"""Tests for utility functions and classes."""

import logging
from unittest.mock import AsyncMock, Mock, patch

import httpx
import pytest
import pytest_asyncio

from notify_bridge.exceptions import NotificationError
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
    return HTTPClientConfig(
        timeout=5,
        max_retries=3,
        retry_delay=0.1,
        verify_ssl=False,
        headers={"User-Agent": "Test"}
    )


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


def test_http_client_request_success(http_client: HTTPClient) -> None:
    """Test successful HTTP request."""
    mock_response = Mock()
    mock_response.raise_for_status = Mock()
    mock_response.json.return_value = {"success": True}
    http_client._client.request.return_value = mock_response

    response = http_client.request(
        method="GET",
        url="https://example.com",
        headers={"Content-Type": "application/json"},
        json={"test": "data"}
    )
    assert response.json() == {"success": True}
    http_client._client.request.assert_called_once_with(
        "GET",
        "https://example.com",
        verify=True,
        headers={"Content-Type": "application/json"},
        json={"test": "data"}
    )


def test_http_client_request_retry(http_client: HTTPClient) -> None:
    """Test HTTP request retry."""
    mock_response = Mock()
    mock_response.raise_for_status = Mock()
    mock_response.json.return_value = {"success": True}
    http_client._client.request.side_effect = [
        httpx.RequestError("Connection error"),
        mock_response
    ]
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
async def test_async_http_client_request_success(async_http_client: AsyncHTTPClient) -> None:
    """Test successful async HTTP request."""
    mock_response = AsyncMock()
    mock_response.raise_for_status = AsyncMock()
    mock_response.json = AsyncMock(return_value={"success": True})
    async_http_client._client.request = AsyncMock(return_value=mock_response)

    response = await async_http_client.request(
        method="GET",
        url="https://example.com",
        headers={"Content-Type": "application/json"},
        json={"test": "data"}
    )
    assert await response.json() == {"success": True}
    async_http_client._client.request.assert_called_once_with(
        "GET",
        "https://example.com",
        headers={"Content-Type": "application/json"},
        json={"test": "data"}
    )


@pytest.mark.asyncio
async def test_async_http_client_request_retry(async_http_client: AsyncHTTPClient) -> None:
    """Test async HTTP request retry."""
    mock_response = AsyncMock()
    mock_response.raise_for_status = AsyncMock()
    mock_response.json = AsyncMock(return_value={"success": True})
    async_http_client._client.request = AsyncMock(side_effect=[
        httpx.RequestError("Connection error"),
        mock_response
    ])
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


@pytest.mark.asyncio
async def test_async_http_client_request_error_handling(async_http_client: AsyncHTTPClient):
    """Test async HTTP client error handling."""
    # Test non-request error
    async_http_client._client.request = AsyncMock(side_effect=ValueError("Test error"))
    with pytest.raises(NotificationError) as exc_info:
        await async_http_client.request("GET", "https://example.com")
    assert "Test error" in str(exc_info.value)

    # Test response error
    mock_response = AsyncMock()
    mock_response.raise_for_status = AsyncMock(side_effect=httpx.HTTPStatusError(
        "404 Not Found",
        request=Mock(),
        response=Mock(status_code=404)
    ))
    async_http_client._client.request = AsyncMock(return_value=mock_response)
    with pytest.raises(NotificationError) as exc_info:
        await async_http_client.request("GET", "https://example.com")
    assert "404 Not Found" in str(exc_info.value)


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


def test_http_client_config_validation():
    """Test HTTP client configuration validation."""
    # Test invalid timeout
    with pytest.raises(ValueError, match="Timeout must be positive"):
        HTTPClientConfig(timeout=0)
    with pytest.raises(ValueError, match="Timeout must be positive"):
        HTTPClientConfig(timeout=-1)

    # Test invalid max_retries
    with pytest.raises(ValueError, match="Max retries cannot be negative"):
        HTTPClientConfig(max_retries=-1)

    # Test invalid retry_delay
    with pytest.raises(ValueError, match="Retry delay must be positive"):
        HTTPClientConfig(retry_delay=0)
    with pytest.raises(ValueError, match="Retry delay must be positive"):
        HTTPClientConfig(retry_delay=-1)


def test_log_config_validation():
    """Test log configuration validation."""
    # Test invalid log level string
    with pytest.raises(ValueError, match="Invalid log level: INVALID"):
        LogConfig(level="INVALID")

    # Test invalid log level int
    with pytest.raises(ValueError, match="Invalid log level: 999"):
        LogConfig(level=999)

    # Test invalid log level type
    with pytest.raises(ValueError) as exc_info:
        LogConfig(level=1.0)
    assert "Invalid log level: 1" in str(exc_info.value)


def test_http_client_context_manager():
    """Test HTTP client context manager."""
    config = HTTPClientConfig()
    client = HTTPClient(config)

    # Test context manager
    with client as c:
        assert c._client is not None
        assert isinstance(c._client, httpx.Client)

    # Test client is closed after context
    assert client._client is None


@pytest.mark.asyncio
async def test_async_http_client_context_manager():
    """Test async HTTP client context manager."""
    config = HTTPClientConfig()
    client = AsyncHTTPClient(config)

    # Test context manager
    async with client as c:
        assert c._client is not None
        assert isinstance(c._client, httpx.AsyncClient)

    # Test client is closed after context
    assert client._client is None


def test_http_client_request_error_handling(http_client: HTTPClient):
    """Test HTTP client error handling."""
    # Test non-request error
    http_client._client.request.side_effect = ValueError("Test error")
    with pytest.raises(NotificationError) as exc_info:
        http_client.request("GET", "https://example.com")
    assert "Test error" in str(exc_info.value)

    # Test response error
    mock_response = Mock()
    mock_response.raise_for_status.side_effect = httpx.HTTPStatusError(
        "404 Not Found",
        request=Mock(),
        response=Mock(status_code=404)
    )
    http_client._client.request.side_effect = None
    http_client._client.request.return_value = mock_response
    with pytest.raises(NotificationError) as exc_info:
        http_client.request("GET", "https://example.com")
    assert "404 Not Found" in str(exc_info.value)


def test_log_call_error_handling():
    """Test log_call decorator error handling."""
    logger = logging.getLogger("test")
    logger.debug = Mock()
    logger.exception = Mock()

    @log_call(logger)
    def test_func():
        raise ValueError("Test error")

    with pytest.raises(ValueError):
        test_func()

    assert logger.debug.call_count == 1
    assert logger.exception.call_count == 1
    logger.debug.assert_called_with(
        "Calling test_func with args=(), kwargs={}"
    )
    logger.exception.assert_called_with("test_func raised an exception")


@pytest.mark.asyncio
async def test_log_call_async_error_handling():
    """Test log_call decorator async error handling."""
    logger = logging.getLogger("test")
    logger.debug = Mock()
    logger.exception = Mock()

    @log_call(logger)
    async def test_func():
        raise ValueError("Test error")

    with pytest.raises(ValueError):
        await test_func()

    assert logger.debug.call_count == 1
    assert logger.exception.call_count == 1
    logger.debug.assert_called_with(
        "Calling test_func with args=(), kwargs={}"
    )
    logger.exception.assert_called_with("test_func raised an exception")


def test_setup_logging_default():
    """Test setup_logging with default config."""
    setup_logging()
    logger = logging.getLogger()

    assert logger.level == logging.INFO
    assert len(logger.handlers) == 1  # Console handler only
    assert isinstance(logger.handlers[0], logging.StreamHandler)


def test_setup_logging_file_creation(tmp_path):
    """Test log file creation."""
    log_dir = tmp_path / "logs"
    log_file = log_dir / "test.log"

    config = LogConfig(filename=str(log_file))
    setup_logging(config)

    assert log_dir.exists()
    assert log_file.exists()


def test_log_config_defaults():
    """Test log configuration defaults."""
    config = LogConfig()

    assert config.level == logging.INFO
    assert "%(asctime)s" in config.format
    assert config.date_format == "%Y-%m-%d %H:%M:%S"
    assert config.filename is None
    assert config.max_bytes == 10 * 1024 * 1024  # 10MB
    assert config.backup_count == 5
