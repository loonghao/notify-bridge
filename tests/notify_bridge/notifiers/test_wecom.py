"""Tests for WeCom notifier."""

# Import built-in modules
from typing import Any, Dict
from unittest.mock import AsyncMock, Mock, patch

# Import third-party modules
import pytest
from pydantic import ValidationError as PydanticValidationError

# Import local modules
from notify_bridge.exceptions import NotificationError, ValidationError
from notify_bridge.notifiers.wecom import WeComNotifier, WeComSchema


@pytest.fixture
def notifier() -> WeComNotifier:
    """Create a test notifier instance."""
    return WeComNotifier(webhook_url="https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key=test")


@pytest.fixture
def test_file(tmp_path) -> str:
    """Create a test file."""
    file_path = tmp_path / "test_file.txt"
    with open(file_path, "w") as f:
        f.write("Test content")
    return str(file_path)


def test_schema_validation():
    """Test schema validation."""
    # Test valid schema
    notification = WeComSchema(
        webhook_url="https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key=test",
        msg_type="text",
        content="Test Content"
    )
    assert notification.url == "https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key=test"
    assert notification.msg_type == "text"
    assert notification.content == "Test Content"

    # Test webhook_url to url conversion
    notification = WeComSchema(
        webhook_url="https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key=test",
        msg_type="text",
        content="Test Content"
    )
    assert notification.url == "https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key=test"

    # Test body to content conversion
    notification = WeComSchema(
        webhook_url="https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key=test",
        msg_type="text",
        body="Test Body"
    )
    assert notification.content == "Test Body"

    # Test invalid message type
    with pytest.raises(ValidationError):
        WeComSchema(
            webhook_url="https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key=test",
            msg_type="invalid",
            content="Test Content"
        )

    # Test missing webhook URL
    with pytest.raises(PydanticValidationError):
        WeComSchema(
            msg_type="text",
            content="Test Content"
        )


def test_wecom_text_message(notifier: WeComNotifier):
    """Test sending a text message."""
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"errcode": 0, "errmsg": "ok"}

    with patch("httpx.Client.post", return_value=mock_response):
        notification = {
            "url": "https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key=test",
            "msg_type": "text",
            "content": "Test Content"
        }
        response = notifier.notify(notification)
        assert response.success is True
        assert response.name == "wecom"
        assert response.data == {"errcode": 0, "errmsg": "ok"}


def test_wecom_markdown_message(notifier: WeComNotifier):
    """Test sending a markdown message."""
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"errcode": 0, "errmsg": "ok"}

    with patch("httpx.Client.post", return_value=mock_response):
        notification = {
            "url": "https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key=test",
            "msg_type": "markdown",
            "content": "# Test Content"
        }
        response = notifier.notify(notification)
        assert response.success is True
        assert response.name == "wecom"
        assert response.data == {"errcode": 0, "errmsg": "ok"}


def test_wecom_image_message(notifier: WeComNotifier, test_file):
    """Test sending an image message."""
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"errcode": 0, "errmsg": "ok"}

    with patch("httpx.Client.post", return_value=mock_response):
        notification = {
            "url": "https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key=test",
            "msg_type": "image",
            "image_path": test_file
        }
        response = notifier.notify(notification)
        assert response.success is True
        assert response.name == "wecom"
        assert response.data == {"errcode": 0, "errmsg": "ok"}


def test_wecom_file_message(notifier: WeComNotifier, test_file):
    """Test sending a file message."""
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.json.side_effect = [
        {"errcode": 0, "errmsg": "ok", "media_id": "test_media_id"},
        {"errcode": 0, "errmsg": "ok"}
    ]

    with patch("httpx.Client.post", return_value=mock_response):
        notification = {
            "url": "https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key=test",
            "msg_type": "file",
            "file_path": test_file
        }
        response = notifier.notify(notification)
        assert response.success is True
        assert response.name == "wecom"
        assert response.data == {"errcode": 0, "errmsg": "ok"}


def test_wecom_file_not_found(notifier: WeComNotifier):
    """Test sending a file that does not exist."""
    with pytest.raises(NotificationError, match="File not found"):
        notification = {
            "url": "https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key=test",
            "msg_type": "file",
            "file_path": "nonexistent_file.txt"
        }
        notifier.notify(notification)


def test_wecom_api_error(notifier: WeComNotifier):
    """Test API error handling."""
    mock_response = Mock()
    mock_response.status_code = 400
    mock_response.json.return_value = {"errcode": 1, "errmsg": "test error"}

    with patch("httpx.Client.post", return_value=mock_response):
        notification = {
            "url": "https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key=test",
            "msg_type": "text",
            "content": "Test Content"
        }
        with pytest.raises(NotificationError, match="WeCom API error: test error"):
            notifier.notify(notification)


@pytest.mark.asyncio
async def test_wecom_async_success(notifier: WeComNotifier):
    """Test successful async notification."""
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.json = AsyncMock(return_value={"errcode": 0, "errmsg": "ok"})

    with patch("httpx.AsyncClient.post", return_value=mock_response):
        notification = {
            "url": "https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key=test",
            "msg_type": "text",
            "content": "Test Content"
        }
        response = await notifier.notify_async(notification)
        assert response.success is True
        assert response.name == "wecom"
        assert response.data == {"errcode": 0, "errmsg": "ok"}


@pytest.mark.asyncio
async def test_wecom_async_error(notifier: WeComNotifier):
    """Test async notification error."""
    mock_response = Mock()
    mock_response.status_code = 400
    mock_response.json = AsyncMock(return_value={"errcode": 1, "errmsg": "test error"})

    with patch("httpx.AsyncClient.post", return_value=mock_response):
        notification = {
            "url": "https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key=test",
            "msg_type": "text",
            "content": "Test Content"
        }
        with pytest.raises(NotificationError):
            await notifier.notify_async(notification)
