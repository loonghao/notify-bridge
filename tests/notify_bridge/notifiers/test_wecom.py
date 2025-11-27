"""Test WeCom notifier implementation."""

# Import built-in modules
from pathlib import Path

# Import third-party modules
import pytest

# Import local modules
from notify_bridge.components import MessageType
from notify_bridge.exceptions import NotificationError
from notify_bridge.notifiers.wecom import (
    Article,
    TemplateCardAction,
    TemplateCardEmphasisContent,
    TemplateCardHorizontalContentItem,
    TemplateCardImage,
    TemplateCardImageTextArea,
    TemplateCardJumpItem,
    TemplateCardMainTitle,
    TemplateCardQuoteArea,
    TemplateCardSource,
    TemplateCardVerticalContentItem,
    WeComNotifier,
    WeComSchema,
)


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
    assert MessageType.MARKDOWN_V2 in notifier.supported_types
    assert MessageType.IMAGE in notifier.supported_types
    assert MessageType.NEWS in notifier.supported_types
    assert MessageType.UPLOAD_MEDIA in notifier.supported_types


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


def test_build_markdown_v2_payload():
    """Test markdown_v2 message payload building."""
    notifier = WeComNotifier()

    # Test markdown_v2 message with underscores (should be preserved, only / is escaped)
    notification = WeComSchema(
        webhook_url="https://test.url", msg_type="markdown_v2", content="# Test Title\n\n_underscored_text_"
    )
    payload = notifier.assemble_data(notification)
    assert payload["msgtype"] == "markdown"
    # Only forward slashes should be escaped in markdown_v2
    assert payload["markdown"]["content"] == "# Test Title\n\n_underscored_text_"

    # Test markdown_v2 message with URL (forward slashes should be escaped)
    url_content = "[这是一个链接](https://work.weixin.qq.com/api/doc)"
    notification = WeComSchema(webhook_url="https://test.url", msg_type="markdown_v2", content=url_content)
    payload = notifier.assemble_data(notification)
    assert payload["msgtype"] == "markdown"
    # Forward slashes in URLs should be escaped
    assert payload["markdown"]["content"] == r"[这是一个链接](https:\/\/work.weixin.qq.com\/api\/doc)"


def test_build_image_payload():
    """Test image message payload building."""
    notifier = WeComNotifier()

    # Mock image data
    mock_base64 = "SGVsbG8gV29ybGQ="  # "Hello World" in base64
    mock_md5 = "ed076287532e86365e841e92bfc50d8c"  # MD5 of "Hello World"

    # Patch _encode_image method
    original_encode_image = notifier._encode_image
    try:
        notifier._encode_image = lambda _: (mock_base64, mock_md5)

        # Test image message
        notification = WeComSchema(webhook_url="https://test.url", msg_type="image", image_path="test.png")
        payload = notifier.assemble_data(notification)
        assert payload["msgtype"] == "image"
        assert payload["image"]["base64"] == mock_base64
        assert payload["image"]["md5"] == mock_md5
    finally:
        # Restore original method
        notifier._encode_image = original_encode_image


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


def test_build_file_payload():
    """Test file message payload building."""
    notifier = WeComNotifier()

    # Mock upload_media method
    original_upload_media = notifier._upload_media
    try:
        notifier._upload_media = lambda _, __: "test_media_id"

        # Test file message with media_path
        notification = WeComSchema(
            webhook_url="https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key=test-key",
            msg_type="file",
            media_path="test.txt",
        )
        payload = notifier.assemble_data(notification)
        assert payload["msgtype"] == "file"
        assert payload["file"]["media_id"] == "test_media_id"

        # Test file message with media_id
        notification = WeComSchema(
            webhook_url="https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key=test-key",
            msg_type="file",
            media_id="existing_media_id",
        )
        payload = notifier.assemble_data(notification)
        assert payload["msgtype"] == "file"
        assert payload["file"]["media_id"] == "existing_media_id"

        # Test file message without media_id or media_path
        notification = WeComSchema(
            webhook_url="https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key=test-key", msg_type="file"
        )
        with pytest.raises(NotificationError, match="Either media_id or media_path is required"):
            notifier.assemble_data(notification)
    finally:
        # Restore original method
        notifier._upload_media = original_upload_media


