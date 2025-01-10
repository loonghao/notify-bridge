"""Tests for core functionality."""

# Import built-in modules
import pytest

# Import local modules
from notify_bridge import NotifyBridge
from notify_bridge.exceptions import NoSuchNotifierError
from notify_bridge.types import BaseNotifier, NotificationResponse, NotificationSchema


class TestSchema(NotificationSchema):
    """Test schema for notifications."""
    title: str
    body: str
    msg_type: str = "text"


class TestNotifier(BaseNotifier):
    """Test notifier implementation."""

    def __init__(self, **config):
        """Initialize the notifier."""
        super().__init__(**config)
        self.name = "test"

    def send(self, notification: NotificationSchema) -> NotificationResponse:
        """Send a notification."""
        if isinstance(notification, dict):
            notification = TestSchema(**notification)
        return NotificationResponse(True, self.name, notification.model_dump())

    async def asend(self, notification: NotificationSchema) -> NotificationResponse:
        """Send a notification asynchronously."""
        if isinstance(notification, dict):
            notification = TestSchema(**notification)
        return NotificationResponse(True, self.name, notification.model_dump())


@pytest.fixture
def bridge():
    """Create a test bridge instance."""
    bridge = NotifyBridge()
    bridge._notifiers["test"] = TestNotifier()
    return bridge


def test_notify(bridge):
    """Test sending a notification."""
    response = bridge.notify(
        "test",
        title="Test",
        body="Test message",
    )
    assert response.success is True
    assert response.notifier == "test"


@pytest.mark.asyncio
async def test_anotify(bridge):
    """Test sending a notification asynchronously."""
    response = await bridge.anotify(
        "test",
        title="Test",
        body="Test message",
    )
    assert response.success is True
    assert response.notifier == "test"


def test_notify_invalid_notifier(bridge):
    """Test sending a notification with an invalid notifier."""
    with pytest.raises(NoSuchNotifierError):
        bridge.notify(
            "invalid",
            title="Test",
            body="Test message",
        )


@pytest.mark.asyncio
async def test_anotify_invalid_notifier(bridge):
    """Test sending a notification with an invalid notifier asynchronously."""
    with pytest.raises(NoSuchNotifierError):
        await bridge.anotify(
            "invalid",
            title="Test",
            body="Test message",
        )
