"""Tests for core components."""

# Import built-in modules
from typing import Any, Dict

import httpx

# Import third-party modules
import pytest
from unittest.mock import AsyncMock

# Import local modules
from notify_bridge.components import BaseNotifier, EmailNotifier, WebhookNotifier
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

    def build_payload(self, notification: WebhookSchema) -> Dict[str, Any]:
        """Build notification payload.

        Args:
            notification: Notification data.

        Returns:
            Dict[str, Any]: API payload.
        """
        notification = self.validate(notification)
        return {
            "url": notification.webhook_url,
            "json": {
                "content": notification.content,
                "title": notification.title
            }
        }


class TestEmailNotifier(EmailNotifier):
    """Test email notifier implementation."""

    name = "test_email"
    schema_class = EmailSchema

    def _send_email(self, schema: EmailSchema) -> Dict[str, Any]:
        """Send email notification synchronously."""
        return NotificationResponse(
            success=True,
            name=self.name,
            message="Email sent successfully"
        ).model_dump()

    async def _send_email_async(self, schema: EmailSchema) -> Dict[str, Any]:
        """Send email notification asynchronously."""
        return NotificationResponse(
            success=True,
            name=self.name,
            message="Email sent successfully"
        ).model_dump()

    def build_payload(self, notification: EmailSchema) -> Dict[str, Any]:
        """Build email notification payload.

        Args:
            notification: Email notification data.

        Returns:
            Dict[str, Any]: API payload.
        """
        notification = self.validate(notification)
        payload = {
            "subject": notification.subject,
            "from_email": notification.from_email,
            "to_emails": notification.to_emails,
            "content": notification.content,
            "title": notification.title,
            "webhook_url": notification.webhook_url
        }
        if notification.html_content:
            payload["html_content"] = notification.html_content
        return payload


@pytest.fixture
def mock_http_client(mocker: pytest.FixtureRequest) -> httpx.Client:
    """Mock HTTP client."""
    mock_response = mocker.Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"message": "success"}
    mock_response.raise_for_status.return_value = None

    mock_client = mocker.Mock(spec=httpx.Client)
    mock_client.request.return_value = mock_response
    mock_client.__enter__ = mocker.Mock(return_value=mock_client)
    mock_client.__exit__ = mocker.Mock(return_value=None)
    return mock_client


