"""Test fixtures and utilities for notify-bridge tests."""

# Import built-in modules
from typing import Any, Dict
from unittest.mock import Mock

# Import third-party modules
import httpx
import pytest

# Import local modules
from notify_bridge.components import BaseNotifier, NotificationSchema
from notify_bridge.utils import HTTPClientConfig


class MockResponse:
    """Mock HTTP response."""

    def __init__(self, status_code: int = 200, json_data: Dict[str, Any] = None):
        """Initialize mock response.

        Args:
            status_code: HTTP status code
            json_data: JSON response data
        """
        self.status_code = status_code
        self._json_data = json_data or {}

    def json(self) -> Dict[str, Any]:
        """Get JSON response data."""
        return self._json_data

    def raise_for_status(self):
        """Raise an exception if status code indicates an error."""
        if self.status_code >= 400:
            raise httpx.HTTPStatusError("Mock HTTP error", request=Mock(), response=Mock(status_code=self.status_code))


@pytest.fixture
def mock_response() -> MockResponse:
    """Fixture for mock HTTP response."""
    return MockResponse(status_code=200, json_data={"status": "success"})


@pytest.fixture
def http_client_config() -> HTTPClientConfig:
    """Fixture for HTTP client configuration."""
    return HTTPClientConfig(timeout=5.0, max_retries=1, retry_delay=0.1, verify_ssl=False)


class TestNotifier(BaseNotifier):
    """Test notifier implementation."""

    name = "test"

    def assemble_data(self, data: NotificationSchema) -> Dict[str, Any]:
        """Build data payload.

        Args:
            data: Notification data.

        Returns:
            Dict[str, Any]: API payload.
        """
        return {"message": data.content, "title": data.title}


@pytest.fixture
def test_notifier(http_client_config: HTTPClientConfig) -> TestNotifier:
    """Fixture for test notifier class."""
    return TestNotifier(http_client_config)
