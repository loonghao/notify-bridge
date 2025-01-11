"""Tests for core functionality."""

# Import built-in modules
from typing import Any, Dict
from unittest.mock import AsyncMock, Mock, patch

# Import third-party modules
import httpx
import pytest

# Import local modules
from notify_bridge.core import NotifyBridge
from notify_bridge.exceptions import NoSuchNotifierError
from notify_bridge.types import BaseNotifier, NotificationResponse


class MockNotifier(BaseNotifier):
    """Mock notifier for testing."""

    name = "mock"

    def notify(self, notification: Dict[str, Any]) -> NotificationResponse:
        """Mock notify method."""
        return NotificationResponse(success=True, name=self.name, data=notification)

    async def notify_async(self, notification: Dict[str, Any]) -> NotificationResponse:
        """Mock async notify method."""
        return NotificationResponse(success=True, name=self.name, data=notification)


@pytest.fixture
def mock_factory():
    """Create a mock factory."""
    with patch("notify_bridge.core.NotifierFactory") as mock:
        mock_instance = mock.return_value
        mock_instance.get_notifier_class.return_value = MockNotifier
        mock_instance.create_notifier.return_value = MockNotifier()
        mock_instance.notify.return_value = NotificationResponse(success=True, name="mock", data={})
        mock_instance.anotify = AsyncMock(return_value=NotificationResponse(success=True, name="mock", data={}))
        mock_instance.get_notifier_names.return_value = {"mock": MockNotifier}
        yield mock_instance


def test_init():
    """Test initialization."""
    bridge = NotifyBridge()
    assert bridge._config == {}

    config = {"test": "config"}
    bridge = NotifyBridge(config)
    assert bridge._config == config


def test_context_manager():
    """Test context manager."""
    with NotifyBridge() as bridge:
        assert isinstance(bridge._sync_client, httpx.Client)
        assert bridge._async_client is None

    assert bridge._sync_client is None


@pytest.mark.asyncio
async def test_async_context_manager():
    """Test async context manager."""
    async with NotifyBridge() as bridge:
        assert isinstance(bridge._async_client, httpx.AsyncClient)
        assert bridge._sync_client is None

    assert bridge._async_client is None


def test_get_notifier_class(mock_factory):
    """Test getting notifier class."""
    bridge = NotifyBridge()
    notifier_class = bridge.get_notifier_class("mock")
    assert notifier_class == MockNotifier
    mock_factory.get_notifier_class.assert_called_once_with("mock")


def test_create_notifier(mock_factory):
    """Test creating notifier."""
    bridge = NotifyBridge()
    with bridge:
        notifier = bridge.create_notifier("mock")
        assert isinstance(notifier, MockNotifier)
        mock_factory.create_notifier.assert_called_once()
        assert "client" in mock_factory.create_notifier.call_args[1]


@pytest.mark.asyncio
async def test_create_async_notifier(mock_factory):
    """Test creating async notifier."""
    bridge = NotifyBridge()
    async with bridge:
        notifier = await bridge.create_async_notifier("mock")
        assert isinstance(notifier, MockNotifier)
        mock_factory.create_notifier.assert_called_once()
        assert "client" in mock_factory.create_notifier.call_args[1]


def test_notify(mock_factory):
    """Test notification."""
    bridge = NotifyBridge()
    with bridge:
        # Test with notification object
        notification = {"test": "data"}
        response = bridge.notify("mock", notification)
        assert response.success is True
        assert response.name == "mock"
        mock_factory.notify.assert_called_with("mock", notification=notification, client=bridge._sync_client)

        # Test with kwargs
        response = bridge.notify("mock", test="data")
        assert response.success is True
        assert response.name == "mock"
        mock_factory.notify.assert_called_with("mock", notification={"test": "data"}, client=bridge._sync_client)


@pytest.mark.asyncio
async def test_anotify(mock_factory):
    """Test async notification."""
    bridge = NotifyBridge()
    async with bridge:
        # Test with notification object
        notification = {"test": "data"}
        response = await bridge.anotify("mock", notification)
        assert response.success is True
        assert response.name == "mock"
        mock_factory.anotify.assert_called_with("mock", notification=notification, client=bridge._async_client)

        # Test with kwargs
        response = await bridge.anotify("mock", test="data")
        assert response.success is True
        assert response.name == "mock"
        mock_factory.anotify.assert_called_with("mock", notification={"test": "data"}, client=bridge._async_client)


def test_get_registered_notifiers(mock_factory):
    """Test getting registered notifiers."""
    bridge = NotifyBridge()
    notifiers = bridge.get_registered_notifiers()
    assert notifiers == ["mock"]
    mock_factory.get_notifier_names.assert_called_once()


def test_error_handling(mock_factory):
    """Test error handling."""
    bridge = NotifyBridge()

    # Test notifier not found
    mock_factory.get_notifier_class.return_value = None
    mock_factory.create_notifier.side_effect = NoSuchNotifierError("Notifier nonexistent not found")
    with pytest.raises(NoSuchNotifierError):
        bridge.create_notifier("nonexistent")

    # Test notification error
    mock_factory.notify.side_effect = Exception("Test error")
    with pytest.raises(Exception, match="Test error"):
        bridge.notify("mock", test="data")


@pytest.mark.asyncio
async def test_async_error_handling(mock_factory):
    """Test async error handling."""
    bridge = NotifyBridge()

    # Test notifier not found
    mock_factory.get_notifier_class.return_value = None
    mock_factory.create_notifier.side_effect = NoSuchNotifierError("Notifier nonexistent not found")
    with pytest.raises(NoSuchNotifierError):
        await bridge.create_async_notifier("nonexistent")

    # Test notification error
    mock_factory.anotify.side_effect = Exception("Test error")
    with pytest.raises(Exception, match="Test error"):
        await bridge.anotify("mock", test="data")