def test_build_voice_payload():
    """Test voice message payload building."""
    notifier = WeComNotifier()

    # Mock upload_media method
    original_upload_media = notifier._upload_media
    try:
        notifier._upload_media = lambda _, __: "test_media_id"

        # Test voice message with media_path
        notification = WeComSchema(
            webhook_url="https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key=test-key",
            msg_type="voice",
            media_path="test.amr",
        )
        payload = notifier.assemble_data(notification)
        assert payload["msgtype"] == "voice"
        assert payload["voice"]["media_id"] == "test_media_id"

        # Test voice message with media_id
        notification = WeComSchema(
            webhook_url="https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key=test-key",
            msg_type="voice",
            media_id="existing_media_id",
        )
        payload = notifier.assemble_data(notification)
        assert payload["msgtype"] == "voice"
        assert payload["voice"]["media_id"] == "existing_media_id"

        # Test voice message without media_id or media_path
        notification = WeComSchema(
            webhook_url="https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key=test-key", msg_type="voice"
        )
        with pytest.raises(NotificationError, match="Either media_id or media_path is required"):
            notifier.assemble_data(notification)
    finally:
        # Restore original method
        notifier._upload_media = original_upload_media


def test_upload_media_validation(tmp_path: Path):
    """Test media upload validation."""
    notifier = WeComNotifier()
    notifier._webhook_key = "test-key"  # Set webhook key for testing

    # Test file not found
    with pytest.raises(NotificationError, match="File not found"):
        notifier._upload_media("nonexistent_file.txt", "file")

    # Test file too small
    small_file = tmp_path / "small.txt"
    small_file.write_bytes(b"1234")  # 4 bytes
    with pytest.raises(NotificationError, match="File size must be greater than 5 bytes"):
        notifier._upload_media(str(small_file), "file")

    # Test file too large
    large_file = tmp_path / "large.txt"
    large_file.write_bytes(b"x" * (20 * 1024 * 1024 + 1))  # 20MB + 1 byte
    with pytest.raises(NotificationError, match="File size must not exceed 20MB"):
        notifier._upload_media(str(large_file), "file")

    # Test voice file too large
    large_voice = tmp_path / "large.amr"
    large_voice.write_bytes(b"x" * (2 * 1024 * 1024 + 1))  # 2MB + 1 byte
    with pytest.raises(NotificationError, match="Voice file size must not exceed 2MB"):
        notifier._upload_media(str(large_voice), "voice")


def test_webhook_key_extraction():
    """Test webhook key extraction from URL."""
    notifier = WeComNotifier()

    # Test simple URL
    notification = WeComSchema(
        webhook_url="https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key=test-key", msg_type="text", content="test"
    )
    notifier.validate(notification)
    assert notifier._webhook_key == "test-key"

    # Test URL with additional parameters
    notification = WeComSchema(
        webhook_url="https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key=test-key&other=param",
        msg_type="text",
        content="test",
    )
    notifier.validate(notification)
    assert notifier._webhook_key == "test-key"


def test_invalid_schema():
    """Test invalid schema handling."""
    notifier = WeComNotifier()
    with pytest.raises(NotificationError):
        notifier.assemble_data({"invalid": "data"})


