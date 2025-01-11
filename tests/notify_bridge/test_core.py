"""Tests for core functionality."""

# Import built-in modules
from typing import Any, Dict
from unittest.mock import patch

# Import third-party modules
import httpx
import pytest
from pydantic import ValidationError as PydanticValidationError
from pydantic_core import ErrorDetails

# Import local modules
from notify_bridge.components import BaseNotifier
from notify_bridge.core import NotifyBridge
from notify_bridge.exceptions import ConfigurationError, NoSuchNotifierError, NotificationError
from notify_bridge.schema import NotificationSchema
from notify_bridge.utils import HTTPClientConfig


class TestSchema(NotificationSchema):
    """Test schema for testing."""

    webhook_url: str
    title: str
    content: str
    msg_type: str = "text"


class TestNotifier(BaseNotifier):
    """Mock notifier for testing."""

    schema_class = TestSchema

    def __init__(self, **kwargs):
        """Initialize test notifier."""
        super().__init__(**kwargs)

    def send(self, notification: NotificationSchema) -> Dict[str, Any]:
        """Mock send method."""
        return {
            "success": True,
            "name": "test",
            "message": "Notification sent successfully",
            "data": notification.model_dump()
        }

    async def send_async(self, notification: NotificationSchema) -> Dict[str, Any]:
        """Mock async send method."""
        return {
            "success": True,
            "name": "test",
            "message": "Notification sent successfully",
            "data": notification.model_dump()
        }


class ErrorNotifier(BaseNotifier):
    """Mock notifier that raises errors."""

    schema_class = TestSchema

    def __init__(self, **kwargs):
        """Initialize error notifier."""
        super().__init__(**kwargs)

    def send(self, notification: NotificationSchema) -> Dict[str, Any]:
        """Mock send method that raises an error."""
        raise NotificationError("Failed to send notification")

    async def send_async(self, notification: NotificationSchema) -> Dict[str, Any]:
        """Mock async send method that raises an error."""
        raise NotificationError("Failed to send notification")


@pytest.fixture
def mock_factory():
    """Create a mock factory."""
    with patch("notify_bridge.core.NotifierFactory") as mock:
        mock_instance = mock.return_value
        mock_instance.get_notifier_class.return_value = TestNotifier
        mock_instance.create_notifier.return_value = TestNotifier()
        mock_instance.get_notifier_names.return_value = {"test": TestNotifier}
        yield mock_instance


def test_init():
    """Test initialization."""
    bridge = NotifyBridge()
    assert isinstance(bridge._config, HTTPClientConfig)

    config = HTTPClientConfig(timeout=10.0)
    bridge = NotifyBridge(config)
    assert bridge._config == config

    # Test with invalid config
    with pytest.raises(ConfigurationError):
        NotifyBridge({"invalid": "config"})


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
    notifier_class = bridge.get_notifier_class("test")
    assert notifier_class == TestNotifier
    mock_factory.get_notifier_class.assert_called_once_with("test")


def test_create_notifier(mock_factory):
    """Test creating notifier."""
    bridge = NotifyBridge()
    notifier = bridge.create_notifier("test")
    assert isinstance(notifier, TestNotifier)
    mock_factory.create_notifier.assert_called_once_with("test", config=bridge._config)


@pytest.mark.asyncio
async def test_create_async_notifier(mock_factory):
    """Test creating async notifier."""
    bridge = NotifyBridge()
    notifier = await bridge.create_async_notifier("test")
    assert isinstance(notifier, TestNotifier)
    mock_factory.create_notifier.assert_called_once_with("test", config=bridge._config)


def test_register_notifier(mock_factory):
    """Test registering notifier."""
    bridge = NotifyBridge()
    bridge.register_notifier("test", TestNotifier)
    mock_factory.register_notifier.assert_called_once_with("test", TestNotifier)

    # Test registering invalid notifier
    mock_factory.register_notifier.side_effect = TypeError("Invalid notifier class")
    with pytest.raises(TypeError):
        bridge.register_notifier("test", object)


def test_get_registered_notifiers(mock_factory):
    """Test getting registered notifiers."""
    bridge = NotifyBridge()
    notifiers = bridge.get_registered_notifiers()
    assert notifiers == ["test"]
    mock_factory.get_notifier_names.assert_called_once()


