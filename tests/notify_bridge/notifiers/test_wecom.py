"""Tests for WeCom notifier."""

# Import built-in modules
import os
import shutil
import tempfile

import pytest
import pytest_asyncio
from httpx import Response

# Import third-party modules
from PIL import Image

# Import local modules
from notify_bridge.exceptions import NotificationError
from notify_bridge.notifiers.wecom import WeComNotifier, WeComSchema


@pytest_asyncio.fixture
async def notifier():
    """Create a WeComNotifier instance."""
    notifier = WeComNotifier()
    yield notifier
    await notifier.aclose()


@pytest.fixture
def test_image():
    """Create a test image file."""
    with tempfile.NamedTemporaryFile(suffix=".jpg", delete=False) as temp_file:
        # 创建一个简单的测试图片
        img = Image.new("RGB", (800, 600), color="white")
        img.save(temp_file.name, "JPEG", quality=95)
        yield temp_file.name
    # 清理临时文件
    if os.path.exists(temp_file.name):
        os.unlink(temp_file.name)


@pytest.fixture
def test_file():
    """Create a test text file."""
    with tempfile.NamedTemporaryFile(suffix=".txt", delete=False) as temp_file:
        temp_file.write(b"Test content")
        temp_file.flush()
        temp_file.close()
        yield temp_file.name
    # 清理临时文件
    if os.path.exists(temp_file.name):
        os.unlink(temp_file.name)


@pytest.mark.asyncio
async def test_wecom_schema_validation():
    """Test WeComSchema validation."""
    # Test valid schema
    valid_data = {
        "webhook_url": "https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key=test",
        "title": "Test Title",
        "body": "Test Body",
        "msg_type": "text",
    }
    schema = WeComSchema(**valid_data)
    assert schema.webhook_url == valid_data["webhook_url"]
    assert schema.title == valid_data["title"]
    assert schema.body == valid_data["body"]
    assert schema.msg_type == valid_data["msg_type"]

    # Test invalid message type
    with pytest.raises(NotificationError):
        invalid_data = valid_data.copy()
        invalid_data["msg_type"] = "invalid"
        schema = WeComSchema(**invalid_data)
        notifier = WeComNotifier()
        await notifier.asend(schema)


@pytest.mark.asyncio
async def test_wecom_text_message(notifier, mocker):
    """Test sending text messages."""
    mock_response = mocker.Mock(spec=Response)
    mock_response.json.return_value = {"errcode": 0, "errmsg": "ok"}
    mocker.patch("notify_bridge.utils.requests.RequestsHelper.apost", return_value=mock_response)

    notification = WeComSchema(
        webhook_url="https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key=test",
        title="Test Title",
        body="Test Body",
        msg_type="text",
        mentioned_list=["user1", "user2"],
        mentioned_mobile_list=["13800138000"],
    )

    response = await notifier.send(notification)
    assert response.success
    assert response.notifier == "wecom"

    # Verify the payload
    mock_post = notifier._requests.apost
    args, kwargs = mock_post.call_args
    payload = kwargs["json"]
    assert payload["msgtype"] == "text"
    assert "Test Title" in payload["text"]["content"]
    assert "Test Body" in payload["text"]["content"]
    assert payload["text"]["mentioned_list"] == ["user1", "user2"]
    assert payload["text"]["mentioned_mobile_list"] == ["13800138000"]


@pytest.mark.asyncio
async def test_wecom_markdown_message(notifier, mocker):
    """Test sending markdown messages."""
    mock_response = mocker.Mock(spec=Response)
    mock_response.json.return_value = {"errcode": 0, "errmsg": "ok"}
    mocker.patch("notify_bridge.utils.requests.RequestsHelper.apost", return_value=mock_response)

    notification = WeComSchema(
        webhook_url="https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key=test",
        title="Test Title",
        body="**Bold Text**\n> Quote",
        msg_type="markdown",
    )

    response = await notifier.send(notification)
    assert response.success
    assert response.notifier == "wecom"

    # Verify the payload
    mock_post = notifier._requests.apost
    args, kwargs = mock_post.call_args
    payload = kwargs["json"]
    assert payload["msgtype"] == "markdown"
    assert "# Test Title" in payload["markdown"]["content"]
    assert "**Bold Text**" in payload["markdown"]["content"]
    assert "> Quote" in payload["markdown"]["content"]