def test_format_markdown():
    """Test markdown formatting."""
    notifier = WeComNotifier()

    # Test headers
    assert "# 标题1" in notifier._format_markdown("# 标题1")
    assert "## 标题2" in notifier._format_markdown("## 标题2")

    # Test lists
    assert "• 项目1" in notifier._format_markdown("- 项目1")
    assert "• 项目2" in notifier._format_markdown("* 项目2")
    assert "• 项目3" in notifier._format_markdown("+ 项目3")

    # Test ordered lists with Chinese numbers
    content = notifier._format_markdown("1. 项目1")
    assert "一、项目1" in content
    content = notifier._format_markdown("2. 项目2")
    assert "二、项目2" in content
    content = notifier._format_markdown("11. 项目11")
    assert "11." in content  # Numbers > 10 stay as is

    # Test horizontal rule
    content = notifier._format_markdown("---")
    assert "\n---\n" in content
    content = notifier._format_markdown("----")
    assert "\n---\n" in content

    # Test colored text with default colors
    colored_text = '<font color="info">提示信息</font>'
    assert colored_text in notifier._format_markdown(colored_text)

    # Test colored text with custom colors
    custom_color_map = {"success": "绿色", "error": "红色"}
    content = notifier._format_markdown(
        '<font color="success">成功</font>\n<font color="error">错误</font>', color_map=custom_color_map
    )
    assert '<font color="success">成功</font>' in content
    assert '<font color="error">错误</font>' in content

    # Test text formatting
    assert "**加粗文本**" in notifier._format_markdown("**加粗文本**")
    assert "*斜体文本*" in notifier._format_markdown("*斜体文本*")
    # Underscores should be preserved as-is, not converted to italic
    assert "_斜体文本_" in notifier._format_markdown("_斜体文本_")
    assert "`代码`" in notifier._format_markdown("`代码`")
    assert "> 引用" in notifier._format_markdown("> 引用")
    assert "[链接](https://example.com)" in notifier._format_markdown("[链接](https://example.com)")

    # Test complex markdown
    complex_md = """# 标题1
## 标题2

- 无序列表1
- 无序列表2

1. 有序列表1
2. 有序列表2

---

**加粗文本**
*斜体文本*
`代码示例`
> 引用文本

[链接](https://example.com)

<font color="info">提示信息</font>
<font color="warning">警告信息</font>"""

    formatted = notifier._format_markdown(complex_md)
    assert "# 标题1" in formatted
    assert "## 标题2" in formatted
    assert "• 无序列表1" in formatted
    assert "• 无序列表2" in formatted
    assert "一、有序列表1" in formatted
    assert "二、有序列表2" in formatted
    assert "\n---\n" in formatted
    assert "**加粗文本**" in formatted
    assert "*斜体文本*" in formatted
    assert "`代码示例`" in formatted
    assert "> 引用文本" in formatted
    assert "[链接](https://example.com)" in formatted
    assert '<font color="info">提示信息</font>' in formatted
    assert '<font color="warning">警告信息</font>' in formatted


def test_markdown_payload_with_custom_colors():
    """Test markdown payload with custom colors."""
    notifier = WeComNotifier()

    # Test with default colors
    data = WeComSchema(
        base_url="https://example.com", message='# 标题\n<font color="info">提示</font>', msg_type="markdown"
    )
    payload = notifier.assemble_data(data)
    assert '<font color="info">提示</font>' in payload["markdown"]["content"]

    # Test with custom colors
    data = WeComSchema(
        base_url="https://example.com",
        message='# 标题\n<font color="success">成功</font>',
        msg_type="markdown",
        color_map={"success": "绿色"},
    )
    payload = notifier.assemble_data(data)
    assert '<font color="success">成功</font>' in payload["markdown"]["content"]


def test_markdown_preserves_underscores():
    """Test that markdown formatting preserves underscores."""
    notifier = WeComNotifier()

    # Test that underscores are preserved in markdown mode
    content_with_underscores = "This is _underscored_text_ and __double_underscored__"
    formatted = notifier._format_markdown(content_with_underscores)
    # Underscores should be preserved as-is
    assert "_underscored_text_" in formatted
    assert "__double_underscored__" in formatted


def test_markdown_v2_preserves_all_formatting():
    """Test that markdown_v2 escapes forward slashes only."""
    notifier = WeComNotifier()

    # Test various markdown elements - only forward slashes should be escaped
    test_cases = [
        ("# Header with _underscores_", "# Header with _underscores_"),
        ("**bold** and *italic* and _underscored_", "**bold** and *italic* and _underscored_"),
        ("- list with _underscores_", "- list with _underscores_"),
        ("`code_with_underscores`", "`code_with_underscores`"),
        (
            "[link_text](https://example.com/path_with_underscores)",
            r"[link_text](https:\/\/example.com\/path_with_underscores)",
        ),
        ("---", "---"),
        ("> quote with _underscores_", "> quote with _underscores_"),
    ]

    for input_content, expected_content in test_cases:
        notification = WeComSchema(webhook_url="https://test.url", msg_type="markdown_v2", content=input_content)
        payload = notifier.assemble_data(notification)
        # Only forward slashes should be escaped
        assert payload["markdown"]["content"] == expected_content
        # msgtype should be "markdown_v2" for markdown_v2 messages
        assert payload["msgtype"] == "markdown_v2"


