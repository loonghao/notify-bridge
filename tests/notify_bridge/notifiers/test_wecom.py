"""Test WeCom notifier implementation."""

# Import built-in modules
from pathlib import Path

# Import third-party modules
import pytest
from pydantic import ValidationError

# Import local modules
from notify_bridge.components import MessageType, NotificationError
from notify_bridge.notifiers.wecom import Article, WeComNotifier, WeComSchema


def test_article_schema():
    """Test Article schema."""
    # Test valid article
    article_data = {
        "title": "Test Title",
        "description": "Test Description",
        "url": "https://test.url",
        "picurl": "https://test.url/image.png"
    }
    article = Article(**article_data)
    assert article.title == "Test Title"
    assert article.description == "Test Description"
    assert article.url == "https://test.url"
    assert article.picurl == "https://test.url/image.png"

    # Test article without optional fields
    article = Article(
        title="Test Title",
        url="https://test.url"
    )
    assert article.title == "Test Title"
    assert article.description is None
    assert article.url == "https://test.url"
    assert article.picurl is None


def test_wecom_notifier_initialization():
    """Test WeComNotifier initialization."""
    notifier = WeComNotifier()
    assert notifier.name == "wecom"
    assert notifier.schema_class == WeComSchema
    assert MessageType.TEXT in notifier.supported_types
    assert MessageType.MARKDOWN in notifier.supported_types
    assert MessageType.IMAGE in notifier.supported_types
    assert MessageType.NEWS in notifier.supported_types


def test_build_text_payload():
    """Test text message payload building."""
    notifier = WeComNotifier()

    # Test text message with mentions
    notification = WeComSchema(
        webhook_url="https://test.url",
        msg_type=MessageType.TEXT,
        content="Test content",
        mentioned_list=["user1", "user2"],
        mentioned_mobile_list=["12345678901"]
    )
    payload = notifier.build_payload(notification)
    assert payload["msgtype"] == "text"
    assert payload["text"]["content"] == "Test content"
    assert payload["text"]["mentioned_list"] == ["user1", "user2"]
    assert payload["text"]["mentioned_mobile_list"] == ["12345678901"]

    # Test text message without mentions
    notification = WeComSchema(
        webhook_url="https://test.url",
        msg_type=MessageType.TEXT,
        content="Test content"
    )
    payload = notifier.build_payload(notification)
    assert payload["msgtype"] == "text"
    assert payload["text"]["content"] == "Test content"
    assert payload["text"]["mentioned_list"] == []
    assert payload["text"]["mentioned_mobile_list"] == []

    # Test text message without content
    with pytest.raises(NotificationError):
        notification = WeComSchema(
            webhook_url="https://test.url",
            msg_type=MessageType.TEXT
        )
        notifier.build_payload(notification)


def test_build_markdown_payload():
    """Test markdown message payload building."""
    notifier = WeComNotifier()

    # Test markdown message
    notification = WeComSchema(
        webhook_url="https://test.url",
        msg_type=MessageType.MARKDOWN,
        content="# Test Title\n\nTest content"
    )
    payload = notifier.build_payload(notification)
    assert payload["msgtype"] == "markdown"
    assert payload["markdown"]["content"] == "# Test Title\n\nTest content"

    # Test markdown message without content
    with pytest.raises(NotificationError):
        notification = WeComSchema(
            webhook_url="https://test.url",
            msg_type=MessageType.MARKDOWN
        )
        notifier.build_payload(notification)