@pytest.mark.asyncio
async def test_wecom_news_message(notifier, mocker):
    """Test sending news messages."""
    mock_response = mocker.Mock(spec=Response)
    mock_response.json.return_value = {"errcode": 0, "errmsg": "ok"}
    mocker.patch("notify_bridge.utils.requests.RequestsHelper.apost", return_value=mock_response)

    articles = [
        {
            "title": "Article Title",
            "description": "Article Description",
            "url": "https://example.com",
            "picurl": "https://example.com/image.jpg",
        }
    ]

    notification = WeComSchema(
        webhook_url="https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key=test",
        title="Test Title",
        body="Test Body",
        msg_type="news",
        articles=articles,
    )

    response = await notifier.send(notification)
    assert response.success
    assert response.notifier == "wecom"

    # Verify the payload
    mock_post = notifier._requests.apost
    args, kwargs = mock_post.call_args
    payload = kwargs["json"]
    assert payload["msgtype"] == "news"
    assert payload["news"]["articles"] == articles


@pytest.mark.asyncio
async def test_wecom_news_message_with_local_image(notifier, mocker, test_image):
    """Test sending news messages with local images."""
    # Mock the upload response
    mock_upload_response = mocker.Mock(spec=Response)
    mock_upload_response.json.return_value = {"errcode": 0, "errmsg": "ok", "media_id": "test_media_id"}

    # Mock the send response
    mock_send_response = mocker.Mock(spec=Response)
    mock_send_response.json.return_value = {"errcode": 0, "errmsg": "ok"}

    # Setup the mock to return different responses
    mock_post = mocker.patch("notify_bridge.utils.requests.RequestsHelper.apost")
    mock_post.side_effect = [mock_upload_response, mock_send_response]

    articles = [
        {
            "title": "Article Title",
            "description": "Article Description",
            "url": "https://example.com",
            "picurl": test_image,
        }
    ]

    notification = WeComSchema(
        webhook_url="https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key=test",
        title="Test Title",
        body="Test Body",
        msg_type="news",
        articles=articles,
    )

    response = await notifier.send(notification)
    assert response.success
    assert response.notifier == "wecom"

    # Verify the final payload
    args, kwargs = mock_post.call_args_list[-1]
    payload = kwargs["json"]
    assert payload["msgtype"] == "news"
    assert payload["news"]["articles"][0]["picurl"] == "https://wework.qpic.cn/wwpic/test_media_id/0"


@pytest.mark.asyncio
async def test_wecom_image_message(notifier, mocker, test_image):
    """Test sending image messages."""
    # Mock the response
    mock_response = mocker.Mock(spec=Response)
    mock_response.json.return_value = {"errcode": 0, "errmsg": "ok"}
    mocker.patch("notify_bridge.utils.requests.RequestsHelper.apost", return_value=mock_response)

    notification = WeComSchema(
        webhook_url="https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key=test",
        title="Test Title",
        body="Test Body",
        msg_type="image",
        file_path=test_image,
    )

    response = await notifier.send(notification)
    assert response.success
    assert response.notifier == "wecom"

    # Verify the payload
    mock_post = notifier._requests.apost
    args, kwargs = mock_post.call_args
    payload = kwargs["json"]
    assert payload["msgtype"] == "image"
    assert "base64" in payload["image"]
    assert "md5" in payload["image"]


@pytest.mark.asyncio
async def test_wecom_file_message(notifier, mocker, test_file):
    """Test sending file messages."""
    # Mock the upload response
    mock_upload_response = mocker.Mock(spec=Response)
    mock_upload_response.json.return_value = {"errcode": 0, "errmsg": "ok", "media_id": "test_media_id"}

    # Mock the send response
    mock_send_response = mocker.Mock(spec=Response)
    mock_send_response.json.return_value = {"errcode": 0, "errmsg": "ok"}

    # Setup the mock to return different responses
    mock_post = mocker.patch("notify_bridge.utils.requests.RequestsHelper.apost")
    mock_post.side_effect = [mock_upload_response, mock_send_response]

    notification = WeComSchema(
        webhook_url="https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key=test",
        title="Test Title",
        body="Test Body",
        msg_type="file",
        file_path=test_file,
    )

    response = await notifier.send(notification)
    assert response.success
    assert response.notifier == "wecom"

    # Verify the final payload
    args, kwargs = mock_post.call_args_list[-1]
    payload = kwargs["json"]
    assert payload["msgtype"] == "file"
    assert payload["file"]["media_id"] == "test_media_id"


