"""Test WeCom notifier implementation."""

# Import built-in modules
from pathlib import Path

# Import third-party modules
import pytest

# Import local modules
from notify_bridge.components import MessageType
from notify_bridge.exceptions import NotificationError
from notify_bridge.notifiers.wecom import Article, WeComNotifier, WeComSchema


def test_article_schema():
    """Test Article schema."""
    # Test valid article
    article_data = {
        "title": "Test Title",
        "description": "Test Description",
        "url": "https://test.url",
        "picurl": "https://test.url/image.png",
    }
    article = Article(**article_data)
    assert article.title == "Test Title"
    assert article.description == "Test Description"
    assert article.url == "https://test.url"
    assert article.picurl == "https://test.url/image.png"

    # Test article without optional fields
    article = Article(title="Test Title", url="https://test.url")
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
        msg_type="text",
        content="Test content",
        mentioned_list=["user1", "user2"],
        mentioned_mobile_list=["12345678901"],
    )
    payload = notifier.assemble_data(notification)
    assert payload["msgtype"] == "text"
    assert payload["text"]["content"] == "Test content"
    assert payload["text"]["mentioned_list"] == ["user1", "user2"]
    assert payload["text"]["mentioned_mobile_list"] == ["12345678901"]

    # Test text message without mentions
    notification = WeComSchema(webhook_url="https://test.url", msg_type="text", content="Test content")
    payload = notifier.assemble_data(notification)
    assert payload["msgtype"] == "text"
    assert payload["text"]["content"] == "Test content"
    assert payload["text"]["mentioned_list"] == []
    assert payload["text"]["mentioned_mobile_list"] == []


def test_build_markdown_payload():
    """Test markdown message payload building."""
    notifier = WeComNotifier()

    # Test markdown message
    notification = WeComSchema(
        webhook_url="https://test.url", msg_type="markdown", content="# Test Title\n\nTest content"
    )
    payload = notifier.assemble_data(notification)
    assert payload["msgtype"] == "markdown"
    assert payload["markdown"]["content"] == "# Test Title\n\nTest content"


def test_build_image_payload(tmp_path: Path):
    """Test image message payload building."""
    notifier = WeComNotifier()

    # Create a test image file
    image_path = tmp_path / "test.png"
    image_path.write_bytes(b"test image content")

    # Test image message
    notification = WeComSchema(webhook_url="https://test.url", msg_type="image", image_path=str(image_path))
    payload = notifier.assemble_data(notification)
    assert payload["msgtype"] == "image"
    assert "base64" in payload["image"]
    assert "md5" in payload["image"]


def test_build_news_payload():
    """Test news message payload building."""
    notifier = WeComNotifier()

    # Test news message
    notification = WeComSchema(
        webhook_url="https://test.url",
        msg_type="news",
        articles=[
            {
                "title": "Test Title",
                "description": "Test Description",
                "url": "https://test.url",
                "picurl": "https://test.url/image.png",
            }
        ],
    )
    payload = notifier.assemble_data(notification)
    assert payload["msgtype"] == "news"
    assert len(payload["news"]["articles"]) == 1
    assert payload["news"]["articles"][0]["title"] == "Test Title"
    assert payload["news"]["articles"][0]["description"] == "Test Description"
    assert payload["news"]["articles"][0]["url"] == "https://test.url"
    assert payload["news"]["articles"][0]["picurl"] == "https://test.url/image.png"


def test_invalid_schema():
    """Test invalid schema handling."""
    notifier = WeComNotifier()
    with pytest.raises(NotificationError):
        notifier.assemble_data({"invalid": "data"})
