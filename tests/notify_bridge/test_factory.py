"""Tests for notifier factory."""

# Import built-in modules
from typing import Any, Dict

# Import third-party modules
import pytest

# Import local modules
from notify_bridge.exceptions import ValidationError
from notify_bridge.factory import NotifierFactory
from notify_bridge.types import BaseNotifier, NotificationResponse, NotificationSchema


class TestSchema(NotificationSchema):
    """Test notification schema."""

    webhook_url: str = "https://example.com/webhook"
    msg_type: str = "text"
    title: str
    body: str


class TestNotifier(BaseNotifier):
    """Test notifier implementation."""

    name = "test"
    schema = TestSchema

    def notify(self, notification: Dict[str, Any]) -> NotificationResponse:
        """Send a notification."""
        if not isinstance(notification, (dict, TestSchema)):
            raise ValueError("Invalid notification")
        if isinstance(notification, dict):
            try:
                notification = TestSchema(**notification)
            except Exception as e:
                raise ValueError(f"Invalid notification: {e}")
        return NotificationResponse(True, self.name, notification.model_dump(), {"status": "sent"})

    async def send(self, notification: Dict[str, Any]) -> NotificationResponse:
        """Send a notification."""
        return self.notify(notification)

    async def asend(self, notification: Dict[str, Any]) -> NotificationResponse:
        """Send a notification asynchronously."""
        return await self.send(notification)


@pytest.fixture
def factory() -> NotifierFactory:
    """Create a notifier factory."""
    return NotifierFactory()


@pytest.fixture
def notifier() -> TestNotifier:
    """Create a test notifier."""
    return TestNotifier()


def test_register_notifier(factory: NotifierFactory):
    """Test registering a notifier."""
    factory.register_notifier("test", TestNotifier)
    assert factory.get_notifier_class("test") == TestNotifier


def test_unregister_notifier(factory: NotifierFactory):
    """Test unregistering a notifier."""
    factory.register_notifier("test", TestNotifier)
    factory.unregister_notifier("test")
    assert factory.get_notifier_class("test") is None


def test_get_notifier_names(factory: NotifierFactory):
    """Test getting notifier names."""
    factory.register_notifier("test", TestNotifier)
    assert "test" in factory.get_notifier_names()


def test_get_notifier_class(factory: NotifierFactory):
    """Test getting a notifier class."""
    factory.register_notifier("test", TestNotifier)
    assert factory.get_notifier_class("test") == TestNotifier


def test_create_notifier(factory: NotifierFactory):
    """Test creating a notifier."""
    factory.register_notifier("test", TestNotifier)
    notifier = factory.create_notifier("test")
    assert isinstance(notifier, TestNotifier)


def test_notify_success(factory: NotifierFactory, notifier: TestNotifier):
    """Test successful notification."""
    factory.register_notifier("test", TestNotifier)
    notification = TestSchema(
        title="Test Title",
        body="Test Body",
        msg_type="text",
    )
    response = factory.notify("test", notification)
    assert response.success
    assert response.notifier == "test"


def test_notify_validation_error(factory: NotifierFactory):
    """Test notification with validation error."""
    factory.register_notifier("test", TestNotifier)
    with pytest.raises(ValidationError):
        factory.notify("test", {"invalid_field": "Invalid"})


@pytest.mark.asyncio
async def test_anotify_success(factory: NotifierFactory, notifier: TestNotifier):
    """Test successful async notification."""
    factory.register_notifier("test", TestNotifier)
    notification = TestSchema(
        title="Test Title",
        body="Test Body",
        msg_type="text",
    )
    response = await factory.anotify("test", notification)
    assert response.success
    assert response.notifier == "test"


@pytest.mark.asyncio
async def test_anotify_validation_error(factory: NotifierFactory):
    """Test async notification with validation error."""
    factory.register_notifier("test", TestNotifier)
    with pytest.raises(ValidationError):
        await factory.anotify("test", {"invalid_field": "Invalid"})
