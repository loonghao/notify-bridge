"""Tests for core functionality."""

# Import built-in modules
from typing import Any
from typing import Dict
from typing import Optional
from typing import Union
from unittest.mock import AsyncMock
from unittest.mock import Mock
from unittest.mock import patch

# Import third-party modules
import httpx
from pydantic_core._pydantic_core import ValidationError
import pytest

# Import local modules
from notify_bridge.components import BaseNotifier
from notify_bridge.components import WebhookNotifier
from notify_bridge.core import NotifyBridge
from notify_bridge.exceptions import NoSuchNotifierError
from notify_bridge.exceptions import NotificationError
from notify_bridge.schema import NotificationResponse
from notify_bridge.schema import NotificationSchema
from notify_bridge.schema import WebhookSchema
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
                "msg_type": notification.get("msg_type", "text"),
            }
        return {"text": notification.content, "title": notification.title, "msg_type": notification.msg_type}

    def notify(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Send notification."""
        notification = self.validate(data)
        response = self._http_client.request(
            method="POST",
            url=notification.webhook_url,
            headers=notification.headers,
            json=self.build_payload(notification),
            timeout=notification.timeout,
            verify=notification.verify_ssl,
        )
        return NotificationResponse(
            success=response.status_code == 200, name=self.name, message="Notification sent successfully"
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
            verify=notification.verify_ssl,
        )
        return NotificationResponse(
            success=True,
            name=self.name,
            message="Notification sent successfully",
            data=response.json() if response.text else None,
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
            success=True, name=notifier_name, message="Notification sent successfully", data={}
        ).model_dump()
        mock_instance.notify_async = AsyncMock(
            side_effect=lambda notifier_name, data: NotificationResponse(
                success=True, name=notifier_name, message="Notification sent successfully", data={}
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
    """Create a test notifier class."""

    class TestNotifier(BaseNotifier):
        """Test notifier."""

        schema_class = NotificationSchema
        supported_types = ["text"]

        def __init__(self, name: str = "test", config: Optional[HTTPClientConfig] = None):
            """Initialize test notifier."""
            super().__init__(name)
            self._name = name
            self._config = config

        def send(self, notification: NotificationSchema) -> Dict[str, Any]:
            """Send notification."""
            with httpx.Client() as client:
                response = client.request(
                    method="POST",
                    url=notification.webhook_url,
                    headers=notification.headers or {},
                    json=self.build_payload(notification),
                    timeout=notification.timeout,
                )
                response.raise_for_status()
                return {
                    "success": True,
                    "name": self.name,
                    "message": "Notification sent successfully",
                    "data": notification.model_dump(),
                }

        async def send_async(self, notification: NotificationSchema) -> Dict[str, Any]:
            """Send notification asynchronously."""
            async with httpx.AsyncClient() as client:
                response = await client.request(
                    method="POST",
                    url=notification.webhook_url,
                    headers=notification.headers or {},
                    json=self.build_payload(notification),
                    timeout=notification.timeout,
                )
                response.raise_for_status()
                return {
                    "success": True,
                    "name": self.name,
                    "message": "Notification sent successfully",
                    "data": notification.model_dump(),
                }

        @classmethod
        def build_payload(cls, notification: Union[NotificationSchema, Dict[str, Any]]) -> Dict[str, Any]:
            """Build payload."""
            if isinstance(notification, dict):
                return {
                    "webhook_url": notification["webhook_url"],
                    "title": notification["title"],
                    "content": notification["content"],
                    "msg_type": notification["msg_type"],
                }
            return {
                "webhook_url": notification.webhook_url,
                "title": notification.title,
                "content": notification.content,
                "msg_type": notification.msg_type,
            }

    return TestNotifier


@pytest.fixture
def test_data() -> Dict[str, Any]:
    """Create test data fixture."""
    return {"webhook_url": "https://example.com", "title": "Test Title", "content": "Test Content", "msg_type": "text"}


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
    notify_bridge.register_notifier("mock", test_notifier)
    with patch("httpx.Client.request") as mock_request:
        mock_request.return_value = Mock(status_code=200, text="", json=lambda: {})
        response = notify_bridge.send("mock", data=test_data)
        assert response["success"] is True
        assert response["name"] == "mock"
        assert response["message"] == "Notification sent successfully"
        mock_request.assert_called_once_with(
            method="POST",
            url=test_data["webhook_url"],
            headers=test_data.get("headers", {}),
            json=test_notifier.build_payload(test_data),
            timeout=test_data.get("timeout"),
        )


@pytest.mark.parametrize("notifier_name", ["test", "another_test"])
def test_anotify(notifier_name: str, test_data: dict, notify_bridge: NotifyBridge, test_notifier):
    """Test asynchronous notification."""
    notify_bridge.register_notifier(notifier_name, test_notifier)

    async def test():
        with patch("httpx.AsyncClient.request") as mock_request:
            mock_request.return_value = Mock(status_code=200, text="", json=lambda: {})
            response = await notify_bridge.send_async(notifier_name, data=test_data)
            assert response["success"] is True
            assert response["name"] == notifier_name
            assert response["message"] == "Notification sent successfully"
            mock_request.assert_called_once_with(
                method="POST",
                url=test_data["webhook_url"],
                headers=test_data.get("headers", {}),
                json=test_notifier.build_payload(test_data),
                timeout=test_data.get("timeout"),
            )

    # Import built-in modules
    import asyncio

    asyncio.run(test())


def test_notify_sync(notify_bridge: NotifyBridge, test_notifier, test_data: Dict[str, Any]):
    """Test synchronous notification."""
    notify_bridge.register_notifier("mock", test_notifier)
    with patch("httpx.Client.request") as mock_request:
        mock_request.return_value = Mock(status_code=200)
        response = notify_bridge.send("mock", data=test_data)
        assert response["success"] is True
        assert response["name"] == "mock"
        assert response["message"] == "Notification sent successfully"


@pytest.mark.asyncio
async def test_notify_async(notify_bridge: NotifyBridge, test_notifier, test_data: Dict[str, Any]):
    """Test asynchronous notification."""
    notify_bridge.register_notifier("test", test_notifier)
    with patch("httpx.AsyncClient.request") as mock_request:
        mock_request.return_value = Mock(status_code=200, text="", json=lambda: {})
        response = await notify_bridge.send_async("test", data=test_data)
        assert response["success"] is True
        assert response["name"] == "test"
        assert response["message"] == "Notification sent successfully"
        mock_request.assert_called_once_with(
            method="POST",
            url=test_data["webhook_url"],
            headers=test_data.get("headers", {}),
            json=test_notifier.build_payload(test_data),
            timeout=test_data.get("timeout"),
        )


def test_notify_validation_error(notify_bridge: NotifyBridge, test_notifier):
    """Test notification with invalid data."""
    notify_bridge.register_notifier("mock", test_notifier)
    with pytest.raises(ValidationError):
        notify_bridge.send("mock", data={})


def test_notify_async_validation_error(notify_bridge: NotifyBridge, test_notifier):
    """Test async notification with invalid data."""
    notify_bridge.register_notifier("mock", test_notifier)

    async def test():
        with pytest.raises(ValidationError):
            await notify_bridge.send_async("mock", data={})

    # Import built-in modules
    import asyncio

    asyncio.run(test())


def test_notify_notifier_not_found(notify_bridge: NotifyBridge, test_data: Dict[str, Any]):
    """Test notification with non-existent notifier."""
    with pytest.raises(NoSuchNotifierError):
        notify_bridge.send("non_existent", data=test_data)


def test_notify_async_notifier_not_found(notify_bridge: NotifyBridge, test_data: Dict[str, Any]):
    """Test async notification with non-existent notifier."""

    async def test():
        with pytest.raises(NoSuchNotifierError):
            await notify_bridge.send_async("non_existent", data=test_data)

    # Import built-in modules
    import asyncio

    asyncio.run(test())


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
