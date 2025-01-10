"""Tests for plugin utilities."""

# Import built-in modules
from typing import Any, Dict
from unittest.mock import Mock, patch

# Import third-party modules
import pytest

# Import local modules
from notify_bridge.exceptions import PluginError
from notify_bridge.types import BaseNotifier, NotificationResponse, NotificationSchema
from notify_bridge.utils.plugin import get_notifiers_from_entry_points, load_notifier_from_entry_point


def test_load_notifier_from_entry_point_multiple_colons():
    """Test loading a notifier with multiple colons in the entry point."""
    entry_point = Mock()
    entry_point.value = "module:submodule:class"

    with pytest.raises(PluginError):
        load_notifier_from_entry_point(entry_point)


def test_load_notifier_from_entry_point_no_colon():
    """Test loading a notifier with no colon in the entry point."""
    entry_point = Mock()
    entry_point.value = "module"

    with pytest.raises(PluginError):
        load_notifier_from_entry_point(entry_point)


def test_load_notifier_from_entry_point_empty():
    """Test loading a notifier with empty entry point."""
    entry_point = Mock()
    entry_point.value = ""

    with pytest.raises(PluginError):
        load_notifier_from_entry_point(entry_point)


def test_load_notifier_from_entry_point_invalid_module():
    """Test loading a notifier with invalid module."""
    entry_point = Mock()
    entry_point.value = "invalid.module:class"

    with pytest.raises(PluginError):
        load_notifier_from_entry_point(entry_point)


def test_get_notifiers_from_entry_points():
    """Test getting notifiers from entry points."""
    mock_entry_point = Mock()
    mock_entry_point.name = "test"
    mock_entry_point.value = "module:TestNotifier"

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

    with patch("importlib.metadata.entry_points") as mock_entry_points:
        mock_entry_points.return_value = Mock()
        mock_entry_points.return_value.select.return_value = [mock_entry_point]
        with patch("notify_bridge.utils.plugin.load_notifier_from_entry_point") as mock_load:
            mock_load.return_value = TestNotifier
            notifiers = get_notifiers_from_entry_points()
            assert "test" in notifiers
            assert notifiers["test"] == TestNotifier