@pytest.fixture
def mock_async_http_client(mocker: pytest.FixtureRequest) -> httpx.AsyncClient:
    """Mock async HTTP client."""
    mock_response = mocker.AsyncMock()
    mock_response.status_code = 200
    mock_response.json = mocker.AsyncMock(return_value={"message": "success"})
    mock_response.raise_for_status.return_value = None

    mock_client = mocker.AsyncMock(spec=httpx.AsyncClient)
    mock_client.request.return_value = mock_response
    mock_client.__aenter__ = mocker.AsyncMock(return_value=mock_client)
    mock_client.__aexit__ = mocker.AsyncMock(return_value=None)
    return mock_client


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
    """Email notification test data."""
    return {
        "msg_type": "text",
        "content": "Test Content",
        "title": "Test Title",
        "from_email": "sender@example.com",
        "to_emails": ["recipient@example.com"],
        "subject": "Test Subject",
        "html_content": "<p>Test Content</p>",
        "webhook_url": "https://api.example.com/email",
        "headers": {}
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
    response = base_notifier.send(test_data)
    assert response["success"] is True
    assert response["name"] == "test"
    assert response["message"] == "Notification sent successfully"


@pytest.mark.asyncio
async def test_base_notifier_notify_async() -> None:
    """Test BaseNotifier notify_async method."""
    base_notifier = BaseNotifier()
    test_data = {
        "message": "Test message",  # Using alias for content
        "title": "Test title",
        "webhook_url": "https://example.com/webhook"
    }

    # Create mock response with proper async behavior
    mock_response = AsyncMock()
    mock_response.status_code = 200
    mock_response.raise_for_status = AsyncMock()
    mock_response.json = AsyncMock(return_value={"result": "success"})
    
    # Mock the request method
    base_notifier._async_http_client = AsyncMock()
    base_notifier._async_http_client.__aenter__ = AsyncMock(return_value=base_notifier._async_http_client)
    base_notifier._async_http_client.__aexit__ = AsyncMock()
    base_notifier._async_http_client.request = AsyncMock(return_value=mock_response)

    # Test successful notification
    response = await base_notifier.send_async(test_data)
    
    # Verify response
    assert response["success"] is True
    assert response["name"] == ""  # BaseNotifier has empty name
    assert response["message"] == "Notification sent successfully"
    assert response["data"] == {"result": "success"}

    # Verify request was made correctly
    base_notifier._async_http_client.request.assert_called_once_with(
        method="POST",
        url="https://example.com/webhook",
        headers={"Content-Type": "application/json"},
        json={
            "msg_type": "text",
            "content": {
                "text": "Test message"
            }
        }
    )


@pytest.mark.asyncio
async def test_webhook_notifier_notify_async() -> None:
    """Test WebhookNotifier notify_async method."""
    webhook_notifier = WebhookNotifier()
    test_data = {
        "message": "Test message",  # Using alias for content
        "title": "Test title",
        "webhook_url": "https://example.com/webhook"
    }

    # Create mock response with proper async behavior
    mock_response = AsyncMock()
    mock_response.status_code = 200
    mock_response.raise_for_status = AsyncMock()
    mock_response.json = AsyncMock(return_value={"result": "success"})
    
    # Mock the request method
    webhook_notifier._async_http_client = AsyncMock()
    webhook_notifier._async_http_client.__aenter__ = AsyncMock(return_value=webhook_notifier._async_http_client)
    webhook_notifier._async_http_client.__aexit__ = AsyncMock()
    webhook_notifier._async_http_client.request = AsyncMock(return_value=mock_response)

    # Test successful notification
    response = await webhook_notifier.send_async(test_data)
    
    # Verify response
    assert response["success"] is True
    assert response["name"] == "webhook"
    assert response["message"] == "Notification sent successfully"
    assert response["data"] == {"result": "success"}


@pytest.mark.asyncio
async def test_email_notifier_notify_async() -> None:
    """Test EmailNotifier notify_async method."""
    email_notifier = EmailNotifier()
    email_data = {
        "message": "Test message",  # Using alias for content
        "title": "Test title",
        "webhook_url": "https://example.com/webhook",
        "subject": "Test Subject",
        "from_email": "test@example.com",
        "to_emails": ["recipient@example.com"],
        "html_content": "<p>Test HTML content</p>"
    }

    # Create mock response with proper async behavior
    mock_response = AsyncMock()
    mock_response.status_code = 200
    mock_response.raise_for_status = AsyncMock()
    mock_response.json = AsyncMock(return_value={"result": "success"})
    
    # Mock the request method
    email_notifier._async_http_client = AsyncMock()
    email_notifier._async_http_client.__aenter__ = AsyncMock(return_value=email_notifier._async_http_client)
    email_notifier._async_http_client.__aexit__ = AsyncMock()
    email_notifier._async_http_client.request = AsyncMock(return_value=mock_response)

    # Test successful notification
    response = await email_notifier.send_async(email_data)
    
    # Verify response
    assert response["success"] is True
    assert response["name"] == "email"
    assert response["message"] == "Notification sent successfully"
    assert response["data"] == {"result": "success"}


def test_webhook_notifier_notify(webhook_notifier: WebhookNotifier, test_data: Dict[str, Any]) -> None:
    """Test webhook notifier notify method."""
    response = webhook_notifier.send(test_data)
    assert response["success"] is True
    assert response["name"] == "webhook"
    assert response["message"] == "Notification sent successfully"


@pytest.mark.asyncio
async def test_webhook_notifier_notify_async(webhook_notifier: WebhookNotifier, test_data: Dict[str, Any]) -> None:
    """Test webhook notifier notify_async method."""
    response = await webhook_notifier.send_async(test_data)
    assert response["success"] is True
    assert response["name"] == "webhook"
    assert response["message"] == "Notification sent successfully"


def test_webhook_notifier_http_error(webhook_notifier: WebhookNotifier, test_data: Dict[str, Any]) -> None:
    """Test webhook notification with HTTP error."""
    webhook_notifier._http_client.request.side_effect = httpx.HTTPError("HTTP error")
    response = webhook_notifier.send(test_data)
    assert response["success"] is False
    assert "Failed to send notification" in response["message"]


@pytest.mark.asyncio
async def test_webhook_notifier_http_error_async(webhook_notifier: WebhookNotifier, test_data: Dict[str, Any]) -> None:
    """Test asynchronous webhook notification with HTTP error."""
    webhook_notifier._async_http_client.request.side_effect = httpx.HTTPError("HTTP error")
    response = await webhook_notifier.send_async(test_data)
    assert response["success"] is False
    assert "Failed to send notification" in response["message"]


def test_email_notifier_notify(email_notifier: EmailNotifier, email_data: Dict[str, Any]) -> None:
    """Test email notification."""
    response = email_notifier.send(email_data)
    assert response["success"] is True
    assert response["name"] == "test_email"
    assert response["message"] == "Email sent successfully"


@pytest.mark.asyncio
async def test_email_notifier_notify_async(email_notifier: EmailNotifier, email_data: Dict[str, Any]) -> None:
    """Test asynchronous email notification."""
    response = await email_notifier.send_async(email_data)
    assert response["success"] is True
    assert response["name"] == "test_email"
    assert response["message"] == "Email sent successfully"


def test_email_notifier_error(email_notifier: EmailNotifier, email_data: Dict[str, Any]) -> None:
    """Test email notification with error."""
    email_notifier._http_client.request.side_effect = httpx.HTTPError("HTTP error")
    response = email_notifier.send(email_data)
    assert response["success"] is False
    assert "Failed to send email" in response["message"]


@pytest.mark.asyncio
async def test_email_notifier_error_async(email_notifier: EmailNotifier, email_data: Dict[str, Any]) -> None:
    """Test asynchronous email notification with error."""
    email_notifier._async_http_client.request.side_effect = httpx.HTTPError("HTTP error")
    response = await email_notifier.send_async(email_data)
    assert response["success"] is False
    assert "Failed to send email" in response["message"]
