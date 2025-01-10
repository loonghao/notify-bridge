"""Tests for the Feishu notifier."""

# Import built-in modules
from unittest.mock import AsyncMock, Mock, patch

# Import third-party modules
import pytest

# Import local modules
from notify_bridge.exceptions import NotificationError
from notify_bridge.notifiers.feishu import FeishuNotifier, FeishuSchema


@pytest.fixture
def notifier():
    """Create a FeishuNotifier instance."""
    return FeishuNotifier()


def test_prepare_text_message(notifier):
    """Test preparing a text message."""
    notification = FeishuSchema(
        webhook_url="https://example.com/webhook", title="Test Title", body="Test Body", msg_type="text"
    )
    message = notifier._prepare_message(notification)
    assert message == {"msg_type": "text", "content": {"text": "Test Title\nTest Body"}}


def test_prepare_interactive_message(notifier):
    """Test preparing an interactive message."""
    notification = FeishuSchema(
        webhook_url="https://example.com/webhook", title="Test Title", body="Test Body", msg_type="interactive"
    )
    message = notifier._prepare_message(notification)
    assert message == {
        "msg_type": "interactive",
        "card": {
            "header": {"title": {"tag": "plain_text", "content": "Test Title"}},
            "elements": [{"tag": "div", "text": {"tag": "plain_text", "content": "Test Body"}}],
        },
    }


def test_prepare_invalid_message_type(notifier):
    """Test preparing a message with an invalid type."""
    notification = FeishuSchema(
        webhook_url="https://example.com/webhook", title="Test Title", body="Test Body", msg_type="invalid"
    )
    with pytest.raises(NotificationError, match="Invalid message type"):
        notifier._prepare_message(notification)


def test_send_success(notifier):
    """Test successful message sending."""
    notification = FeishuSchema(
        webhook_url="https://example.com/webhook", title="Test Title", body="Test Body", msg_type="text"
    )

    with patch("notify_bridge.notifiers.feishu.RequestsHelper") as mock_requests:
        mock_response = Mock()
        mock_response.raise_for_status.return_value = None
        mock_response.json.return_value = {"ok": True}
        mock_requests.return_value = Mock()
        mock_requests.return_value.post.return_value = mock_response
        notifier._requests = mock_requests.return_value

        response = notifier.send(notification)
        assert response.success
        assert response.notifier == "feishu"


def test_send_error(notifier):
    """Test message sending with error."""
    notification = FeishuSchema(
        webhook_url="https://example.com/webhook", title="Test Title", body="Test Body", msg_type="text"
    )

    with patch("notify_bridge.notifiers.feishu.RequestsHelper") as mock_requests:
        mock_response = Mock()
        mock_response.raise_for_status.side_effect = Exception("Test error")
        mock_requests.return_value = Mock()
        mock_requests.return_value.post.return_value = mock_response
        notifier._requests = mock_requests.return_value

        with pytest.raises(NotificationError, match="Failed to send Feishu notification"):
            notifier.send(notification)


def test_send_no_webhook_url():
    """Test sending without webhook URL."""
    notifier = FeishuNotifier()
    notification = FeishuSchema(title="Test Title", body="Test Body", msg_type="text", webhook_url="")
    with pytest.raises(NotificationError, match="No webhook URL provided"):
        notifier.send(notification)


@pytest.mark.asyncio
async def test_asend_success(notifier):
    """Test successful async message sending."""
    notification = FeishuSchema(
        webhook_url="https://example.com/webhook", title="Test Title", body="Test Body", msg_type="text"
    )

    with patch("notify_bridge.notifiers.feishu.RequestsHelper") as mock_requests:
        mock_response = Mock()
        mock_response.raise_for_status.return_value = None
        mock_response.json.return_value = {"ok": True}
        mock_requests.return_value = Mock()
        mock_requests.return_value.apost = AsyncMock(return_value=mock_response)
        notifier._requests = mock_requests.return_value

        response = await notifier.asend(notification)
        assert response.success
        assert response.notifier == "feishu"


@pytest.mark.asyncio
async def test_asend_error(notifier):
    """Test async message sending with error."""
    notification = FeishuSchema(
        webhook_url="https://example.com/webhook", title="Test Title", body="Test Body", msg_type="text"
    )

    with patch("notify_bridge.notifiers.feishu.RequestsHelper") as mock_requests:
        mock_response = Mock()
        mock_response.raise_for_status.side_effect = Exception("Test error")
        mock_requests.return_value = Mock()
        mock_requests.return_value.apost = AsyncMock(return_value=mock_response)
        notifier._requests = mock_requests.return_value

        with pytest.raises(NotificationError, match="Failed to send Feishu notification"):
            await notifier.asend(notification)


def test_close(notifier):
    """Test closing the notifier."""
    with patch("notify_bridge.notifiers.feishu.RequestsHelper") as mock_requests:
        mock_instance = Mock()
        mock_requests.return_value = mock_instance
        notifier._requests = mock_instance
        notifier.close()
        mock_instance.close.assert_called_once()


@pytest.mark.asyncio
async def test_aclose(notifier):
    """Test closing the notifier asynchronously."""
    with patch("notify_bridge.notifiers.feishu.RequestsHelper") as mock_requests:
        mock_instance = Mock()
        mock_instance.aclose = AsyncMock()
        mock_requests.return_value = mock_instance
        notifier._requests = mock_instance
        await notifier.aclose()
        mock_instance.aclose.assert_called_once()
