"""Tests for NotifierFactory."""

# Import built-in modules
from typing import Any, Dict

import pytest

# Import local modules
from notify_bridge.exceptions import NoSuchNotifierError, ValidationError
from notify_bridge.factory import NotifierFactory
from notify_bridge.types import BaseNotifier, NotificationResponse, NotificationSchema


class TestSchema(NotificationSchema):
    """Test schema for testing."""

    webhook_url: str
    msg_type: str


class TestNotifier(BaseNotifier):
    """Test notifier for testing."""

    name = "test"

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

    def send(self, notification: NotificationSchema) -> NotificationResponse:
        """Send a notification.

        Args:
            notification: Notification data to send.

        Returns:
            NotificationResponse: Response from the notification attempt.
        """
        return NotificationResponse(success=True, message="Test notification sent")

    async def asend(self, notification: NotificationSchema) -> NotificationResponse:
        """Send a notification asynchronously.

        Args:
            notification: Notification data to send.

        Returns:
            NotificationResponse: Response from the notification attempt.
        """
        return NotificationResponse(success=True, message="Test notification sent")


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
    response = factory.notify("test", {"title": "Test", "body": "Test message"})
    assert response.success
    assert response.message == "Test notification sent"


def test_notify_validation_error(factory: NotifierFactory) -> None:
    """Test notification validation error."""
    with pytest.raises(ValidationError):
        factory.notify("test", {})


@pytest.mark.asyncio
async def test_anotify_success(factory: NotifierFactory) -> None:
    """Test successful async notification."""
    response = await factory.anotify("test", {"title": "Test", "body": "Test message"})
    assert response.success
    assert response.message == "Test notification sent"


@pytest.mark.asyncio
async def test_anotify_validation_error(factory: NotifierFactory) -> None:
    """Test async notification validation error."""
    with pytest.raises(ValidationError):
        await factory.anotify("test", {})
