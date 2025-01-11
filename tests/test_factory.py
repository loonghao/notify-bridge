"""Tests for NotifierFactory."""

# Import built-in modules
from typing import Any, Dict
from unittest.mock import Mock, patch

# Import third-party modules
import pytest

from notify_bridge.components import BaseNotifier, WebhookNotifier, WebhookSchema
from notify_bridge.exceptions import NoSuchNotifierError, ValidationError

# Import local modules
from notify_bridge.factory import NotifierFactory
from notify_bridge.utils import HTTPClientConfig


class TestSchema(WebhookSchema):
    """Test notification schema."""
    pass


class TestNotifier(BaseNotifier):
    """Test notifier."""

    name = "test"
    schema = TestSchema

    def _send(self, schema: WebhookSchema) -> Dict[str, Any]:
        """Send notification synchronously."""
        return {"success": True}

    async def _send_async(self, schema: WebhookSchema) -> Dict[str, Any]:
        """Send notification asynchronously."""
        return {"success": True}

    def build_payload(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Build payload for notification.

        Args:
            data: Notification data.

        Returns:
            Dict[str, Any]: Payload.
        """
        notification = self.validate(data)
        return {
            "url": notification.url,
            "json": {
                "content": notification.content,
                "title": notification.title
            }
        }


@pytest.fixture
def factory() -> NotifierFactory:
    """Create a NotifierFactory instance."""
    factory = NotifierFactory()
    factory.register_notifier("webhook", WebhookNotifier)
    return factory


@pytest.fixture
def test_notifier() -> TestNotifier:
    """Create test notifier fixture."""
    return TestNotifier()


@pytest.fixture
def test_data() -> Dict[str, Any]:
    """Create test data fixture."""
    return {
        "url": "https://example.com",
        "title": "Test Title",
        "content": "Test Content",
        "msg_type": "text"
    }


def test_register_notifier(factory: NotifierFactory) -> None:
    """Test registering a notifier."""
    factory.register_notifier("test", TestNotifier)
    assert factory.get_notifier_class("test") == TestNotifier


def test_unregister_notifier(factory: NotifierFactory) -> None:
    """Test unregistering a notifier."""
    factory.register_notifier("test", TestNotifier)
    factory.unregister_notifier("test")
    assert "test" not in factory.get_notifier_names()


def test_get_notifier_names(factory: NotifierFactory) -> None:
    """Test getting notifier names."""
    factory.register_notifier("test", TestNotifier)
    assert "test" in factory.get_notifier_names()


def test_get_notifier_class(factory: NotifierFactory) -> None:
    """Test getting notifier class."""
    factory.register_notifier("test", TestNotifier)
    assert factory.get_notifier_class("test") == TestNotifier


def test_create_notifier(factory: NotifierFactory) -> None:
    """Test creating a notifier."""
    factory.register_notifier("test", TestNotifier)
    config = HTTPClientConfig()
    notifier = factory.create_notifier("test", config)
    assert isinstance(notifier, TestNotifier)


def test_create_notifier_invalid(factory: NotifierFactory) -> None:
    """Test creating an invalid notifier."""
    config = HTTPClientConfig()
    with pytest.raises(NoSuchNotifierError):
        factory.create_notifier("invalid", config)


def test_notify_success(factory: NotifierFactory, test_data: Dict[str, Any]) -> None:
    """Test successful notification."""
    with patch("httpx.Client.post") as mock_post:
        mock_post.return_value = Mock(
            status_code=200,
            json=lambda: {"success": True}
        )

        factory.register_notifier("test", TestNotifier)
        response = factory.notify("test", test_data)

        assert response.success is True
        assert response.name == "test"
        assert response.message == "Notification sent successfully"
        assert response.data == {"success": True}

        mock_post.assert_called_once()


@pytest.mark.asyncio
async def test_notify_async_success(factory: NotifierFactory, test_data: Dict[str, Any]) -> None:
    """Test successful async notification."""
    with patch("httpx.AsyncClient.post") as mock_post:
        mock_post.return_value = Mock(
            status_code=200,
            json=lambda: {"success": True}
        )

        factory.register_notifier("test", TestNotifier)
        response = await factory.notify_async("test", test_data)

        assert response.success is True
        assert response.name == "test"
        assert response.message == "Notification sent successfully"
        assert response.data == {"success": True}

        mock_post.assert_called_once()


def test_notify_validation_error(factory: NotifierFactory) -> None:
    """Test notification validation error."""
    factory.register_notifier("test", TestNotifier)
    with pytest.raises(ValidationError):
        factory.notify("test", {})


@pytest.mark.asyncio
async def test_notify_async_validation_error(factory: NotifierFactory) -> None:
    """Test async notification validation error."""
    factory.register_notifier("test", TestNotifier)
    with pytest.raises(ValidationError):
        await factory.notify_async("test", {})


def test_notify_notifier_not_found(factory: NotifierFactory, test_data: Dict[str, Any]) -> None:
    """Test notification with non-existent notifier."""
    with pytest.raises(NoSuchNotifierError):
        factory.notify("non_existent", test_data)


@pytest.mark.asyncio
async def test_notify_async_notifier_not_found(factory: NotifierFactory, test_data: Dict[str, Any]) -> None:
    """Test async notification with non-existent notifier."""
    with pytest.raises(NoSuchNotifierError):
        await factory.notify_async("non_existent", test_data)
