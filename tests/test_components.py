"""Tests for core components."""

# Import built-in modules
from typing import Any, Dict
from unittest.mock import AsyncMock, Mock

import httpx

# Import third-party modules
import pytest

# Import local modules
from notify_bridge.components import BaseNotifier, EmailNotifier, WebhookNotifier
from notify_bridge.exceptions import NotificationError
from notify_bridge.schema import EmailSchema, NotificationResponse, WebhookSchema


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
        return NotificationResponse(
            success=True,
            name=self.name,
            message="Notification sent successfully"
        ).model_dump()

    async def _send_async(self, schema: WebhookSchema) -> Dict[str, Any]:
        """Send notification asynchronously."""
        return NotificationResponse(
            success=True,
            name=self.name,
            message="Notification sent successfully"
        ).model_dump()

    def build_payload(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Build test payload."""
        notification = self.validate(data)
        return {
            "url": notification.url,
            "json": {
                "content": notification.content,
                "title": notification.title
            }
        }


class TestEmailNotifier(EmailNotifier):
    """Test email notifier implementation."""

    name = "test_email"

    def _send_email(self, schema: EmailSchema) -> Dict[str, Any]:
        """Send email notification synchronously."""
        return NotificationResponse(
            success=True,
            name=self.name,
            message="Notification sent successfully"
        ).model_dump()

    async def _send_email_async(self, schema: EmailSchema) -> Dict[str, Any]:
        """Send email notification asynchronously."""
        return NotificationResponse(
            success=True,
            name=self.name,
            message="Notification sent successfully"
        ).model_dump()


@pytest.fixture
def mock_http_client() -> httpx.Client:
    """Create mock HTTP client."""
    client = Mock(spec=httpx.Client)
    response = Mock(
        status_code=200,
        json=lambda: {"success": True},
        raise_for_status=lambda: None
    )
    client.request.return_value = response
    return client


@pytest.fixture
def mock_async_http_client() -> httpx.AsyncClient:
    """Create mock async HTTP client."""
    client = AsyncMock(spec=httpx.AsyncClient)
    response = Mock(
        status_code=200,
        json=lambda: {"success": True},
        raise_for_status=lambda: None
    )
    client.request.return_value = response
    return client


@pytest.fixture
def base_notifier(mock_http_client: httpx.Client, mock_async_http_client: httpx.AsyncClient) -> BaseNotifier:
    """Create base notifier fixture."""
    notifier = TestNotifier()
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
        "url": "https://example.com",
        "title": "Test Title",
        "content": "Test Content",
        "msg_type": "text",
        "method": "POST",
        "webhook_url": "https://example.com",
        "headers": {},
        "timeout": 10,
        "verify_ssl": True
    }


@pytest.fixture
def email_data() -> Dict[str, Any]:
    """Create email data fixture."""
    return {
        "url": "https://example.com",
        "title": "Test Email",
        "content": "Test Content",
        "msg_type": "text",
        "subject": "Test Subject",
        "from_email": "sender@example.com",
        "to_emails": ["test@example.com"],
        "html_content": "<p>Test Content</p>"
    }


@pytest.fixture
def email_notifier(mock_http_client: httpx.Client, mock_async_http_client: httpx.AsyncClient) -> EmailNotifier:
    """Create email notifier fixture."""
    notifier = TestEmailNotifier()
    notifier._http_client = mock_http_client
    notifier._async_http_client = mock_async_http_client
    return notifier


def test_base_notifier_notify(base_notifier: BaseNotifier, test_data: Dict[str, Any]) -> None:
    """Test base notifier notify method."""
    response = base_notifier.notify(test_data)
    assert response["success"] is True
    assert response["name"] == "test"
    assert response["message"] == "Notification sent successfully"


@pytest.mark.asyncio
async def test_base_notifier_notify_async(base_notifier: BaseNotifier, test_data: Dict[str, Any]) -> None:
    """Test base notifier notify_async method."""
    response = await base_notifier.notify_async(test_data)
    assert response["success"] is True
    assert response["name"] == "test"
    assert response["message"] == "Notification sent successfully"


def test_webhook_notifier_notify(webhook_notifier: WebhookNotifier, test_data: Dict[str, Any]) -> None:
    """Test webhook notifier notify method."""
    response = webhook_notifier.send(test_data)
    assert response["success"] is True
    assert response["name"] == "webhook"
    assert response["message"] == "Notification sent successfully"


@pytest.mark.asyncio
async def test_webhook_notifier_notify_async(webhook_notifier: WebhookNotifier, test_data: Dict[str, Any]) -> None:
    """Test webhook notifier notify_async method."""
    response = await webhook_notifier.notify_async(test_data)
    assert response["success"] is True
    assert response["name"] == "webhook"
    assert response["message"] == "Notification sent successfully"


def test_webhook_notifier_http_error(webhook_notifier: WebhookNotifier, test_data: Dict[str, Any]) -> None:
    """Test webhook notification with HTTP error."""
    webhook_notifier._http_client.request.side_effect = httpx.HTTPError("HTTP error")
    with pytest.raises(NotificationError):
        webhook_notifier.send(test_data)


@pytest.mark.asyncio
async def test_webhook_notifier_http_error_async(webhook_notifier: WebhookNotifier, test_data: Dict[str, Any]) -> None:
    """Test asynchronous webhook notification with HTTP error."""
    webhook_notifier._async_http_client.request.side_effect = httpx.HTTPError("HTTP error")
    with pytest.raises(NotificationError):
        await webhook_notifier.notify_async(test_data)


def test_email_notifier_notify(email_notifier: EmailNotifier, email_data: Dict[str, Any]) -> None:
    """Test email notification."""
    response = email_notifier.send(email_data)
    assert response["success"] is True
    assert response["name"] == "test_email"
    assert response["message"] == "Notification sent successfully"


@pytest.mark.asyncio
async def test_email_notifier_notify_async(email_notifier: EmailNotifier, email_data: Dict[str, Any]) -> None:
    """Test asynchronous email notification."""
    response = await email_notifier.notify_async(email_data)
    assert response["success"] is True
    assert response["name"] == "test_email"
    assert response["message"] == "Notification sent successfully"
