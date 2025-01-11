"""Tests for NotifierFactory."""

# Import built-in modules
from typing import Any, Dict, Optional, Union

import pytest
from unittest.mock import Mock

# Import third-party modules
import httpx
import json

# Import local modules
from notify_bridge.exceptions import NoSuchNotifierError, ValidationError, NotificationError
from notify_bridge.factory import NotifierFactory
from notify_bridge.types import BaseNotifier, NotificationResponse, NotificationSchema


class TestSchema(NotificationSchema):
    """Test schema for testing."""

    url: str
    title: str
    body: str
    msg_type: str = "text"


class TestNotifier(BaseNotifier):
    """Test notifier for testing."""

    name = "test"
    schema = TestSchema

    def __init__(self, client: Any = None) -> None:
        """Initialize the notifier.

        Args:
            client: HTTP client to use.
        """
        self.client = client

    def validate(self, notification: Dict[str, Any]) -> NotificationSchema:
        """Validate notification data.

        Args:
            notification: Notification data to validate.

        Returns:
            NotificationSchema: Validated notification data.

        Raises:
            ValidationError: If notification data is invalid.
        """
        if not isinstance(notification, dict):
            raise ValidationError("Notification must be a dictionary")
        if not notification.get("title"):
            raise ValidationError("Title is required")
        if not notification.get("body"):
            raise ValidationError("Body is required")
        return super().validate(notification)

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
def factory() -> NotifierFactory:
    """Create a NotifierFactory instance for testing.

    Returns:
        NotifierFactory: Factory instance.
    """
    factory = NotifierFactory()
    factory.register_notifier("test", TestNotifier)
    return factory


def test_register_notifier(factory: NotifierFactory) -> None:
    """Test registering a notifier.

    Args:
        factory: NotifierFactory instance.
    """
    assert "test" in factory.get_notifier_names()


def test_unregister_notifier(factory: NotifierFactory) -> None:
    """Test unregistering a notifier.

    Args:
        factory: NotifierFactory instance.
    """
    factory.unregister_notifier("test")
    assert "test" not in factory.get_notifier_names()


def test_get_notifier_names(factory: NotifierFactory) -> None:
    """Test getting notifier names.

    Args:
        factory: NotifierFactory instance.
    """
    assert "test" in factory.get_notifier_names()


def test_get_notifier_class(factory: NotifierFactory) -> None:
    """Test getting a notifier class.

    Args:
        factory: NotifierFactory instance.
    """
    assert factory.get_notifier_class("test") == TestNotifier


def test_create_notifier(factory: NotifierFactory) -> None:
    """Test creating a notifier instance.

    Args:
        factory: NotifierFactory instance.
    """
    notifier = factory.create_notifier("test")
    assert isinstance(notifier, TestNotifier)


def test_create_notifier_invalid(factory: NotifierFactory) -> None:
    """Test creating an invalid notifier.

    Args:
        factory: NotifierFactory instance.
    """
    with pytest.raises(NoSuchNotifierError):
        factory.create_notifier("invalid")


def test_notify_success(factory: NotifierFactory) -> None:
    """Test successful notification."""
    transport = httpx.MockTransport(lambda _: httpx.Response(200, json={"success": True}))
    client = httpx.Client(transport=transport)
    response = factory.notify("test", {"url": "https://example.com", "title": "Test", "body": "Test message"}, client=client)
    assert response.success
    assert response.name == "test"
    assert response.data["success"] is True


@pytest.mark.asyncio
async def test_anotify_success(factory: NotifierFactory) -> None:
    """Test successful async notification."""
    def mock_transport(request):
        if request.method == "POST":
            return httpx.Response(200, json={"success": True})
        return httpx.Response(405)
    
    transport = httpx.MockTransport(mock_transport)
    async with httpx.AsyncClient(transport=transport) as client:
        response = await factory.anotify("test", {"url": "https://example.com", "title": "Test", "body": "Test message"}, client=client)
        assert response.success
        assert response.name == "test"
        assert response.data["success"] is True


@pytest.mark.asyncio
async def test_anotify_validation_error(factory: NotifierFactory) -> None:
    """Test async notification validation error."""
    with pytest.raises(ValidationError):
        await factory.anotify("test", {})
