"""Tests for core components."""

# Import built-in modules
from typing import Any, Dict
from unittest.mock import AsyncMock, Mock

# Import third-party modules
import httpx
import pytest

# Import local modules
from notify_bridge.components import BaseNotifier
from notify_bridge.schema import NotificationResponse, WebhookSchema


class TestSchema(WebhookSchema):
    """Test data schema."""

    method: str = "POST"
    webhook_url: str = "https://example.com"
    headers: Dict[str, str] = {}
    timeout: int = 10
    verify_ssl: bool = True


class TestNotifier(BaseNotifier):
    """Test notifier implementation."""

    name = "test"
    schema_class = WebhookSchema

    def assemble_data(self, data: WebhookSchema) -> Dict[str, Any]:
        """Assemble data data.

        Args:
            data: Notification data.

        Returns:
            Dict[str, Any]: API payload.
        """
        data = self.validate(data)
        return data.to_payload()

    async def _send_async(self, schema: WebhookSchema) -> Dict[str, Any]:
        """Send data asynchronously."""
        return NotificationResponse(success=True, name=self.name, message="Notification sent successfully").model_dump()

    def _send(self, schema: WebhookSchema) -> Dict[str, Any]:
        """Send data synchronously."""
        return NotificationResponse(success=True, name=self.name, message="Notification sent successfully").model_dump()


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


def test_schema_populate_by_name():
    """Test that schema accepts both field name and alias.

    The content field has alias="message", so both should work:
    - content="Test" (field name)
    - message="Test" (alias)
    """
    # Test using alias (message=)
    schema1 = WebhookSchema(
        webhook_url="https://example.com",
        message="Test via alias",
    )
    assert schema1.content == "Test via alias"

    # Test using field name (content=)
    schema2 = WebhookSchema(
        webhook_url="https://example.com",
        content="Test via field name",
    )
    assert schema2.content == "Test via field name"

    # Test dict with field name
    schema3 = WebhookSchema(
        **{
            "webhook_url": "https://example.com",
            "content": "Test via dict field name",
        }
    )
    assert schema3.content == "Test via dict field name"

    # Test dict with alias
    schema4 = WebhookSchema(
        **{
            "webhook_url": "https://example.com",
            "message": "Test via dict alias",
        }
    )
    assert schema4.content == "Test via dict alias"
