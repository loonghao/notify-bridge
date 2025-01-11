"""Tests for Notify notifier."""

# Import third-party modules
from pydantic import ValidationError
import pytest

# Import local modules
from notify_bridge.components import MessageType
from notify_bridge.components import NotificationError
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

    # Test required fields
    with pytest.raises(ValidationError):
        NotifySchema(title="Test")  # Missing required fields


def test_notify_notifier_initialization():
    """Test Notify notifier initialization."""
    notifier = NotifyNotifier()
    assert notifier.name == "notify"
    assert notifier.schema_class == NotifySchema
    assert MessageType.TEXT in notifier.supported_types


def test_notify_headers():
    """Test Notify headers generation."""
    notifier = NotifyNotifier()

    # Test without token
    headers = notifier._get_headers()
    assert headers["Content-Type"] == "application/json"
    assert "Authorization" not in headers

    # Test with token
    token = "test-token"
    headers = notifier._get_headers(token)
    assert headers["Content-Type"] == "application/json"
    assert headers["Authorization"] == f"Bearer {token}"


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
    payload = notifier.build_payload(notification)

    assert payload["title"] == "Test Notification"
    assert payload["message"] == "Test content"
    assert "icon" not in payload
    assert "tags" not in payload

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
    payload = notifier.build_payload(notification)

    assert payload["title"] == "Test Notification"
    assert payload["message"] == "Test content"
    assert payload["icon"] == "https://example.com/icon.png"
    assert payload["tags"] == ["test", "notify"]

    # Test with invalid schema
    with pytest.raises(NotificationError):
        notifier.build_payload(object())  # Pass invalid schema object
