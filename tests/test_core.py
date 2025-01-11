"""Tests for core functionality."""

# Import built-in modules
from typing import Any, Dict, Optional, Union

# Import third-party modules
import pytest
import httpx
from unittest.mock import Mock

# Import local modules
from notify_bridge.core import NotifyBridge
from notify_bridge.exceptions import NoSuchNotifierError, NotificationError
from notify_bridge.types import BaseNotifier, NotificationResponse, NotificationSchema


class TestSchema(NotificationSchema):
    """Test schema for notifications."""

    url: str
    msg_type: str = "text"


class TestNotifier(BaseNotifier):
    """Test notifier for testing."""

    name = "test"
    schema = TestSchema

    def __init__(self, client: Optional[httpx.Client] = None) -> None:
        """Initialize the notifier.

        Args:
            client: HTTP client to use.
        """
        self.client = client
        self.session = Mock()

    def build_payload(self, notification: NotificationSchema) -> Dict[str, Any]:
        """Build payload for notification.

        Args:
            notification: Notification data.

        Returns:
            Dict[str, Any]: Payload for notification.
        """
        return {
            "webhook_url": notification.url,
            "json": {
                "title": notification.title,
                "body": notification.body,
                "msg_type": notification.msg_type
            }
        }

    async def build_payload_async(self, notification: NotificationSchema) -> Dict[str, Any]:
        """Build payload for async notification.

        Args:
            notification: Notification data.

        Returns:
            Dict[str, Any]: Payload for notification.
        """
        return {
            "webhook_url": notification.url,
            "json": {
                "title": notification.title,
                "body": notification.body,
                "msg_type": notification.msg_type
            }
        }

    def notify(self, notification: Optional[Union[NotificationSchema, Dict[str, Any]]] = None, **kwargs: Any) -> NotificationResponse:
        """Send a notification.

        Args:
            notification: Notification data.
            **kwargs: Additional arguments.

        Returns:
            NotificationResponse: Response from the notification attempt.
        """
        if notification is None:
            notification = kwargs
        if isinstance(notification, dict):
            notification = self.validate(notification)
        client = kwargs.get('client') or self.client
        if client is None:
            client = httpx.Client()
        try:
            payload = self.build_payload(notification)
            response = client.post(payload["webhook_url"], json=payload["json"])
            response.raise_for_status()
            data = response.json()
            return NotificationResponse(success=True, name=self.name, data=data)
        except Exception as e:
            raise NotificationError(str(e))

    async def anotify(self, notification: Optional[Union[NotificationSchema, Dict[str, Any]]] = None, **kwargs: Any) -> NotificationResponse:
        """Send a notification asynchronously.

        Args:
            notification: Notification data.
            **kwargs: Additional arguments.

        Returns:
            NotificationResponse: Response from the notification attempt.
        """
        if notification is None:
            notification = kwargs
        if isinstance(notification, dict):
            notification = self.validate(notification)
        client = kwargs.get('client') or self.client
        if client is None:
            client = httpx.AsyncClient()
        try:
            payload = await self.build_payload_async(notification)
            response = await client.post(payload["webhook_url"], json=payload["json"])
            response.raise_for_status()
            data = response.json()
            return NotificationResponse(success=True, name=self.name, data=data)
        except Exception as e:
            raise NotificationError(str(e))


@pytest.fixture
def bridge():
    """Create a NotifyBridge instance."""
    bridge = NotifyBridge()
    bridge._factory.register_notifier("test", TestNotifier)
    return bridge


@pytest.mark.asyncio
async def test_anotify(bridge: NotifyBridge) -> None:
    """Test async notification."""
    def mock_transport(request):
        if request.method == "POST":
            return httpx.Response(200, json={"success": True})
        return httpx.Response(405)
    
    transport = httpx.MockTransport(mock_transport)
    client = httpx.AsyncClient(transport=transport)
    response = await bridge.anotify("test", {"url": "https://example.com", "title": "Test", "body": "Test message"}, client=client)
    assert response.success
    assert response.name == "test"
    assert response.data["success"] is True

def test_notify(bridge: NotifyBridge) -> None:
    """Test notification."""
    def mock_transport(request):
        if request.method == "POST":
            return httpx.Response(200, json={"success": True})
        return httpx.Response(405)
    
    transport = httpx.MockTransport(mock_transport)
    client = httpx.Client(transport=transport)
    response = bridge.notify("test", {"url": "https://example.com", "title": "Test", "body": "Test message"}, client=client)
    assert response.success is True
    assert response.name == "test"

def test_notify_invalid_notifier(bridge: NotifyBridge) -> None:
    """Test notification with invalid notifier."""
    with pytest.raises(NoSuchNotifierError):
        bridge.notify("invalid", {"url": "http://test.com", "title": "Test", "body": "Test message"})

@pytest.mark.asyncio
async def test_anotify_invalid_notifier(bridge: NotifyBridge) -> None:
    """Test async notification with invalid notifier."""
    with pytest.raises(NoSuchNotifierError):
        await bridge.anotify("invalid", {"url": "http://test.com", "title": "Test", "body": "Test message"})
