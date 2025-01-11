"""Tests for plugin utilities."""

# Import built-in modules
from typing import Any
from typing import Dict
from typing import Type
from unittest.mock import Mock
from unittest.mock import patch

# Import third-party modules
import pytest

# Import local modules
from notify_bridge.components import BaseNotifier
from notify_bridge.components import NotificationResponse
from notify_bridge.exceptions import PluginError
from notify_bridge.plugin import get_notifiers_from_entry_points
from notify_bridge.plugin import load_notifier
from notify_bridge.schema import NotificationSchema


@pytest.fixture
def test_schema():
    """Create a test schema class."""

    class TestSchema(NotificationSchema):
        """Test schema."""

        pass

    return TestSchema


@pytest.fixture
def test_notifier():
    """Create a test notifier class."""

    class TestNotifier(BaseNotifier):
        """Test notifier."""

        name = "test"
        schema = NotificationSchema

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

    return TestNotifier


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


def test_get_notifiers_from_entry_points(test_notifier):
    """Test getting notifiers from entry points."""
    # Mock pkg_resources.iter_entry_points
    with patch("importlib.metadata.entry_points") as mock_entry_points:
        # Create a mock entry point
        mock_entry_point = Mock()
        mock_entry_point.module = "notify_bridge.notifiers.test"
        mock_entry_point.attr = "TestNotifier"
        mock_entry_point.name = "test"

        # Mock entry_points() behavior for Python 3.10+
        mock_select = Mock()
        mock_select.return_value = [mock_entry_point]
        mock_entry_points.return_value.select = mock_select

        # Mock entry_points() behavior for Python 3.9 and below
        mock_entry_points.return_value.get = Mock(return_value=[mock_entry_point])

        # Mock load_notifier
        with patch(
            "notify_bridge.plugin.load_notifier",
            return_value=test_notifier,
        ):
            # Test getting notifiers
            notifiers = get_notifiers_from_entry_points()
            assert len(notifiers) == 1
            assert test_notifier.name.lower() in notifiers
            assert notifiers[test_notifier.name.lower()] == test_notifier


def test_load_plugins(tmp_path, monkeypatch):
    """Test loading plugins from a directory."""
    # Create a temporary plugin file
    plugin_dir = tmp_path / "plugins"
    plugin_dir.mkdir()
    plugin_file = plugin_dir / "test_plugin.py"
    plugin_file.write_text(
        """
from notify_bridge.components import BaseNotifier, NotificationResponse
from notify_bridge.schema import NotificationSchema
from typing import Dict, Any, Type

class TestPlugin(BaseNotifier):
    name = "test_plugin"
    schema = NotificationSchema

    def __init__(self, schema: Type[NotificationSchema], **kwargs: Any) -> None:
        super().__init__(schema=schema, **kwargs)

    def notify(self, notification: Dict[str, Any], **kwargs: Any) -> NotificationResponse:
        return NotificationResponse(success=True, name=self.name)

    async def anotify(self, notification: Dict[str, Any], **kwargs: Any) -> NotificationResponse:
        return NotificationResponse(success=True, name=self.name)

    def build_payload(self, data: Dict[str, Any]) -> Dict[str, Any]:
        return {}
"""
    )

    # Add plugin directory to Python path
    monkeypatch.syspath_prepend(str(plugin_dir))

    # Test loading plugins
    # Import local modules
    from notify_bridge.plugin import load_plugins

    plugins = load_plugins(str(plugin_dir))
    assert len(plugins) == 1
    assert "test_plugin" in plugins
    assert plugins["test_plugin"].name == "test_plugin"


