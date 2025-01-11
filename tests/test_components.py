"""Tests for core components."""

# Import built-in modules
from typing import Any
from typing import Dict
from unittest.mock import AsyncMock
from unittest.mock import Mock

# Import third-party modules
import httpx
import pytest

# Import local modules
from notify_bridge.components import BaseNotifier
from notify_bridge.components import WebhookNotifier
from notify_bridge.schema import NotificationResponse
from notify_bridge.schema import WebhookSchema


class TestSchema(WebhookSchema):
    """Test notification schema."""

    method: str = "POST"
    webhook_url: str = "https://example.com"
    headers: Dict[str, str] = {}
    timeout: int = 10
    verify_ssl: bool = True


class TestNotifier(BaseNotifier):
    """Test notifier implementation."""

    name = "test"
    schema_class = TestSchema

    def _send(self, schema: WebhookSchema) -> Dict[str, Any]:
        """Send notification synchronously."""
        return NotificationResponse(success=True, name=self.name, message="Notification sent successfully").model_dump()

    async def _send_async(self, schema: WebhookSchema) -> Dict[str, Any]:
        """Send notification asynchronously."""
        return NotificationResponse(success=True, name=self.name, message="Notification sent successfully").model_dump()

    def build_payload(self, notification: WebhookSchema) -> Dict[str, Any]:
        """Build notification payload.

        Args:
            notification: Notification data.

        Returns:
            Dict[str, Any]: API payload.
        """
        notification = self.validate(notification)
        return notification.to_payload()


@pytest.fixture
def mock_http_client(mocker: pytest.FixtureRequest) -> httpx.Client:
    """Mock HTTP client."""
    mock_client = Mock(spec=httpx.Client)
    mock_client.request = Mock()
    mock_client.__enter__ = Mock(return_value=mock_client)
    mock_client.__exit__ = Mock()
    return mock_client


@pytest.fixture
def mock_async_http_client(mocker: pytest.FixtureRequest) -> httpx.AsyncClient:
    """Mock async HTTP client."""
    mock_client = AsyncMock(spec=httpx.AsyncClient)
    mock_client.request = AsyncMock()
    mock_client.__aenter__ = AsyncMock(return_value=mock_client)
    mock_client.__aexit__ = AsyncMock()
    return mock_client


@pytest.fixture
def base_notifier(mock_http_client: httpx.Client, mock_async_http_client: httpx.AsyncClient) -> BaseNotifier:
    """Create base notifier fixture."""
    notifier = BaseNotifier()
    notifier._http_client = mock_http_client
    notifier._async_http_client = mock_async_http_client
    return notifier


@pytest.fixture
def webhook_notifier(mock_http_client: httpx.Client, mock_async_http_client: httpx.AsyncClient) -> WebhookNotifier:
    """Create webhook notifier fixture."""
    notifier = WebhookNotifier()
    notifier._http_client = mock_http_client
    notifier._async_http_client = mock_async_http_client
    return notifier


@pytest.fixture
def test_data() -> Dict[str, Any]:
    """Create test data fixture."""
    return {
        "message": "Test message",
        "title": "Test title",
        "webhook_url": "https://example.com/webhook",
        "headers": {"Content-Type": "application/json"},
        "msg_type": "text",
        "labels": ["test"],
    }
