"""Tests for the Feishu notifier."""

# Import built-in modules
from unittest.mock import AsyncMock, Mock, patch

# Import third-party modules
import pytest
from pydantic import ValidationError as PydanticValidationError

# Import local modules
from notify_bridge.exceptions import NotificationError, ValidationError
from notify_bridge.notifiers.feishu import FeishuNotifier, FeishuSchema


@pytest.fixture
def notifier():
    """Create a FeishuNotifier instance."""
    return FeishuNotifier()


def test_schema_validation():
    """Test schema validation."""
    # Test valid schema
    notification = FeishuSchema(
        webhook_url="https://example.com/webhook",
        msg_type="text",
        content="Test Content"
    )
    assert notification.url == "https://example.com/webhook"
    assert notification.msg_type == "text"
    assert notification.content == "Test Content"

    # Test webhook_url to url conversion
    notification = FeishuSchema(
        webhook_url="https://example.com/webhook",
        msg_type="text",
        content="Test Content"
    )
    assert notification.url == "https://example.com/webhook"

    # Test body to content conversion
    notification = FeishuSchema(
        webhook_url="https://example.com/webhook",
        msg_type="text",
        body="Test Body"
    )
    assert notification.content == "Test Body"

    # Test invalid message type
    with pytest.raises(ValidationError):
        FeishuSchema(
            webhook_url="https://example.com/webhook",
            msg_type="invalid",
            content="Test Content"
        )

    # Test missing webhook URL
    with pytest.raises(PydanticValidationError):
        FeishuSchema(
            msg_type="text",
            content="Test Content"
        )


def test_build_text_payload(notifier):
    """Test building text message payload."""
    notification = {
        "url": "https://example.com/webhook",
        "msg_type": "text",
        "content": "Test Content"
    }
    payload = notifier._build_text_payload(notification)
    assert payload == {
        "msg_type": "text",
        "content": {
            "text": "Test Content"
        }
    }


def test_build_post_payload(notifier):
    """Test building post message payload."""
    notification = {
        "url": "https://example.com/webhook",
        "msg_type": "post",
        "title": "Test Title",
        "content": "Test Content"
    }
    payload = notifier._build_post_payload(notification)
    assert payload == {
        "msg_type": "post",
        "content": {
            "post": {
                "zh_cn": {
                    "title": "Test Title",
                    "content": [
                        [
                            {
                                "tag": "text",
                                "text": "Test Content"
                            }
                        ]
                    ]
                }
            }
        }
    }


def test_build_image_payload(notifier):
    """Test building image message payload."""
    notification = {
        "url": "https://example.com/webhook",
        "msg_type": "image",
        "image_path": "test.jpg"
    }
    payload = notifier._build_image_payload(notification)
    assert payload == {
        "msg_type": "image",
        "content": {
            "image_key": "test.jpg"
        }
    }


def test_build_file_payload(notifier):
    """Test building file message payload."""
    notification = {
        "url": "https://example.com/webhook",
        "msg_type": "file",
        "file_path": "test.txt"
    }
    payload = notifier._build_file_payload(notification)
    assert payload == {
        "msg_type": "file",
        "content": {
            "file_key": "test.txt"
        }
    }


def test_build_payload(notifier):
    """Test building notification payload."""
    notification = {
        "url": "https://example.com/webhook",
        "msg_type": "text",
        "content": "Test Content"
    }
    payload = notifier._build_payload(notification)
    assert payload == {
        "url": "https://example.com/webhook",
        "json": {
            "msg_type": "text",
            "content": {
                "text": "Test Content"
            }
        }
    }


def test_build_payload_with_schema(notifier):
    """Test building notification payload with schema."""
    notification = FeishuSchema(
        webhook_url="https://example.com/webhook",
        msg_type="text",
        content="Test Content"
    )
    payload = notifier.build_payload(notification)
    assert payload == {
        "url": "https://example.com/webhook",
        "json": {
            "msg_type": "text",
            "content": {
                "text": "Test Content"
            }
        }
    }


def test_notify_success(notifier):
    """Test successful notification."""
    with patch("httpx.Client") as mock_client:
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"code": 0, "data": {}, "msg": "success"}
        mock_client.return_value.post.return_value = mock_response

        notification = {
            "url": "https://example.com/webhook",
            "msg_type": "text",
            "content": "Test Content"
        }
        response = notifier.notify(notification)
        assert response.success
        assert response.name == "feishu"
        assert response.data == {"code": 0, "data": {}, "msg": "success"}


def test_notify_error(notifier):
    """Test notification error."""
    with patch("httpx.Client") as mock_client:
        mock_response = Mock()
        mock_response.status_code = 400
        mock_response.json.return_value = {"code": 19001, "data": {}, "msg": "param invalid"}
        mock_client.return_value.post.return_value = mock_response

        notification = {
            "url": "https://example.com/webhook",
            "msg_type": "text",
            "content": "Test Content"
        }
        response = notifier.notify(notification)
        assert response.success
        assert response.name == "feishu"
        assert response.data == {"code": 19001, "data": {}, "msg": "param invalid"}


@pytest.mark.asyncio
async def test_notify_async_success(notifier):
    """Test successful async notification."""
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.json = AsyncMock(return_value={"code": 0, "data": {}, "msg": "success"})

    with patch("httpx.AsyncClient.post", return_value=mock_response):
        notification = {
            "url": "https://example.com/webhook",
            "msg_type": "text",
            "content": "Test Content"
        }
        response = await notifier.notify_async(notification)
        assert response.success is True
        assert response.name == "feishu"
        assert response.data == {"code": 0, "data": {}, "msg": "success"}


@pytest.mark.asyncio
async def test_notify_async_error(notifier):
    """Test async notification error."""
    mock_response = Mock()
    mock_response.status_code = 400
    mock_response.json = AsyncMock(return_value={"code": 19001, "data": {}, "msg": "param invalid"})

    with patch("httpx.AsyncClient.post", return_value=mock_response):
        notification = {
            "url": "https://example.com/webhook",
            "msg_type": "text",
            "content": "Test Content"
        }
        with pytest.raises(NotificationError):
            await notifier.notify_async(notification)