def test_build_image_payload(tmp_path: Path):
    """Test image message payload building."""
    notifier = WeComNotifier()

    # Create a test image file
    image_path = tmp_path / "test.png"
    image_content = b"test image content"
    image_path.write_bytes(image_content)

    # Test image message
    notification = WeComSchema(
        webhook_url="https://test.url",
        msg_type=MessageType.IMAGE,
        image_path=str(image_path)
    )
    payload = notifier.build_payload(notification)
    assert payload["msgtype"] == "image"
    assert "base64" in payload["image"]
    assert "md5" in payload["image"]

    # Test image message without image_path
    with pytest.raises(NotificationError):
        notification = WeComSchema(
            webhook_url="https://test.url",
            msg_type=MessageType.IMAGE
        )
        notifier.build_payload(notification)

    # Test with non-existent image file
    with pytest.raises(NotificationError):
        notification = WeComSchema(
            webhook_url="https://test.url",
            msg_type=MessageType.IMAGE,
            image_path="non_existent.png"
        )
        notifier.build_payload(notification)


def test_build_news_payload():
    """Test news message payload building."""
    notifier = WeComNotifier()

    # Test news message with all fields
    articles = [
        Article(
            title="Test Title 1",
            description="Test Description 1",
            url="https://test.url/1",
            picurl="https://test.url/image1.png"
        ),
        Article(
            title="Test Title 2",
            url="https://test.url/2"
        )
    ]
    notification = WeComSchema(
        webhook_url="https://test.url",
        msg_type=MessageType.NEWS,
        articles=articles,
        mentioned_list=["user1"],
        mentioned_mobile_list=["12345678901"]
    )
    payload = notifier.build_payload(notification)
    assert payload["msgtype"] == "news"
    assert len(payload["news"]["articles"]) == 2
    assert payload["news"]["articles"][0]["title"] == "Test Title 1"
    assert payload["news"]["articles"][0]["description"] == "Test Description 1"
    assert payload["news"]["articles"][0]["url"] == "https://test.url/1"
    assert payload["news"]["articles"][0]["picurl"] == "https://test.url/image1.png"
    assert payload["news"]["articles"][1]["title"] == "Test Title 2"
    assert payload["news"]["articles"][1]["url"] == "https://test.url/2"
    assert "description" not in payload["news"]["articles"][1]
    assert "picurl" not in payload["news"]["articles"][1]
    assert payload["text"]["mentioned_list"] == ["user1"]
    assert payload["text"]["mentioned_mobile_list"] == ["12345678901"]

    # Test news message without articles
    with pytest.raises(NotificationError):
        notification = WeComSchema(
            webhook_url="https://test.url",
            msg_type=MessageType.NEWS
        )
        notifier.build_payload(notification)


def test_wecom_notifier_validation():
    """Test WeComNotifier validation."""
    notifier = WeComNotifier()

    # Test text message validation
    text_data = {
        "webhook_url": "https://test.url",
        "msg_type": MessageType.TEXT,
        "content": "Test content"
    }
    notification = WeComSchema(**text_data)
    notifier.build_payload(notification)

    # Test text message without content
    text_data["content"] = None
    notification = WeComSchema(**text_data)
    with pytest.raises(NotificationError):
        notifier.build_payload(notification)

    # Test markdown message validation
    markdown_data = {
        "webhook_url": "https://test.url",
        "msg_type": MessageType.MARKDOWN,
        "content": "# Test Title"
    }
    notification = WeComSchema(**markdown_data)
    notifier.build_payload(notification)

    # Test markdown message without content
    markdown_data["content"] = None
    notification = WeComSchema(**markdown_data)
    with pytest.raises(NotificationError):
        notifier.build_payload(notification)


def test_invalid_schema():
    """Test invalid schema handling."""
    notifier = WeComNotifier()

    # Test invalid schema type
    with pytest.raises(NotificationError):
        notifier.build_payload(object())


def test_unsupported_message_type():
    """Test unsupported message type handling."""
    notifier = WeComNotifier()

    # Create a notification with unsupported message type
    notification = WeComSchema(
        webhook_url="https://test.url",
        msg_type=MessageType.FILE  # Not in supported_types
    )
    with pytest.raises(NotificationError) as exc_info:
        notifier.build_payload(notification)
    assert "Unsupported message type: file" in str(exc_info.value)
