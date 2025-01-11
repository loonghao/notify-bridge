"""Tests for plugin utilities."""

# Import built-in modules
from typing import Any, Dict, Type
from unittest.mock import Mock, patch

# Import third-party modules
import pytest
from notify_bridge.components import BaseNotifier, NotificationResponse

# Import local modules
from notify_bridge.exceptions import PluginError
from notify_bridge.plugin import get_notifiers_from_entry_points, load_notifier
from notify_bridge.schema import NotificationSchema


def test_load_notifier_multiple_colons():
    """Test loading a notifier with multiple colons in the entry point."""
    with pytest.raises(PluginError):
        load_notifier("module:submodule:class")


def test_load_notifier_no_colon():
    """Test loading a notifier with no colon in the entry point."""
    with pytest.raises(PluginError):
        load_notifier("module")


def test_load_notifier_empty():
    """Test loading a notifier with empty entry point."""
    with pytest.raises(PluginError):
        load_notifier("")


def test_load_notifier_invalid_module():
    """Test loading a notifier with invalid module."""
    with pytest.raises(PluginError):
        load_notifier("invalid.module:class")


def test_get_notifiers_from_entry_points():
    """Test getting notifiers from entry points."""

    class TestSchema(NotificationSchema):
        """Test schema."""

        pass

    class TestNotifier(BaseNotifier):
        """Test notifier."""

        name = "test"
        schema = TestSchema

        def __init__(self, schema: Type[NotificationSchema], **kwargs: Any) -> None:
            """Initialize the notifier.

            Args:
                schema: The schema class to use for validation.
                **kwargs: Additional arguments to pass to the notifier.
            """
            super().__init__(schema=schema, **kwargs)

        def notify(self, notification: Dict[str, Any], **kwargs: Any) -> NotificationResponse:
            """Send data."""
            return NotificationResponse(success=True, name=self.name)

        async def anotify(self, notification: Dict[str, Any], **kwargs: Any) -> NotificationResponse:
            """Send data asynchronously."""
            return NotificationResponse(success=True, name=self.name)

        def build_payload(self, data: Dict[str, Any]) -> Dict[str, Any]:
            """Build payload."""
            return {}

    # Mock pkg_resources.iter_entry_points
    with patch("pkg_resources.iter_entry_points") as mock_entry_points:
        # Create a mock entry point
        mock_entry_point = Mock()
        mock_entry_point.module_name = "notify_bridge.notifiers.test"
        mock_entry_point.name = "test"
        mock_entry_points.return_value = [mock_entry_point]

        # Mock load_notifier
        with patch(
            "notify_bridge.plugin.load_notifier",
            return_value=TestNotifier,
        ) as mock_load:
            notifiers = get_notifiers_from_entry_points()

            # Verify the results
            assert len(notifiers) == 1
            assert "test" in notifiers
            assert notifiers["test"] == TestNotifier

            # Verify the mocks were called correctly
            mock_entry_points.assert_called_once_with("notify_bridge.notifiers")
            mock_load.assert_called_once_with("notify_bridge.notifiers.test:test")
