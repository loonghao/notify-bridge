"""Tests for Feishu notifier."""

# Import built-in modules
import base64
from pathlib import Path
import pytest
from typing import Dict, Any

# Import third-party modules
from pydantic import ValidationError

# Import local modules
from notify_bridge.components import MessageType, NotificationError
from notify_bridge.notifiers.feishu import (
    CardConfig,
    CardHeader,
    FeishuNotifier,
    FeishuSchema
)

def test_card_config():
    """Test CardConfig model."""
    # Test default values
    config = CardConfig()
    assert config.wide_screen_mode is True

    # Test custom values
    config = CardConfig(wide_screen_mode=False)
    assert config.wide_screen_mode is False

def test_card_header():
    """Test CardHeader model."""
    # Test with required fields
    header = CardHeader(title="Test Title")
    assert header.title == "Test Title"
    assert header.template == "blue"  # Default value

    # Test with custom template
    header = CardHeader(title="Test Title", template="red")
    assert header.title == "Test Title"
    assert header.template == "red"

def test_feishu_notifier_initialization():
    """Test FeishuNotifier initialization."""
    notifier = FeishuNotifier()
    assert notifier.name == "feishu"
    assert notifier.schema_class == FeishuSchema
    assert MessageType.TEXT in notifier.supported_types
    assert MessageType.POST in notifier.supported_types
    assert MessageType.IMAGE in notifier.supported_types
    assert MessageType.FILE in notifier.supported_types
    assert MessageType.INTERACTIVE in notifier.supported_types

def test_build_text_payload():
    """Test text message payload building."""
    notifier = FeishuNotifier()
    notification = FeishuSchema(
        webhook_url="https://test.url",
        msg_type=MessageType.TEXT,
        content="Test content"
    )
    payload = notifier.build_payload(notification)
    assert payload["msg_type"] == "text"
    assert payload["content"]["text"] == "Test content"

def test_build_post_payload():
    """Test post message payload building."""
    notifier = FeishuNotifier()
    post_content = {
        "zh_cn": [[{"tag": "text", "text": "Test post"}]]
    }
    notification = FeishuSchema(
        webhook_url="https://test.url",
        msg_type=MessageType.POST,
        post_content=post_content
    )
    payload = notifier.build_payload(notification)
    assert payload["msg_type"] == "post"
    assert payload["content"]["post"] == post_content

    # Test without post_content
    notification = FeishuSchema(
        webhook_url="https://test.url",
        msg_type=MessageType.POST
    )
    with pytest.raises(NotificationError):
        notifier.build_payload(notification)

def test_build_image_payload(tmp_path: Path):
    """Test image message payload building."""
    notifier = FeishuNotifier()
    
    # Create a test image file
    image_path = tmp_path / "test.png"
    image_content = b"test image content"
    image_path.write_bytes(image_content)
    
    notification = FeishuSchema(
        webhook_url="https://test.url",
        msg_type=MessageType.IMAGE,
        image_path=str(image_path)
    )
    payload = notifier.build_payload(notification)
    assert payload["msg_type"] == "image"
    assert payload["content"]["base64"] == base64.b64encode(image_content).decode()

    # Test with non-existent image
    notification.image_path = "non_existent.png"
    with pytest.raises(NotificationError):
        notifier.build_payload(notification)

    # Test without image_path
    notification = FeishuSchema(
        webhook_url="https://test.url",
        msg_type=MessageType.IMAGE
    )
    with pytest.raises(NotificationError):
        notifier.build_payload(notification)

def test_build_file_payload(tmp_path: Path):
    """Test file message payload building."""
    notifier = FeishuNotifier()
    
    # Create a test file
    file_path = tmp_path / "test.txt"
    file_path.write_text("test content")
    
    notification = FeishuSchema(
        webhook_url="https://test.url",
        msg_type=MessageType.FILE,
        file_path=str(file_path),
        token="test_token"
    )
    
    # Test file upload not implemented
    with pytest.raises(NotificationError) as exc_info:
        notifier.build_payload(notification)
    assert "File upload not implemented yet" in str(exc_info.value)

    # Test without file_path
    notification = FeishuSchema(
        webhook_url="https://test.url",
        msg_type=MessageType.FILE,
        token="test_token"
    )
    with pytest.raises(NotificationError):
        notifier.build_payload(notification)

    # Test without token
    notification = FeishuSchema(
        webhook_url="https://test.url",
        msg_type=MessageType.FILE,
        file_path=str(file_path)
    )
    with pytest.raises(NotificationError):
        notifier.build_payload(notification)

