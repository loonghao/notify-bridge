"""Tests for core functionality."""

# Import built-in modules
from typing import Any, Dict, Optional
from unittest.mock import ANY, AsyncMock, Mock, patch

# Import third-party modules
import httpx
import pytest
from pydantic_core._pydantic_core import ValidationError

# Import local modules
from notify_bridge.components import BaseNotifier, WebhookNotifier
from notify_bridge.core import NotifyBridge
from notify_bridge.exceptions import NoSuchNotifierError, NotificationError
from notify_bridge.schema import NotificationResponse, NotificationSchema, WebhookSchema
from notify_bridge.utils import HTTPClientConfig


class MockSchema(WebhookSchema):
    """Mock schema for testing."""

    content: str
    title: str
    msg_type: str = "text"
    webhook_url: str
    method: str = "POST"
    headers: Dict[str, str] = {}
    timeout: Optional[float] = None
    verify_ssl: bool = True


class MockNotifier(WebhookNotifier):
    """Mock notifier for testing."""

    name = "mock"
    schema_class = MockSchema

    def build_payload(self, notification: MockSchema) -> Dict[str, Any]:
        """Build payload for notification."""
        if isinstance(notification, dict):
            return {
                "text": notification.get("content", ""),
                "title": notification.get("title", ""),
                "msg_type": notification.get("msg_type", "text")
            }
        return {
            "text": notification.content,
            "title": notification.title,
            "msg_type": notification.msg_type
        }

    def notify(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Send notification."""
        notification = self.validate(data)
        response = self._http_client.request(
            method="POST",
            url=notification.webhook_url,
            headers=notification.headers,
            json=self.build_payload(notification),
            timeout=notification.timeout,
            verify=notification.verify_ssl
        )
        return NotificationResponse(
            success=response.status_code == 200,
            name=self.name,
            message="Notification sent successfully"
        ).model_dump()

    async def notify_async(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Send notification asynchronously."""
        notification = self.validate(data)
        response = await self._async_http_client.request(
            method="POST",
            url=notification.webhook_url,
            headers=notification.headers,
            json=self.build_payload(notification),
            timeout=notification.timeout,
            verify=notification.verify_ssl
        )
        return NotificationResponse(
            success=True,
            name=self.name,
            message="Notification sent successfully",
            data=response.json() if response.text else None
        ).model_dump()


@pytest.fixture
def mock_factory():
    """Create a mock factory."""
    with patch("notify_bridge.core.NotifierFactory") as mock:
        mock_instance = mock.return_value
        mock_instance.get_notifier_class.return_value = MockNotifier
        mock_instance.create_notifier.return_value = MockNotifier()
        mock_instance.create_notifier_async = AsyncMock(return_value=MockNotifier())
        mock_instance.send.side_effect = lambda notifier_name, data: NotificationResponse(
            success=True,
            name=notifier_name,
            message="Notification sent successfully",
            data={}
        ).model_dump()
        mock_instance.notify_async = AsyncMock(
            side_effect=lambda notifier_name, data: NotificationResponse(
                success=True,
                name=notifier_name,
                message="Notification sent successfully",
                data={}
            ).model_dump()
        )
        mock_instance.get_notifier_names.return_value = {"mock": MockNotifier}
        yield mock_instance


@pytest.fixture
def notify_bridge() -> NotifyBridge:
    """Create a NotifyBridge instance."""
    return NotifyBridge()


@pytest.fixture
def test_notifier():
    """Test notifier fixture."""
    class TestNotifier(BaseNotifier):
        schema_class = NotificationSchema
        supported_types = ["text"]

        def __init__(self, name: str = "test", config: Optional[HTTPClientConfig] = None):
            super().__init__(name)
            self._name = name
            self._config = config

        def build_payload(self, data: Dict[str, Any]) -> Dict[str, Any]:
            return data

        def send(self, data: NotificationSchema) -> Dict[str, Any]:
            return NotificationResponse(
                success=True,
                name=self._name,
                message="Notification sent successfully",
                data=data.model_dump()
            ).model_dump()

        async def send_async(self, data: NotificationSchema) -> Dict[str, Any]:
            return NotificationResponse(
                success=True,
                name=self._name,
                message="Notification sent successfully",
                data=data.model_dump()
            ).model_dump()

    return TestNotifier


@pytest.fixture
def test_data() -> Dict[str, Any]:
    """Create test data fixture."""
    return {
        "webhook_url": "https://example.com",
        "title": "Test Title",
        "content": "Test Content",
        "msg_type": "text"
    }


def test_init():
    """Test initialization."""
    bridge = NotifyBridge()
    assert isinstance(bridge._config, HTTPClientConfig)

    config = HTTPClientConfig(timeout=60.0)
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
    notifier_class = mock_factory.get_notifier_class("mock")
    assert notifier_class == MockNotifier


def test_create_notifier(mock_factory):
    """Test creating notifier."""
    notifier = mock_factory.create_notifier("mock")
    assert isinstance(notifier, MockNotifier)
    assert notifier.name == "mock"


@pytest.mark.asyncio
async def test_create_async_notifier(mock_factory):
    """Test creating async notifier."""
    notifier = await mock_factory.create_notifier_async("mock")
    assert isinstance(notifier, MockNotifier)
    assert notifier.name == "mock"


def test_notify(test_data: dict, notify_bridge: NotifyBridge, test_notifier):
    """Test notification."""
    notify_bridge.register_notifier("test", test_notifier)
    with patch.object(notify_bridge, 'get_notifier') as mock_get_notifier:
        mock_notifier = Mock()
        mock_notifier.schema_class = NotificationSchema
        mock_notifier.send.return_value = {
            "success": True,
            "name": "test",
            "message": "Notification sent successfully",
            "data": test_data
        }
        mock_get_notifier.return_value = mock_notifier

        response = notify_bridge.send("test", data=test_data)

        assert response["success"] is True
        assert response["name"] == "test"
        for key, value in test_data.items():
            assert response["data"][key] == value

        mock_get_notifier.assert_called_once_with("test")
        mock_notifier.send.assert_called_once_with(ANY)


@pytest.mark.asyncio
@pytest.mark.parametrize("notifier_name", ["test", "another_test"])
async def test_anotify(notifier_name: str, test_data: dict, notify_bridge: NotifyBridge, test_notifier):
    """Test asynchronous notification."""
    notify_bridge.register_notifier(notifier_name, test_notifier)
    with patch.object(notify_bridge, 'get_notifier') as mock_get_notifier:
        mock_notifier = AsyncMock()
        mock_notifier.schema_class = NotificationSchema
        mock_notifier.send_async.return_value = {
            "success": True,
            "name": notifier_name,
            "message": "Notification sent successfully",
            "data": test_data
        }
        mock_get_notifier.return_value = mock_notifier

        response = await notify_bridge.send_async(notifier_name, data=test_data)

        assert response["success"] is True
        assert response["name"] == notifier_name
        for key, value in test_data.items():
            assert response["data"][key] == value

        mock_get_notifier.assert_called_once_with(notifier_name)
        mock_notifier.send_async.assert_called_once_with(ANY)


def test_get_registered_notifiers(mock_factory):
    """Test getting registered notifiers."""
    notifiers = mock_factory.get_notifier_names()
    assert isinstance(notifiers, dict)
    assert "mock" in notifiers
    assert notifiers["mock"] == MockNotifier


def test_error_handling(mock_factory, test_data):
    """Test error handling."""
    mock_factory.send.side_effect = NotificationError("Test error")
    with pytest.raises(NotificationError):
        mock_factory.send("mock", test_data)


@pytest.mark.asyncio
async def test_async_error_handling(mock_factory, test_data):
    """Test async error handling."""
    mock_factory.notify_async.side_effect = NotificationError("Test error")
    with pytest.raises(NotificationError):
        await mock_factory.notify_async("mock", test_data)


def test_register_notifier(notify_bridge: NotifyBridge, test_notifier):
    """Test registering a notifier."""
    notify_bridge.register_notifier("test", test_notifier)
    assert notify_bridge.get_notifier_class("test") == test_notifier


def test_get_notifier_not_found(notify_bridge: NotifyBridge):
    """Test getting a non-existent notifier."""
    with pytest.raises(NoSuchNotifierError):
        notify_bridge.get_notifier_class("nonexistent")


def test_notify_sync(notify_bridge: NotifyBridge, test_notifier, test_data: Dict[str, Any]):
    """Test synchronous notification."""
    notify_bridge.register_notifier("test", test_notifier)

    response = notify_bridge.send("test", test_data)
    assert response["success"] is True
    assert response["name"] == "test"
    for key, value in test_data.items():
        assert response["data"][key] == value


@pytest.mark.asyncio
async def test_notify_async(notify_bridge: NotifyBridge, test_notifier, test_data: Dict[str, Any]):
    """Test asynchronous notification."""
    notify_bridge.register_notifier("test", test_notifier)

    response = await notify_bridge.send_async("test", test_data)
    assert response["success"] is True
    assert response["name"] == "test"
    for key, value in test_data.items():
        assert response["data"][key] == value


def test_notify_validation_error(notify_bridge: NotifyBridge, test_notifier):
    """Test notification with invalid data."""
    notify_bridge.register_notifier("test", test_notifier)
    with pytest.raises(ValidationError) as exc_info:
        notify_bridge.send("test", {})
    assert "url" in str(exc_info.value)


@pytest.mark.asyncio
async def test_notify_async_validation_error(notify_bridge: NotifyBridge, test_notifier):
    """Test async notification with invalid data."""
    notify_bridge.register_notifier("test", test_notifier)
    with pytest.raises(ValidationError) as exc_info:
        await notify_bridge.send_async("test", {})
    assert "url" in str(exc_info.value)


def test_notify_notifier_not_found(notify_bridge: NotifyBridge, test_data: Dict[str, Any]):
    """Test notification with non-existent notifier."""
    with pytest.raises(NoSuchNotifierError):
        notify_bridge.send("nonexistent", test_data)


@pytest.mark.asyncio
async def test_notify_async_notifier_not_found(notify_bridge: NotifyBridge, test_data: Dict[str, Any]):
    """Test async notification with non-existent notifier."""
    with pytest.raises(NoSuchNotifierError):
        await notify_bridge.send_async("nonexistent", test_data)
