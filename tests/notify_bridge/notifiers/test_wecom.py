"""Tests for WeCom notifier."""

# Import built-in modules
from typing import Any, Dict

# Import third-party modules
import pytest
from pytest_mock import MockerFixture

# Import local modules
from notify_bridge.exceptions import NotificationError
from notify_bridge.notifiers.wecom import WeComNotifier


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


@pytest.fixture
def mock_response(mocker: MockerFixture) -> Dict[str, Any]:
    """Mock successful API response."""
    return {"errcode": 0, "errmsg": "ok"}


@pytest.fixture
def mock_requests(mocker: MockerFixture, mock_response: Dict[str, Any]):
    """Mock requests."""
    mock = mocker.patch("notify_bridge.utils.requests.RequestsHelper")
    mock_instance = mock.return_value
    mock_instance.post.return_value.json.return_value = mock_response
    mock_instance.apost.return_value.json.return_value = mock_response
    return mock_instance


def test_wecom_text_message(notifier: WeComNotifier, mock_requests):
    """Test sending a text message."""
    response = notifier.send({
        "title": "Test Title",
        "body": "Test Body",
        "msg_type": "text"
    })
    assert response.success
    assert response.notifier == "wecom"
    mock_requests.post.assert_called_once()
    payload = mock_requests.post.call_args[1]["json"]
    assert payload["msgtype"] == "text"
    assert "Test Title\nTest Body" in payload["text"]["content"]


def test_wecom_markdown_message(notifier: WeComNotifier, mock_requests):
    """Test sending a markdown message."""
    response = notifier.send({
        "title": "Test Title",
        "body": "# Test Body\n**Bold Text**",
        "msg_type": "markdown"
    })
    assert response.success
    assert response.notifier == "wecom"
    mock_requests.post.assert_called_once()
    payload = mock_requests.post.call_args[1]["json"]
    assert payload["msgtype"] == "markdown"
    assert "# Test Title\n# Test Body\n**Bold Text**" in payload["markdown"]["content"]


def test_wecom_news_message(notifier: WeComNotifier, mock_requests):
    """Test sending a news message."""
    response = notifier.send({
        "title": "Test Title",
        "body": "Test Body",
        "msg_type": "news",
        "articles": [
            {
                "title": "Article 1",
                "description": "Description 1",
                "url": "https://example.com",
                "picurl": "https://example.com/image.jpg"
            }
        ]
    })
    assert response.success
    assert response.notifier == "wecom"
    mock_requests.post.assert_called_once()
    payload = mock_requests.post.call_args[1]["json"]
    assert payload["msgtype"] == "news"
    assert len(payload["news"]["articles"]) == 1
    assert payload["news"]["articles"][0]["title"] == "Article 1"


def test_wecom_news_message_with_local_image(notifier: WeComNotifier, mock_requests, test_file):
    """Test sending a news message with local image."""
    response = notifier.send({
        "title": "Test Title",
        "body": "Test Body",
        "msg_type": "news",
        "articles": [
            {
                "title": "Article 1",
                "description": "Description 1",
                "url": "https://example.com",
                "picurl": test_file
            }
        ]
    })
    assert response.success
    assert response.notifier == "wecom"
    mock_requests.post.assert_called_once()
    payload = mock_requests.post.call_args[1]["json"]
    assert payload["msgtype"] == "news"
    assert len(payload["news"]["articles"]) == 1
    assert payload["news"]["articles"][0]["title"] == "Article 1"


def test_wecom_image_message(notifier: WeComNotifier, mock_requests, test_file):
    """Test sending an image message."""
    response = notifier.send({
        "title": "Test Title",
        "body": test_file,
        "msg_type": "image"
    })
    assert response.success
    assert response.notifier == "wecom"
    mock_requests.post.assert_called_once()
    payload = mock_requests.post.call_args[1]["json"]
    assert payload["msgtype"] == "image"
    assert "base64" in payload["image"]
    assert "md5" in payload["image"]


def test_wecom_file_message(notifier: WeComNotifier, mock_requests, test_file):
    """Test sending a file message."""
    mock_requests.post.return_value.json.side_effect = [
        {"errcode": 0, "errmsg": "ok", "media_id": "test_media_id"},
        {"errcode": 0, "errmsg": "ok"}
    ]
    response = notifier.send({
        "title": "Test Title",
        "body": test_file,
        "msg_type": "file"
    })
    assert response.success
    assert response.notifier == "wecom"
    assert mock_requests.post.call_count == 2
    payload = mock_requests.post.call_args[1]["json"]
    assert payload["msgtype"] == "file"
    assert payload["file"]["media_id"] == "test_media_id"


def test_wecom_file_not_found(notifier: WeComNotifier):
    """Test sending a file that does not exist."""
    with pytest.raises(NotificationError, match="File not found"):
        notifier.send({
            "title": "Test Title",
            "body": "nonexistent_file.txt",
            "msg_type": "file"
        })


def test_wecom_api_error(notifier: WeComNotifier, mocker: MockerFixture):
    """Test API error handling."""
    mock = mocker.patch("notify_bridge.utils.requests.RequestsHelper")
    mock.return_value.post.return_value.json.return_value = {
        "errcode": 1,
        "errmsg": "test error"
    }
    with pytest.raises(NotificationError, match="WeCom API error: test error"):
        notifier.send({
            "title": "Test Title",
            "body": "Test Body",
            "msg_type": "text"
        })


@pytest.mark.asyncio
async def test_wecom_async_send(notifier: WeComNotifier, mock_requests):
    """Test async message sending."""
    response = await notifier.asend({
        "title": "Test Title",
        "body": "Test Body",
        "msg_type": "text"
    })
    assert response.success
    assert response.notifier == "wecom"
    mock_requests.apost.assert_called_once()
    payload = mock_requests.apost.call_args[1]["json"]
    assert payload["msgtype"] == "text"
    assert "Test Title\nTest Body" in payload["text"]["content"]


@pytest.mark.asyncio
async def test_wecom_async_send_with_file(notifier: WeComNotifier, mock_requests, test_file):
    """Test async file message sending."""
    mock_requests.post.return_value.json.side_effect = [
        {"errcode": 0, "errmsg": "ok", "media_id": "test_media_id"},
        {"errcode": 0, "errmsg": "ok"}
    ]
    mock_requests.apost.return_value.json.return_value = {"errcode": 0, "errmsg": "ok"}
    response = await notifier.asend({
        "title": "Test Title",
        "body": test_file,
        "msg_type": "file"
    })
    assert response.success
    assert response.notifier == "wecom"
    assert mock_requests.post.call_count == 1
    assert mock_requests.apost.call_count == 1
    payload = mock_requests.apost.call_args[1]["json"]
    assert payload["msgtype"] == "file"
    assert payload["file"]["media_id"] == "test_media_id"