def test_build_interactive_payload():
    """Test interactive message payload building."""
    notifier = FeishuNotifier()
    card_header = CardHeader(title="Test Header")
    card_elements = [{"tag": "div", "text": "Test Element"}]
    
    notification = FeishuSchema(
        webhook_url="https://test.url",
        msg_type=MessageType.INTERACTIVE,
        card_header=card_header,
        card_elements=card_elements
    )
    payload = notifier.build_payload(notification)
    assert payload["msg_type"] == "interactive"
    assert payload["card"]["header"]["title"]["content"] == "Test Header"
    assert payload["card"]["elements"] == card_elements
    assert payload["card"]["config"]["wide_screen_mode"] is True

    # Test with custom card config
    notification.card_config = CardConfig(wide_screen_mode=False)
    payload = notifier.build_payload(notification)
    assert payload["card"]["config"]["wide_screen_mode"] is False

    # Test without card_header
    notification = FeishuSchema(
        webhook_url="https://test.url",
        msg_type=MessageType.INTERACTIVE,
        card_elements=card_elements
    )
    with pytest.raises(NotificationError):
        notifier.build_payload(notification)

    # Test without card_elements
    notification = FeishuSchema(
        webhook_url="https://test.url",
        msg_type=MessageType.INTERACTIVE,
        card_header=card_header
    )
    with pytest.raises(NotificationError):
        notifier.build_payload(notification)

def test_feishu_notifier_validation():
    """Test FeishuNotifier validation."""
    notifier = FeishuNotifier()

    # Test text message validation
    text_data = {
        "webhook_url": "https://test.url",
        "msg_type": MessageType.TEXT,
        "content": "Test content"
    }
    notification = FeishuSchema(**text_data)
    notifier.build_payload(notification)

    # Test text message without content
    text_data["content"] = None
    notification = FeishuSchema(**text_data)
    with pytest.raises(NotificationError):
        notifier.build_payload(notification)

    # Test post message validation
    post_data = {
        "webhook_url": "https://test.url",
        "msg_type": MessageType.POST,
        "post_content": {
            "zh_cn": [
                [{"tag": "text", "text": "Test Content"}]
            ]
        }
    }
    notification = FeishuSchema(**post_data)
    notifier.build_payload(notification)

    # Test post message without post_content
    post_data["post_content"] = None
    notification = FeishuSchema(**post_data)
    with pytest.raises(NotificationError):
        notifier.build_payload(notification)

    # Test interactive message validation
    interactive_data = {
        "webhook_url": "https://test.url",
        "msg_type": MessageType.INTERACTIVE,
        "card_header": {"title": "Test Header"},
        "card_elements": [{"tag": "div", "text": "Test Element"}]
    }
    notification = FeishuSchema(**interactive_data)
    notifier.build_payload(notification)

    # Test interactive message without required fields
    interactive_data["card_header"] = None
    notification = FeishuSchema(**interactive_data)
    with pytest.raises(NotificationError):
        notifier.build_payload(notification)

    interactive_data["card_elements"] = None
    notification = FeishuSchema(**interactive_data)
    with pytest.raises(NotificationError):
        notifier.build_payload(notification)

def test_invalid_schema():
    """Test invalid schema handling."""
    notifier = FeishuNotifier()
    with pytest.raises(NotificationError):
        notifier.build_payload(object())

def test_unsupported_message_type():
    """Test unsupported message type handling."""
    notifier = FeishuNotifier()
    
    # Create a notification with unsupported message type
    notification = FeishuSchema(
        webhook_url="https://test.url",
        msg_type=MessageType.MARKDOWN  # Not in supported_types
    )
    with pytest.raises(NotificationError) as exc_info:
        notifier.build_payload(notification)
    assert "Unsupported message type: markdown" in str(exc_info.value)
