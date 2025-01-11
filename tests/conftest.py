"""Test fixtures and utilities for notify-bridge tests."""

# Import third-party modules
from typing import Any, Dict
from unittest.mock import Mock

import httpx
import pytest
from notify_bridge.components import BaseNotifier, EmailNotifier, WebhookNotifier

# Import local modules
from notify_bridge.schema import EmailSchema, NotificationResponse
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
            raise httpx.HTTPStatusError(
                "Mock HTTP error",
                request=Mock(),
                response=Mock(status_code=self.status_code)
            )


@pytest.fixture
def mock_response() -> MockResponse:
    """Fixture for mock HTTP response."""
    return MockResponse(
        status_code=200,
        json_data={"status": "success"}
    )


@pytest.fixture
def mock_http_client(mock_response: MockResponse) -> Mock:
    """Fixture for mock HTTP client."""
    client = Mock()
    client.request.return_value = mock_response
    return client


@pytest.fixture
def http_client_config() -> HTTPClientConfig:
    """Fixture for HTTP client configuration."""
    return HTTPClientConfig(
        timeout=5.0,
        max_retries=2,
        retry_delay=0.1
    )


class TestNotifier(BaseNotifier):
    """Test notifier implementation."""

    name = "test"

    def notify(self, notification: Dict[str, Any]) -> Dict[str, Any]:
        """Send notification synchronously."""
        return NotificationResponse(
            success=True,
            name=self.name,
            data=notification
        ).model_dump()

    async def notify_async(self, notification: Dict[str, Any]) -> Dict[str, Any]:
        """Send notification asynchronously."""
        return NotificationResponse(
            success=True,
            name=self.name,
            data=notification
        ).model_dump()


class TestWebhookNotifier(WebhookNotifier):
    """Test webhook notifier implementation."""

    name = "test_webhook"


class TestEmailNotifier(EmailNotifier):
    """Test email notifier implementation."""

    name = "test_email"

    def _send_email(self, schema: EmailSchema) -> Dict[str, Any]:
        """Mock synchronous email send."""
        return NotificationResponse(
            success=True,
            name=self.name,
            data=schema.model_dump()
        ).model_dump()

    async def _send_email_async(self, schema: EmailSchema) -> Dict[str, Any]:
        """Mock asynchronous email send."""
        return NotificationResponse(
            success=True,
            name=self.name,
            data=schema.model_dump()
        ).model_dump()


@pytest.fixture
def test_notifier() -> type[TestNotifier]:
    """Fixture for test notifier class."""
    return TestNotifier


@pytest.fixture
def test_webhook_notifier() -> type[TestWebhookNotifier]:
    """Fixture for test webhook notifier class."""
    return TestWebhookNotifier


@pytest.fixture
def test_email_notifier() -> type[TestEmailNotifier]:
    """Fixture for test email notifier class."""
    return TestEmailNotifier


@pytest.fixture
def sample_notification_data() -> Dict[str, Any]:
    """Fixture for sample notification data."""
    return {
        "url": "https://example.com",
        "content": "Test notification",
        "title": "Test Title",
        "msg_type": "text"
    }


@pytest.fixture
def sample_webhook_data() -> Dict[str, Any]:
    """Fixture for sample webhook data."""
    return {
        "url": "https://example.com/webhook",
        "content": "Test webhook notification",
        "title": "Test Title",
        "msg_type": "text",
        "webhook_url": "https://example.com/webhook",
        "method": "POST",
        "headers": {"X-Test": "test"}
    }


@pytest.fixture
def sample_email_data() -> Dict[str, Any]:
    """Fixture for sample email data."""
    return {
        "url": "https://example.com/email",
        "content": "Test email notification",
        "title": "Test Title",
        "msg_type": "text",
        "subject": "Test Subject",
        "from_email": "from@example.com",
        "to_emails": ["to@example.com"],
        "cc_emails": ["cc@example.com"],
        "bcc_emails": ["bcc@example.com"]
    }

@pytest.fixture
def notification_data():
    return {
        "url": "https://example.com",
        "title": "Test",
        "body": "Test message",
        "content": "Test content"
    }