def test_build_upload_media_payload():
    """Test building upload_media payload.

    Note: UPLOAD_MEDIA is not an official WeCom webhook message type.
    It's exposed for convenience to access the upload_media API.
    """
    notifier = WeComNotifier()

    # Mock upload_media method
    original_upload_media = notifier._upload_media
    try:
        notifier._upload_media = lambda file_path, media_type: f"test_media_id_{media_type}"

        # Test upload_media with default type (file) via send()
        response = notifier.send(
            {
                "webhook_url": "https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key=test",
                "msg_type": "upload_media",
                "media_path": "test.pdf",
            }
        )
        assert response.success is True
        assert response.data["media_id"] == "test_media_id_file"
        assert response.data["type"] == "file"
        assert "msgtype" not in response.data  # upload_media doesn't use msgtype

        # Test upload_media with voice type via send()
        response = notifier.send(
            {
                "webhook_url": "https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key=test",
                "msg_type": "upload_media",
                "media_path": "test.amr",
                "upload_media_type": "voice",
            }
        )
        assert response.success is True
        assert response.data["media_id"] == "test_media_id_voice"
        assert response.data["type"] == "voice"

        # Test upload_media without media_path should raise error
        with pytest.raises(NotificationError, match="media_path is required"):
            notifier.send(
                {
                    "webhook_url": "https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key=test",
                    "msg_type": "upload_media",
                }
            )

        # Test upload_media with invalid type should raise error
        with pytest.raises(NotificationError, match="Invalid upload_media_type"):
            notifier.send(
                {
                    "webhook_url": "https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key=test",
                    "msg_type": "upload_media",
                    "media_path": "test.pdf",
                    "upload_media_type": "invalid",
                }
            )

        # Test that assemble_data raises error for UPLOAD_MEDIA
        with pytest.raises(NotificationError, match="UPLOAD_MEDIA should be handled via send"):
            notification = WeComSchema(
                webhook_url="https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key=test",
                msg_type="upload_media",
                media_path="test.pdf",
            )
            notifier.assemble_data(notification)

    finally:
        notifier._upload_media = original_upload_media


def test_template_card_schemas():
    """Test template card schema classes."""
    # Test TemplateCardSource
    source = TemplateCardSource(
        icon_url="https://example.com/icon.png",
        desc="Test Source",
        desc_color=1,
    )
    assert source.icon_url == "https://example.com/icon.png"
    assert source.desc == "Test Source"
    assert source.desc_color == 1

    # Test TemplateCardMainTitle
    main_title = TemplateCardMainTitle(
        title="Main Title",
        desc="Main Description",
    )
    assert main_title.title == "Main Title"
    assert main_title.desc == "Main Description"

    # Test TemplateCardEmphasisContent
    emphasis = TemplateCardEmphasisContent(
        title="100",
        desc="Data Meaning",
    )
    assert emphasis.title == "100"
    assert emphasis.desc == "Data Meaning"

    # Test TemplateCardQuoteArea
    quote = TemplateCardQuoteArea(
        type=1,
        url="https://example.com",
        title="Quote Title",
        quote_text="Quote Text",
    )
    assert quote.type == 1
    assert quote.url == "https://example.com"
    assert quote.title == "Quote Title"
    assert quote.quote_text == "Quote Text"

    # Test TemplateCardHorizontalContentItem
    horizontal_item = TemplateCardHorizontalContentItem(
        keyname="Inviter",
        value="Zhang San",
    )
    assert horizontal_item.keyname == "Inviter"
    assert horizontal_item.value == "Zhang San"

    # Test TemplateCardJumpItem
    jump_item = TemplateCardJumpItem(
        type=1,
        url="https://example.com",
        title="Jump Title",
    )
    assert jump_item.type == 1
    assert jump_item.url == "https://example.com"
    assert jump_item.title == "Jump Title"

    # Test TemplateCardAction
    action = TemplateCardAction(
        type=1,
        url="https://example.com",
    )
    assert action.type == 1
    assert action.url == "https://example.com"


