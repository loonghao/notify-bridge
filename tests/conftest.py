"""Common test fixtures."""

# Import third-party modules
import pytest

# Import local modules
from notify_bridge.types import BaseNotifier, NotificationResponse, NotificationSchema


class TestSchema(NotificationSchema):
    """Test notification schema."""


class TestNotifier(BaseNotifier):
    """Test notifier implementation."""

    name = "test"
    schema = TestSchema

    def send(self, notification: NotificationSchema) -> NotificationResponse:
        """Send a notification."""
        return NotificationResponse(True, self.name, notification.model_dump())

    async def asend(self, notification: NotificationSchema) -> NotificationResponse:
        """Send a notification asynchronously."""
        return NotificationResponse(True, self.name, notification.model_dump())

    def close(self) -> None:
        """Close any resources held by the notifier."""

    async def aclose(self) -> None:
        """Close any resources held by the notifier asynchronously."""


@pytest.fixture
def test_schema():
    """Create a test schema instance."""
    return TestSchema


@pytest.fixture
def test_notifier():
    """Create a test notifier instance."""
    return TestNotifier