def test_notifiers_property(mock_factory):
    """Test notifiers property."""
    bridge = NotifyBridge()
    assert bridge.notifiers == ["test"]
    mock_factory.get_notifier_names.assert_called_once()


def test_get_notifier(mock_factory):
    """Test getting notifier."""
    bridge = NotifyBridge()
    notifier = bridge.get_notifier("test")
    assert isinstance(notifier, TestNotifier)
    mock_factory.create_notifier.assert_called_once_with("test", config=bridge._config)


def test_send(mock_factory):
    """Test sending notification."""
    bridge = NotifyBridge()
    test_data = {
        "webhook_url": "https://example.com",
        "title": "Test Title",
        "content": "Test Content",
        "msg_type": "text"
    }
    response = bridge.send("test", test_data)
    assert response["success"] is True
    assert response["name"] == "test"
    assert response["message"] == "Notification sent successfully"
    assert response["data"]["webhook_url"] == "https://example.com"

    # Test sending with invalid data
    with pytest.raises(PydanticValidationError):
        bridge.send("test", {"invalid_field": "invalid"})

    # Test sending with error notifier
    mock_factory.create_notifier.return_value = ErrorNotifier()
    with pytest.raises(NotificationError):
        bridge.send("test", test_data)


@pytest.mark.asyncio
async def test_send_async(mock_factory):
    """Test sending notification asynchronously."""
    bridge = NotifyBridge()
    test_data = {
        "webhook_url": "https://example.com",
        "title": "Test Title",
        "content": "Test Content",
        "msg_type": "text"
    }
    response = await bridge.send_async("test", test_data)
    assert response["success"] is True
    assert response["name"] == "test"
    assert response["message"] == "Notification sent successfully"
    assert response["data"]["webhook_url"] == "https://example.com"

    # Test sending with invalid data
    with pytest.raises(PydanticValidationError):
        await bridge.send_async("test", {"invalid_field": "invalid"})

    # Test sending with error notifier
    mock_factory.create_notifier.return_value = ErrorNotifier()
    with pytest.raises(NotificationError):
        await bridge.send_async("test", test_data)


def test_error_handling(mock_factory):
    """Test error handling."""
    bridge = NotifyBridge()

    # Test notifier not found
    mock_factory.get_notifier_class.return_value = None
    with pytest.raises(NoSuchNotifierError):
        bridge.get_notifier_class("nonexistent")

    # Test notification error
    mock_factory.create_notifier.side_effect = NoSuchNotifierError("Notifier nonexistent not found")
    with pytest.raises(NoSuchNotifierError):
        bridge.create_notifier("nonexistent")

    # Test validation error
    mock_factory.get_notifier_class.side_effect = None  # Reset side effect
    mock_factory.get_notifier_class.return_value = TestNotifier
    error = ErrorDetails(type="missing", loc=("field",), input="invalid", msg="Field required")
    mock_factory.create_notifier.side_effect = PydanticValidationError.from_exception_data(
        "Invalid notification data",
        [error]
    )
    with pytest.raises(PydanticValidationError):
        bridge.create_notifier("test")


@pytest.mark.asyncio
async def test_async_error_handling():
    """Test async error handling."""
    bridge = NotifyBridge()

    with patch.object(bridge._factory, '_notifiers', {}):
        # Test notifier not found
        with pytest.raises(NoSuchNotifierError):
            await bridge.create_async_notifier("nonexistent")

        # Register test notifier for validation error test
        bridge._factory._notifiers = {"test": TestNotifier}

        # Test validation error with invalid data
        with pytest.raises(PydanticValidationError) as exc_info:
            await bridge.send_async("test", {"invalid_field": "invalid"})
        assert "invalid_field" in str(exc_info.value)

        # Replace with error notifier for notification error test
        bridge._factory._notifiers["test"] = ErrorNotifier
        
        # Test notification error with valid data but error notifier
        with pytest.raises(NotificationError) as exc_info:
            await bridge.send_async("test", {
                "webhook_url": "https://example.com",
                "title": "Test",
                "content": "Test"
            })
        assert "Failed to send notification" in str(exc_info.value)
