"""Tests for Notify notifier."""

# Import third-party modules
import pytest

# Import local modules
from notify_bridge.components import MessageType
from notify_bridge.notifiers.notify import NotifyNotifier
from notify_bridge.notifiers.notify import NotifySchema


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


def test_notify_build_payload():
    """Test Notify payload building."""
    notifier = NotifyNotifier()

    # Test with minimal data using new usage
    minimal_data = {
        "base_url": "https://notify.example.com",
        "title": "Test Notification",
        "message": "Test content",  # Using message instead of content
        "msg_type": "text",
    }
    notification = NotifySchema(**minimal_data)
    data = notifier.assemble_data(notification)

    assert data["title"] == "Test Notification"
    assert data["message"] == "Test content"
    assert "icon" not in data
    assert "tags" not in data

    # Test with all optional fields using new usage
    full_data = {
        "base_url": "https://notify.example.com",
        "token": "test-token",
        "title": "Test Notification",
        "message": "Test content",  # Using message instead of content
        "tags": ["test", "notify"],
        "icon": "https://example.com/icon.png",
        "msg_type": "text",
    }
    notification = NotifySchema(**full_data)
    data = notifier.assemble_data(notification)

    assert data["title"] == "Test Notification"
    assert data["message"] == "Test content"
    assert data["icon"] == "https://example.com/icon.png"
    assert data["tags"] == ["test", "notify"]

    # Test with invalid schema
    with pytest.raises(AttributeError):
        notifier.assemble_data(object())  # Pass invalid schema object