def test_build_template_card_payload_minimal():
    """Test template card message payload building with minimal fields."""
    notifier = WeComNotifier()

    # Test minimal template card
    notification = WeComSchema(
        webhook_url="https://test.url",
        msg_type="template_card",
        template_card_type="text_notice",
    )
    payload = notifier.assemble_data(notification)
    assert payload["msgtype"] == "template_card"
    assert payload["template_card"]["card_type"] == "text_notice"


def test_build_template_card_payload_full():
    """Test template card message payload building with all fields."""
    notifier = WeComNotifier()

    # Test full template card with all fields
    notification = WeComSchema(
        webhook_url="https://test.url",
        msg_type="template_card",
        template_card_type="text_notice",
        template_card_source={
            "icon_url": "https://wework.qpic.cn/wwpic/252813_jOfDHtcISzuodLa_1629280209/0",
            "desc": "Enterprise WeChat",
            "desc_color": 0,
        },
        template_card_main_title={
            "title": "Welcome to Enterprise WeChat",
            "desc": "Your friend is inviting you to join Enterprise WeChat",
        },
        template_card_emphasis_content={
            "title": "100",
            "desc": "Data Meaning",
        },
        template_card_quote_area={
            "type": 1,
            "url": "https://work.weixin.qq.com/?from=openApi",
            "title": "Quote Title",
            "quote_text": "Jack: Enterprise WeChat is really good~\nBalian: Super good software!",
        },
        template_card_sub_title_text="Download Enterprise WeChat to grab red packets!",
        template_card_horizontal_content_list=[
            {
                "keyname": "Inviter",
                "value": "Zhang San",
            },
            {
                "keyname": "Official Website",
                "value": "Click to visit",
                "type": 1,
                "url": "https://work.weixin.qq.com/?from=openApi",
            },
        ],
        template_card_jump_list=[
            {
                "type": 1,
                "url": "https://work.weixin.qq.com/?from=openApi",
                "title": "Enterprise WeChat Official Website",
            },
        ],
        template_card_card_action={
            "type": 1,
            "url": "https://work.weixin.qq.com/?from=openApi",
        },
    )
    payload = notifier.assemble_data(notification)

    assert payload["msgtype"] == "template_card"
    assert payload["template_card"]["card_type"] == "text_notice"
    assert (
        payload["template_card"]["source"]["icon_url"]
        == "https://wework.qpic.cn/wwpic/252813_jOfDHtcISzuodLa_1629280209/0"
    )
    assert payload["template_card"]["source"]["desc"] == "Enterprise WeChat"
    assert payload["template_card"]["source"]["desc_color"] == 0
    assert payload["template_card"]["main_title"]["title"] == "Welcome to Enterprise WeChat"
    assert payload["template_card"]["main_title"]["desc"] == "Your friend is inviting you to join Enterprise WeChat"
    assert payload["template_card"]["emphasis_content"]["title"] == "100"
    assert payload["template_card"]["emphasis_content"]["desc"] == "Data Meaning"
    assert payload["template_card"]["quote_area"]["type"] == 1
    assert payload["template_card"]["quote_area"]["url"] == "https://work.weixin.qq.com/?from=openApi"
    assert payload["template_card"]["sub_title_text"] == "Download Enterprise WeChat to grab red packets!"
    assert len(payload["template_card"]["horizontal_content_list"]) == 2
    assert payload["template_card"]["horizontal_content_list"][0]["keyname"] == "Inviter"
    assert payload["template_card"]["horizontal_content_list"][0]["value"] == "Zhang San"
    assert payload["template_card"]["horizontal_content_list"][1]["type"] == 1
    assert len(payload["template_card"]["jump_list"]) == 1
    assert payload["template_card"]["jump_list"][0]["title"] == "Enterprise WeChat Official Website"
    assert payload["template_card"]["card_action"]["type"] == 1
    assert payload["template_card"]["card_action"]["url"] == "https://work.weixin.qq.com/?from=openApi"