def test_get_all_notifiers(tmp_path, monkeypatch, test_notifier):
    """Test getting all notifiers."""
    # Create a temporary plugin file
    plugin_dir = tmp_path / "plugins"
    plugin_dir.mkdir()
    plugin_file = plugin_dir / "test_plugin.py"
    plugin_file.write_text(
        """
from notify_bridge.components import BaseNotifier, NotificationResponse
from notify_bridge.schema import NotificationSchema
from typing import Dict, Any, Type

class TestPlugin(BaseNotifier):
    name = "test_plugin"
    schema = NotificationSchema

    def __init__(self, schema: Type[NotificationSchema], **kwargs: Any) -> None:
        super().__init__(schema=schema, **kwargs)

    def notify(self, notification: Dict[str, Any], **kwargs: Any) -> NotificationResponse:
        return NotificationResponse(success=True, name=self.name)

    async def anotify(self, notification: Dict[str, Any], **kwargs: Any) -> NotificationResponse:
        return NotificationResponse(success=True, name=self.name)

    def build_payload(self, data: Dict[str, Any]) -> Dict[str, Any]:
        return {}
"""
    )

    # Add plugin directory to Python path
    monkeypatch.syspath_prepend(str(plugin_dir))

    # Mock entry points
    with patch("importlib.metadata.entry_points") as mock_entry_points:
        mock_entry_point = Mock()
        mock_entry_point.module = "notify_bridge.notifiers.test"
        mock_entry_point.attr = "TestNotifier"
        mock_entry_point.name = "test"

        # Mock entry_points() behavior for Python 3.10+
        mock_select = Mock()
        mock_select.return_value = [mock_entry_point]
        mock_entry_points.return_value.select = mock_select

        # Mock entry_points() behavior for Python 3.9 and below
        mock_entry_points.return_value.get = Mock(return_value=[mock_entry_point])

        # Mock load_notifier
        with patch(
            "notify_bridge.plugin.load_notifier",
            return_value=test_notifier,
        ):
            # Test getting all notifiers
            # Import local modules
            from notify_bridge.plugin import get_all_notifiers

            notifiers = get_all_notifiers(str(plugin_dir))
            assert len(notifiers) >= 2  # At least the test notifier and test plugin
            assert test_notifier.name.lower() in notifiers
            assert "test_plugin" in notifiers


def test_get_notifier_class(tmp_path, monkeypatch, test_notifier):
    """Test getting a notifier class by name."""
    # Create a temporary plugin file
    plugin_dir = tmp_path / "plugins"
    plugin_dir.mkdir()
    plugin_file = plugin_dir / "test_plugin.py"
    plugin_file.write_text(
        """
from notify_bridge.components import BaseNotifier, NotificationResponse
from notify_bridge.schema import NotificationSchema
from typing import Dict, Any, Type

class TestPlugin(BaseNotifier):
    name = "test_plugin"
    schema = NotificationSchema

    def __init__(self, schema: Type[NotificationSchema], **kwargs: Any) -> None:
        super().__init__(schema=schema, **kwargs)

    def notify(self, notification: Dict[str, Any], **kwargs: Any) -> NotificationResponse:
        return NotificationResponse(success=True, name=self.name)

    async def anotify(self, notification: Dict[str, Any], **kwargs: Any) -> NotificationResponse:
        return NotificationResponse(success=True, name=self.name)

    def build_payload(self, data: Dict[str, Any]) -> Dict[str, Any]:
        return {}
"""
    )

    # Add plugin directory to Python path
    monkeypatch.syspath_prepend(str(plugin_dir))

    # Mock entry points
    with patch("importlib.metadata.entry_points") as mock_entry_points:
        mock_entry_point = Mock()
        mock_entry_point.module = "notify_bridge.notifiers.test"
        mock_entry_point.attr = "TestNotifier"
        mock_entry_point.name = "test"

        # Mock entry_points() behavior for Python 3.10+
        mock_select = Mock()
        mock_select.return_value = [mock_entry_point]
        mock_entry_points.return_value.select = mock_select

        # Mock entry_points() behavior for Python 3.9 and below
        mock_entry_points.return_value.get = Mock(return_value=[mock_entry_point])

        # Mock load_notifier
        with patch(
            "notify_bridge.plugin.load_notifier",
            return_value=test_notifier,
        ):
            # Test getting notifier class
            # Import local modules
            from notify_bridge.plugin import get_notifier_class

            # Test getting existing notifier
            notifier_class = get_notifier_class(test_notifier.name, str(plugin_dir))
            assert notifier_class == test_notifier

            # Test getting plugin notifier
            plugin_class = get_notifier_class("test_plugin", str(plugin_dir))
            assert plugin_class.name == "test_plugin"

            # Test getting non-existent notifier
            with pytest.raises(PluginError):
                get_notifier_class("non_existent", str(plugin_dir))


def test_load_plugins_invalid_directory():
    """Test loading plugins from an invalid directory."""
    # Import local modules
    from notify_bridge.plugin import load_plugins

    plugins = load_plugins("/non/existent/directory")
    assert len(plugins) == 0


def test_load_plugins_invalid_plugin():
    """Test loading an invalid plugin."""
    # Create a temporary plugin file with invalid code
    with patch("os.path.exists", return_value=True), patch("os.listdir", return_value=["invalid_plugin.py"]), patch(
        "importlib.import_module", side_effect=ImportError
    ):
        # Import local modules
        from notify_bridge.plugin import load_plugins

        plugins = load_plugins("/test/plugins")
        assert len(plugins) == 0
