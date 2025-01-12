"""Tests for core functionality."""

# Import built-in modules
from typing import Any, Dict, Optional, Type
from unittest.mock import AsyncMock, patch

# Import third-party modules
import httpx
import pytest

# Import local modules
from notify_bridge.components import BaseNotifier
from notify_bridge.core import NotifyBridge
from notify_bridge.exceptions import NoSuchNotifierError, NotificationError
from notify_bridge.schema import NotificationResponse, NotificationSchema
from notify_bridge.utils import HTTPClientConfig


class MockSchema(NotificationSchema):
    """Mock schema for testing."""

    content: str
    title: str
    msg_type: str = "text"
    webhook_url: str
    method: str = "POST"
    headers: Dict[str, str] = {}
    timeout: Optional[float] = None
    verify_ssl: bool = True


class MockNotifier(BaseNotifier):
    """Mock notifier for testing."""

    name = "mock"
    schema_class = MockSchema

    def assemble_data(self, data: MockSchema) -> Dict[str, Any]:
        """Assemble data.

        Args:
            data: Notification data.

        Returns:
            Dict[str, Any]: API payload.
        """
        if isinstance(data, dict):
            return {
                "text": data.get("content", ""),
                "title": data.get("title", ""),
                "msg_type": data.get("msg_type", "text"),
            }
        return {"text": data.content, "title": data.title, "msg_type": data.msg_type}

    def prepare_request_params(self, notification: NotificationSchema, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Prepare request parameters.

        Args:
            notification: Notification data.
            payload: Prepared payload.

        Returns:
            Dict[str, Any]: Request parameters.
        """
        return {
            "method": "POST",
            "url": notification.webhook_url,
            "json": payload,
            "headers": notification.headers,
        }

    def send_notification(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Send data."""
        notification = self.validate(data)
        self._ensure_sync_client()
        response = self._http_client.request(
            method=self.get_http_method(),
            url=notification.webhook_url,
            headers=notification.headers,
            json=self.assemble_data(notification),
            timeout=self._config.timeout,
        )
        return NotificationResponse(
            success=response.status_code == 200, name=self.name, message="Notification sent successfully", data=response
        ).model_dump()

    async def send_notification_async(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Send data asynchronously."""
        notification = self.validate(data)
        response = await self._async_http_client.request(
            method=notification.method,
            url=notification.webhook_url,
            headers=notification.headers,
            json=self.assemble_data(notification),
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
        mock_instance.send_async = AsyncMock(
            side_effect=lambda notifier_name, data: NotificationResponse(
                success=True, name=notifier_name, message="Notification sent successfully", data={}
            ).model_dump()
        )
        mock_instance.get_notifier_names.return_value = {"mock": MockNotifier}
        yield mock_instance


@pytest.fixture
def test_data() -> Dict[str, Any]:
    """Test data fixture."""
    return {
        "webhook_url": "https://example.com",
        "title": "test title",
        "content": "test content",
        "msg_type": "text",
    }


@pytest.fixture
def test_notifier() -> Type[BaseNotifier]:
    """Test notifier fixture."""

    class TestNotifier(BaseNotifier):
        """Test notifier."""

        name = "mock"

        def get_http_method(self) -> str:
            """Get HTTP method.

            Returns:
                str: HTTP method.
            """
            return "POST"

        def assemble_data(self, notification: NotificationSchema) -> Dict[str, Any]:
            """Assemble notification data.

            Args:
                notification: Notification data.

            Returns:
                Dict[str, Any]: Assembled data.
            """
            payload = {
                "msg_type": notification.msg_type,
                "text": notification.content,
                "title": notification.title,
            }
            return {
                "method": "POST",
                "url": notification.url,
                "json": payload,
            }

        def send(self, data: Dict[str, Any]) -> Dict[str, Any]:
            """Send notification.

            Args:
                data: Notification data.

            Returns:
                Dict[str, Any]: Response data.
            """
            notification = self.validate(data)
            self._ensure_sync_client()
            response = self._http_client.request(
                method=self.get_http_method(),
                url=notification.url,
                headers=notification.headers,
                json=self.assemble_data(notification),
                timeout=self._config.timeout,
            )
            return NotificationResponse(
                success=response.status_code == 200,
                name=self.name,
                message="Notification sent successfully",
                data=response.json() if response.text else None,
            ).model_dump()

    return TestNotifier


@pytest.fixture
def notify_bridge() -> NotifyBridge:
    """NotifyBridge fixture."""
    return NotifyBridge()


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


def test_notify_validation_error(notify_bridge: NotifyBridge, test_notifier):
    """Test notification with invalid data."""
    notify_bridge.register_notifier("mock", test_notifier)
    with pytest.raises(NotificationError):
        notify_bridge.send("mock", data={"invalid": "data"})


def test_notify_notifier_not_found(notify_bridge: NotifyBridge):
    """Test notification with non-existent notifier."""
    with pytest.raises(NoSuchNotifierError):
        notify_bridge.send("non_existent", data={})


@pytest.mark.asyncio
async def test_notify_async_notifier_not_found(notify_bridge: NotifyBridge):
    """Test async notification with non-existent notifier."""
    with pytest.raises(NoSuchNotifierError):
        await notify_bridge.send_async("non_existent", data={})


def test_get_registered_notifiers(mock_factory):
    """Test getting registered notifiers."""
    notifiers = mock_factory.get_notifier_names()
    assert isinstance(notifiers, dict)
    assert "mock" in notifiers
    assert notifiers["mock"] == MockNotifier


def test_register_notifier(notify_bridge: NotifyBridge, test_notifier):
    """Test registering a notifier."""
    notify_bridge.register_notifier("test", test_notifier)
    assert notify_bridge.get_notifier_class("test") == test_notifier


def test_get_notifier_not_found(notify_bridge: NotifyBridge):
    """Test getting a non-existent notifier."""
    with pytest.raises(NoSuchNotifierError):
        notify_bridge.get_notifier_class("nonexistent")