def test_build_template_card_payload_with_pydantic_models():
    """Test template card message payload building with Pydantic models."""
    notifier = WeComNotifier()

    # Test template card with Pydantic model instances
    notification = WeComSchema(
        webhook_url="https://test.url",
        msg_type="template_card",
        template_card_type="text_notice",
        template_card_source=TemplateCardSource(
            icon_url="https://example.com/icon.png",
            desc="Test Source",
            desc_color=1,
        ),
        template_card_main_title=TemplateCardMainTitle(
            title="Test Title",
            desc="Test Description",
        ),
        template_card_emphasis_content=TemplateCardEmphasisContent(
            title="50",
            desc="Test Data",
        ),
        template_card_horizontal_content_list=[
            TemplateCardHorizontalContentItem(
                keyname="Key1",
                value="Value1",
            ),
        ],
        template_card_jump_list=[
            TemplateCardJumpItem(
                type=1,
                url="https://example.com",
                title="Jump Link",
            ),
        ],
        template_card_card_action=TemplateCardAction(
            type=1,
            url="https://example.com/action",
        ),
    )
    payload = notifier.assemble_data(notification)

    assert payload["msgtype"] == "template_card"
    assert payload["template_card"]["card_type"] == "text_notice"
    assert payload["template_card"]["source"]["icon_url"] == "https://example.com/icon.png"
    assert payload["template_card"]["main_title"]["title"] == "Test Title"
    assert payload["template_card"]["emphasis_content"]["title"] == "50"
    assert len(payload["template_card"]["horizontal_content_list"]) == 1
    assert payload["template_card"]["horizontal_content_list"][0]["keyname"] == "Key1"
    assert len(payload["template_card"]["jump_list"]) == 1
    assert payload["template_card"]["card_action"]["url"] == "https://example.com/action"


def test_wecom_notifier_supports_template_card():
    """Test that WeComNotifier supports TEMPLATE_CARD message type."""
    notifier = WeComNotifier()
    assert MessageType.TEMPLATE_CARD in notifier.supported_types


def test_template_card_news_notice_schemas():
    """Test template card news_notice schema classes."""
    # Test TemplateCardImage
    card_image = TemplateCardImage(
        url="https://example.com/image.png",
        aspect_ratio=2.25,
    )
    assert card_image.url == "https://example.com/image.png"
    assert card_image.aspect_ratio == 2.25

    # Test TemplateCardImageTextArea
    image_text_area = TemplateCardImageTextArea(
        type=1,
        url="https://example.com",
        title="Image Text Title",
        desc="Image Text Description",
        image_url="https://example.com/image.png",
    )
    assert image_text_area.type == 1
    assert image_text_area.url == "https://example.com"
    assert image_text_area.title == "Image Text Title"
    assert image_text_area.desc == "Image Text Description"
    assert image_text_area.image_url == "https://example.com/image.png"

    # Test TemplateCardVerticalContentItem
    vertical_item = TemplateCardVerticalContentItem(
        title="Vertical Title",
        desc="Vertical Description",
    )
    assert vertical_item.title == "Vertical Title"
    assert vertical_item.desc == "Vertical Description"