@pytest.mark.asyncio
async def test_wecom_file_not_found(notifier):
    """Test handling of non-existent files."""
    notification = WeComSchema(
        webhook_url="https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key=test",
        title="Test Title",
        body="Test Body",
        msg_type="file",
        file_path="nonexistent.txt",
    )

    with pytest.raises(NotificationError) as exc_info:
        await notifier.send(notification)
    assert "File not found" in str(exc_info.value)


@pytest.mark.asyncio
async def test_wecom_invalid_file_type(notifier, test_file):
    """Test handling of invalid file types."""
    # 创建一个新的临时目录
    with tempfile.TemporaryDirectory() as temp_dir:
        # 复制测试文件到临时目录
        invalid_file = os.path.join(temp_dir, "test.xyz")
        shutil.copy2(test_file, invalid_file)

        notification = WeComSchema(
            webhook_url="https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key=test",
            title="Test Title",
            body="Test Body",
            msg_type="file",
            file_path=invalid_file,
        )

        with pytest.raises(NotificationError) as exc_info:
            await notifier.send(notification)
        assert "Unable to determine file type" in str(exc_info.value)


@pytest.mark.asyncio
async def test_wecom_api_error(notifier, mocker):
    """Test handling of API errors."""
    mock_response = mocker.Mock(spec=Response)
    mock_response.json.return_value = {"errcode": 93000, "errmsg": "Invalid webhook url"}
    mocker.patch("notify_bridge.utils.requests.RequestsHelper.apost", return_value=mock_response)

    notification = WeComSchema(
        webhook_url="https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key=invalid",
        title="Test Title",
        body="Test Body",
        msg_type="text",
    )

    with pytest.raises(NotificationError) as exc_info:
        await notifier.send(notification)
    assert "Invalid webhook url" in str(exc_info.value)


@pytest.mark.asyncio
async def test_wecom_async_send(notifier, mocker):
    """Test sending notifications asynchronously."""
    mock_response = mocker.Mock(spec=Response)
    mock_response.json.return_value = {"errcode": 0, "errmsg": "ok"}
    mocker.patch("notify_bridge.utils.requests.RequestsHelper.apost", return_value=mock_response)

    notification = WeComSchema(
        webhook_url="https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key=test",
        title="Test Title",
        body="Test Body",
        msg_type="text",
    )

    response = await notifier.send(notification)
    assert response.success
    assert response.notifier == "wecom"

    # Verify the payload
    mock_post = notifier._requests.apost
    args, kwargs = mock_post.call_args
    payload = kwargs["json"]
    assert payload["msgtype"] == "text"
    assert "Test Title" in payload["text"]["content"]
    assert "Test Body" in payload["text"]["content"]


@pytest.mark.asyncio
async def test_wecom_async_send_with_file(notifier, mocker, test_file):
    """Test sending file notifications asynchronously."""
    # Mock the upload response
    mock_upload_response = mocker.Mock(spec=Response)
    mock_upload_response.json.return_value = {"errcode": 0, "errmsg": "ok", "media_id": "test_media_id"}

    # Mock the send response
    mock_send_response = mocker.Mock(spec=Response)
    mock_send_response.json.return_value = {"errcode": 0, "errmsg": "ok"}

    # Setup the mock to return different responses
    mock_post = mocker.patch("notify_bridge.utils.requests.RequestsHelper.apost")
    mock_post.side_effect = [mock_upload_response, mock_send_response]

    notification = WeComSchema(
        webhook_url="https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key=test",
        title="Test Title",
        body="Test Body",
        msg_type="file",
        file_path=test_file,
    )

    response = await notifier.send(notification)
    assert response.success
    assert response.notifier == "wecom"

    # Verify the final payload
    args, kwargs = mock_post.call_args_list[-1]
    payload = kwargs["json"]
    assert payload["msgtype"] == "file"
    assert payload["file"]["media_id"] == "test_media_id"
