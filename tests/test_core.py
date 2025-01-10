"""Tests for core functionality."""

# Import built-in modules

# Import third-party modules
import pytest

# Import local modules
from notify_bridge import NotifyBridge
from notify_bridge.exceptions import NoSuchNotifierError
from notify_bridge.types import BaseNotifier, NotificationResponse, NotificationSchema


class TestSchema(NotificationSchema):
    """Test notification schema."""

    title: str
    body: str
    msg_type: str


class TestNotifier(BaseNotifier):
    """Test notifier implementation."""

    name = "test"
    schema = TestSchema

    def notify(self, notification: NotificationSchema) -> NotificationResponse:
        """Send a notification synchronously."""
        data = notification.model_dump()
        return NotificationResponse(True, self.name, data, {"status": "sent"})

    async def send(self, notification: NotificationSchema) -> NotificationResponse:
        """Send a notification.

        Args:
            notification: The notification data.

        Returns:
            NotificationResponse: The response from the notification attempt.
        """
        data = notification.model_dump()
        return NotificationResponse(True, self.name, data, {"status": "sent"})

    async def asend(self, notification: NotificationSchema) -> NotificationResponse:
        """Send a notification asynchronously.

        Args:
            notification: The notification data.

        Returns:
            NotificationResponse: The response from the notification attempt.
        """
        return await self.send(notification)


@pytest.fixture
def notifier():
    """Create a TestNotifier instance."""
    return TestNotifier()


@pytest.fixture
def bridge():
    """Create a NotifyBridge instance."""
    return NotifyBridge()


def test_register_notifier(bridge: NotifyBridge, notifier: TestNotifier):
    """Test registering a notifier."""
    bridge.add_notifier(notifier)
    assert "test" in bridge.get_registered_notifiers()


def test_unregister_notifier(bridge: NotifyBridge, notifier: TestNotifier):
    """Test unregistering a notifier."""
    bridge.add_notifier(notifier)
    bridge.remove_notifier("test")
    assert "test" not in bridge.get_registered_notifiers()


def test_notify(bridge: NotifyBridge, notifier: TestNotifier):
    """Test sending a notification."""
    bridge.add_notifier(notifier)
    response = bridge.notify(
        "test",
        title="Test Title",
        body="Test Body",
        msg_type="text",
    )
    assert response.success
    assert response.notifier == "test"


def test_notify_validation_error(bridge: NotifyBridge, notifier: TestNotifier):
    """Test sending a notification with invalid data."""
    bridge.add_notifier(notifier)
    with pytest.raises(ValueError):
        bridge.notify(
            "test",
            invalid_field="Invalid",
        )


@pytest.mark.asyncio
async def test_anotify(bridge: NotifyBridge, notifier: TestNotifier):
    """Test sending a notification asynchronously."""
    bridge.add_notifier(notifier)
    response = await bridge.anotify(
        "test",
        title="Test Title",
        body="Test Body",
        msg_type="text",
    )
    assert response.success
    assert response.notifier == "test"


@pytest.mark.asyncio
async def test_anotify_validation_error(bridge: NotifyBridge, notifier: TestNotifier):
    """Test sending a notification asynchronously with invalid data."""
    bridge.add_notifier(notifier)
    with pytest.raises(ValueError):
        await bridge.anotify(
            "test",
            invalid_field="Invalid",
        )


def test_notifier_not_found(bridge: NotifyBridge):
    """Test handling of non-existent notifier."""
    with pytest.raises(NoSuchNotifierError):
        bridge.notify(
            "nonexistent",
            title="Test Title",
            body="Test Body",
            msg_type="text",
        )


@pytest.mark.asyncio
async def test_notifier_not_found_async(bridge: NotifyBridge):
    """Test handling of non-existent notifier asynchronously."""
    with pytest.raises(NoSuchNotifierError):
        await bridge.anotify(
            "nonexistent",
            title="Test Title",
            body="Test Body",
            msg_type="text",
        )