def test_build_template_card_news_notice_payload():
    """Test template card news_notice message payload building."""
    notifier = WeComNotifier()

    # Test news_notice template card with all fields
    notification = WeComSchema(
        webhook_url="https://test.url",
        msg_type="template_card",
        template_card_type="news_notice",
        template_card_source={
            "icon_url": "https://wework.qpic.cn/wwpic/252813_jOfDHtcISzuodLa_1629280209/0",
            "desc": "Enterprise WeChat",
            "desc_color": 0,
        },
        template_card_main_title={
            "title": "Welcome to Enterprise WeChat",
            "desc": "Your friend is inviting you to join Enterprise WeChat",
        },
        template_card_image={
            "url": "https://wework.qpic.cn/wwpic/354393_4zpkKXd7SrGMvfg_1629280616/0",
            "aspect_ratio": 2.25,
        },
        template_card_image_text_area={
            "type": 1,
            "url": "https://work.weixin.qq.com",
            "title": "Welcome to Enterprise WeChat",
            "desc": "Your friend is inviting you to join Enterprise WeChat",
            "image_url": "https://wework.qpic.cn/wwpic/354393_4zpkKXd7SrGMvfg_1629280616/0",
        },
        template_card_quote_area={
            "type": 1,
            "url": "https://work.weixin.qq.com/?from=openApi",
            "title": "Quote Title",
            "quote_text": "Jack: Enterprise WeChat is really good~\nBalian: Super good software!",
        },
        template_card_vertical_content_list=[
            {
                "title": "Surprise red packets waiting for you",
                "desc": "Download Enterprise WeChat to grab red packets!",
            },
        ],
        template_card_horizontal_content_list=[
            {
                "keyname": "Inviter",
                "value": "Zhang San",
            },
            {
                "keyname": "Official Website",
                "value": "Click to visit",
                "type": 1,
                "url": "https://work.weixin.qq.com/?from=openApi",
            },
        ],
        template_card_jump_list=[
            {
                "type": 1,
                "url": "https://work.weixin.qq.com/?from=openApi",
                "title": "Enterprise WeChat Official Website",
            },
        ],
        template_card_card_action={
            "type": 1,
            "url": "https://work.weixin.qq.com/?from=openApi",
        },
    )
    payload = notifier.assemble_data(notification)

    assert payload["msgtype"] == "template_card"
    assert payload["template_card"]["card_type"] == "news_notice"
    assert payload["template_card"]["source"]["desc"] == "Enterprise WeChat"
    assert payload["template_card"]["main_title"]["title"] == "Welcome to Enterprise WeChat"
    assert (
        payload["template_card"]["card_image"]["url"]
        == "https://wework.qpic.cn/wwpic/354393_4zpkKXd7SrGMvfg_1629280616/0"
    )
    assert payload["template_card"]["card_image"]["aspect_ratio"] == 2.25
    assert payload["template_card"]["image_text_area"]["type"] == 1
    assert payload["template_card"]["image_text_area"]["title"] == "Welcome to Enterprise WeChat"
    assert (
        payload["template_card"]["image_text_area"]["image_url"]
        == "https://wework.qpic.cn/wwpic/354393_4zpkKXd7SrGMvfg_1629280616/0"
    )
    assert len(payload["template_card"]["vertical_content_list"]) == 1
    assert payload["template_card"]["vertical_content_list"][0]["title"] == "Surprise red packets waiting for you"
    assert len(payload["template_card"]["horizontal_content_list"]) == 2
    assert len(payload["template_card"]["jump_list"]) == 1


def test_build_template_card_news_notice_with_pydantic_models():
    """Test template card news_notice message payload building with Pydantic models."""
    notifier = WeComNotifier()

    # Test news_notice template card with Pydantic model instances
    notification = WeComSchema(
        webhook_url="https://test.url",
        msg_type="template_card",
        template_card_type="news_notice",
        template_card_source=TemplateCardSource(
            icon_url="https://example.com/icon.png",
            desc="Test Source",
            desc_color=1,
        ),
        template_card_main_title=TemplateCardMainTitle(
            title="Test Title",
            desc="Test Description",
        ),
        template_card_image=TemplateCardImage(
            url="https://example.com/image.png",
            aspect_ratio=1.5,
        ),
        template_card_image_text_area=TemplateCardImageTextArea(
            type=1,
            url="https://example.com",
            title="Image Text Title",
            desc="Image Text Description",
            image_url="https://example.com/image.png",
        ),
        template_card_vertical_content_list=[
            TemplateCardVerticalContentItem(
                title="Vertical Title 1",
                desc="Vertical Description 1",
            ),
            TemplateCardVerticalContentItem(
                title="Vertical Title 2",
                desc="Vertical Description 2",
            ),
        ],
        template_card_horizontal_content_list=[
            TemplateCardHorizontalContentItem(
                keyname="Key1",
                value="Value1",
            ),
        ],
    )
    payload = notifier.assemble_data(notification)

    assert payload["msgtype"] == "template_card"
    assert payload["template_card"]["card_type"] == "news_notice"
    assert payload["template_card"]["source"]["icon_url"] == "https://example.com/icon.png"
    assert payload["template_card"]["main_title"]["title"] == "Test Title"
    assert payload["template_card"]["card_image"]["url"] == "https://example.com/image.png"
    assert payload["template_card"]["card_image"]["aspect_ratio"] == 1.5
    assert payload["template_card"]["image_text_area"]["title"] == "Image Text Title"
    assert len(payload["template_card"]["vertical_content_list"]) == 2
    assert payload["template_card"]["vertical_content_list"][0]["title"] == "Vertical Title 1"
    assert payload["template_card"]["vertical_content_list"][1]["title"] == "Vertical Title 2"
    assert len(payload["template_card"]["horizontal_content_list"]) == 1
