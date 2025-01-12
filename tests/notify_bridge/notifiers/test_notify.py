"""Tests for Notify notifier."""

# Import third-party modules

# Import local modules
from notify_bridge.components import MessageType
from notify_bridge.notifiers.notify import NotifyNotifier, NotifySchema


def test_notify_schema_validation():
    """Test Notify schema validation."""
    # Test valid schema with new usage
    valid_data = {
        "base_url": "https://notify.example.com",
        "token": "test-token",
        "title": "Test Notification",
        "message": "Test content",  # Using message instead of content
        "tags": ["test", "notify"],
        "icon": "https://example.com/icon.png",
        "msg_type": "text",
    }
    schema = NotifySchema(**valid_data)
    assert schema.base_url == "https://notify.example.com"
    assert schema.token == "test-token"
    assert schema.content == "Test content"  # Verify content is set from message
    assert schema.tags == ["test", "notify"]
    assert schema.icon == "https://example.com/icon.png"
    assert schema.msg_type == MessageType.TEXT


def test_notify_notifier_initialization():
    """Test Notify notifier initialization."""
    notifier = NotifyNotifier()
    assert notifier.name == "notify"
    assert notifier.schema_class == NotifySchema
    assert MessageType.TEXT in notifier.supported_types
