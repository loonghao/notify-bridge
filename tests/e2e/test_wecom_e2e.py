"""End-to-end tests for WeCom notifier.

These tests require a valid WeCom webhook URL to run.
Set the WECOM_WEBHOOK_URL environment variable before running.

Usage:
    WECOM_WEBHOOK_URL="https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key=xxx" \
    pytest tests/e2e/test_wecom_e2e.py -v
"""

# Import built-in modules
import os
from datetime import datetime

# Import third-party modules
import pytest

# Import local modules
from notify_bridge import NotifyBridge
from notify_bridge.notifiers.wecom import WeComNotifier, WeComSchema


# Skip all tests if WECOM_WEBHOOK_URL is not set
pytestmark = pytest.mark.skipif(
    not os.getenv("WECOM_WEBHOOK_URL"),
    reason="WECOM_WEBHOOK_URL environment variable not set",
)


@pytest.fixture
def webhook_url() -> str:
    """Get webhook URL from environment."""
    return os.getenv("WECOM_WEBHOOK_URL", "")


@pytest.fixture
def bridge() -> NotifyBridge:
    """Create NotifyBridge instance."""
    return NotifyBridge()


@pytest.fixture
def notifier() -> WeComNotifier:
    """Create WeComNotifier instance."""
    return WeComNotifier()


class TestWeComTextMessage:
    """Test WeCom text message sending."""

    def test_send_text_message(self, bridge: NotifyBridge, webhook_url: str) -> None:
        """Test sending a simple text message."""
        response = bridge.send(
            "wecom",
            webhook_url=webhook_url,
            message=f"[E2E Test] Text message at {datetime.now().isoformat()}",
            msg_type="text",
        )
        assert response.success is True
        assert response.data.get("errcode") == 0

    def test_send_text_message_with_mentions(self, bridge: NotifyBridge, webhook_url: str) -> None:
        """Test sending a text message with mentions."""
        response = bridge.send(
            "wecom",
            webhook_url=webhook_url,
            message=f"[E2E Test] Text with mentions at {datetime.now().isoformat()}",
            msg_type="text",
            mentioned_list=["@all"],
        )
        assert response.success is True
        assert response.data.get("errcode") == 0

    @pytest.mark.asyncio
    async def test_send_text_message_async(self, bridge: NotifyBridge, webhook_url: str) -> None:
        """Test sending a text message asynchronously."""
        response = await bridge.send_async(
            "wecom",
            webhook_url=webhook_url,
            message=f"[E2E Test] Async text message at {datetime.now().isoformat()}",
            msg_type="text",
        )
        assert response.success is True
        assert response.data.get("errcode") == 0


class TestWeComMarkdownMessage:
    """Test WeCom markdown message sending."""

    def test_send_markdown_message(self, bridge: NotifyBridge, webhook_url: str) -> None:
        """Test sending a markdown message."""
        content = f"""# E2E Test - Markdown Message

**Time**: {datetime.now().isoformat()}

## Features
- Bold text: **bold**
- Italic text: *italic*
- Link: [GitHub](https://github.com)
- Quote: > This is a quote

## Code
`inline code`

<font color="info">Info text</font>
<font color="warning">Warning text</font>
<font color="comment">Comment text</font>
"""
        response = bridge.send(
            "wecom",
            webhook_url=webhook_url,
            message=content,
            msg_type="markdown",
        )
        assert response.success is True
        assert response.data.get("errcode") == 0

    def test_send_markdown_message_with_mentions(self, bridge: NotifyBridge, webhook_url: str) -> None:
        """Test sending a markdown message with mentions."""
        content = f"""# E2E Test - Markdown with Mentions

**Time**: {datetime.now().isoformat()}

This message mentions @all users.
"""
        response = bridge.send(
            "wecom",
            webhook_url=webhook_url,
            message=content,
            msg_type="markdown",
            mentioned_list=["@all"],
        )
        assert response.success is True
        assert response.data.get("errcode") == 0

    @pytest.mark.asyncio
    async def test_send_markdown_message_async(self, bridge: NotifyBridge, webhook_url: str) -> None:
        """Test sending a markdown message asynchronously."""
        content = f"""# E2E Test - Async Markdown

**Time**: {datetime.now().isoformat()}

This is an async markdown message.
"""
        response = await bridge.send_async(
            "wecom",
            webhook_url=webhook_url,
            message=content,
            msg_type="markdown",
        )
        assert response.success is True
        assert response.data.get("errcode") == 0


class TestWeComMarkdownV2Message:
    """Test WeCom markdown_v2 message sending.

    markdown_v2 is an enhanced markdown format that supports more features
    like underscores without escaping.
    """

    def test_send_markdown_v2_message(self, bridge: NotifyBridge, webhook_url: str) -> None:
        """Test sending a markdown_v2 message."""
        content = f"""# E2E Test - Markdown V2 Message

**Time**: {datetime.now().isoformat()}

## Enhanced Features
- _Underscored text_ (preserved in markdown_v2)
- **Bold text**
- *Italic text*
- [Link with slashes](https://github.com/loonghao/notify-bridge)

## Code
`code_with_underscores`

This tests the markdown_v2 format which properly handles underscores.
"""
        response = bridge.send(
            "wecom",
            webhook_url=webhook_url,
            message=content,
            msg_type="markdown_v2",
        )
        assert response.success is True
        assert response.data.get("errcode") == 0

    def test_send_markdown_v2_with_url(self, bridge: NotifyBridge, webhook_url: str) -> None:
        """Test sending markdown_v2 with URLs (forward slashes should be escaped)."""
        content = f"""# E2E Test - Markdown V2 with URLs

**Time**: {datetime.now().isoformat()}

Links:
- [WeCom API](https://work.weixin.qq.com/api/doc)
- [GitHub](https://github.com/loonghao/notify-bridge)
- [Python](https://www.python.org/)
"""
        response = bridge.send(
            "wecom",
            webhook_url=webhook_url,
            message=content,
            msg_type="markdown_v2",
        )
        assert response.success is True
        assert response.data.get("errcode") == 0

    def test_send_markdown_v2_with_mentions(self, bridge: NotifyBridge, webhook_url: str) -> None:
        """Test sending markdown_v2 with mentions."""
        content = f"""# E2E Test - Markdown V2 with Mentions

**Time**: {datetime.now().isoformat()}

This message mentions @all users using markdown_v2 format.
"""
        response = bridge.send(
            "wecom",
            webhook_url=webhook_url,
            message=content,
            msg_type="markdown_v2",
            mentioned_list=["@all"],
        )
        assert response.success is True
        assert response.data.get("errcode") == 0

    @pytest.mark.asyncio
    async def test_send_markdown_v2_message_async(self, bridge: NotifyBridge, webhook_url: str) -> None:
        """Test sending a markdown_v2 message asynchronously."""
        content = f"""# E2E Test - Async Markdown V2

**Time**: {datetime.now().isoformat()}

This is an async markdown_v2 message with _underscores_.
"""
        response = await bridge.send_async(
            "wecom",
            webhook_url=webhook_url,
            message=content,
            msg_type="markdown_v2",
        )
        assert response.success is True
        assert response.data.get("errcode") == 0


class TestWeComNewsMessage:
    """Test WeCom news message sending."""

    def test_send_news_message(self, bridge: NotifyBridge, webhook_url: str) -> None:
        """Test sending a news message."""
        response = bridge.send(
            "wecom",
            webhook_url=webhook_url,
            msg_type="news",
            articles=[
                {
                    "title": f"E2E Test - News Message",
                    "description": f"This is a news message sent at {datetime.now().isoformat()}",
                    "url": "https://github.com/loonghao/notify-bridge",
                    "picurl": "https://github.githubassets.com/images/modules/logos_page/GitHub-Mark.png",
                }
            ],
        )
        assert response.success is True
        assert response.data.get("errcode") == 0

    def test_send_news_message_multiple_articles(self, bridge: NotifyBridge, webhook_url: str) -> None:
        """Test sending a news message with multiple articles."""
        response = bridge.send(
            "wecom",
            webhook_url=webhook_url,
            msg_type="news",
            articles=[
                {
                    "title": "Article 1 - E2E Test",
                    "description": "First article description",
                    "url": "https://github.com/loonghao/notify-bridge",
                    "picurl": "https://github.githubassets.com/images/modules/logos_page/GitHub-Mark.png",
                },
                {
                    "title": "Article 2 - E2E Test",
                    "description": "Second article description",
                    "url": "https://github.com/loonghao/notify-bridge",
                },
            ],
        )
        assert response.success is True
        assert response.data.get("errcode") == 0

    @pytest.mark.asyncio
    async def test_send_news_message_async(self, bridge: NotifyBridge, webhook_url: str) -> None:
        """Test sending a news message asynchronously."""
        response = await bridge.send_async(
            "wecom",
            webhook_url=webhook_url,
            msg_type="news",
            articles=[
                {
                    "title": "E2E Test - Async News Message",
                    "description": f"Async news message sent at {datetime.now().isoformat()}",
                    "url": "https://github.com/loonghao/notify-bridge",
                }
            ],
        )
        assert response.success is True
        assert response.data.get("errcode") == 0


class TestWeComTemplateCardMessage:
    """Test WeCom template card message sending."""

    def test_send_template_card_text_notice(self, bridge: NotifyBridge, webhook_url: str) -> None:
        """Test sending a text_notice template card."""
        response = bridge.send(
            "wecom",
            webhook_url=webhook_url,
            msg_type="template_card",
            template_card_type="text_notice",
            template_card_source={
                "icon_url": "https://github.githubassets.com/images/modules/logos_page/GitHub-Mark.png",
                "desc": "E2E Test",
                "desc_color": 0,
            },
            template_card_main_title={
                "title": "E2E Test - Template Card",
                "desc": f"Test at {datetime.now().isoformat()}",
            },
            template_card_emphasis_content={
                "title": "100%",
                "desc": "Test Coverage",
            },
            template_card_sub_title_text="This is a test template card message",
            template_card_horizontal_content_list=[
                {"keyname": "Type", "value": "E2E Test"},
                {"keyname": "Time", "value": datetime.now().strftime("%H:%M:%S")},
            ],
            template_card_jump_list=[
                {
                    "type": 1,
                    "url": "https://github.com/loonghao/notify-bridge",
                    "title": "View on GitHub",
                }
            ],
            template_card_card_action={
                "type": 1,
                "url": "https://github.com/loonghao/notify-bridge",
            },
        )
        assert response.success is True
        assert response.data.get("errcode") == 0

    def test_send_template_card_news_notice(self, bridge: NotifyBridge, webhook_url: str) -> None:
        """Test sending a news_notice template card."""
        response = bridge.send(
            "wecom",
            webhook_url=webhook_url,
            msg_type="template_card",
            template_card_type="news_notice",
            template_card_source={
                "icon_url": "https://github.githubassets.com/images/modules/logos_page/GitHub-Mark.png",
                "desc": "E2E Test",
            },
            template_card_main_title={
                "title": "E2E Test - News Notice Card",
                "desc": f"Test at {datetime.now().isoformat()}",
            },
            template_card_vertical_content_list=[
                {
                    "title": "Feature 1",
                    "desc": "Description of feature 1",
                },
                {
                    "title": "Feature 2",
                    "desc": "Description of feature 2",
                },
            ],
            template_card_card_action={
                "type": 1,
                "url": "https://github.com/loonghao/notify-bridge",
            },
        )
        assert response.success is True
        assert response.data.get("errcode") == 0

    @pytest.mark.asyncio
    async def test_send_template_card_async(self, bridge: NotifyBridge, webhook_url: str) -> None:
        """Test sending a template card asynchronously."""
        response = await bridge.send_async(
            "wecom",
            webhook_url=webhook_url,
            msg_type="template_card",
            template_card_type="text_notice",
            template_card_main_title={
                "title": "E2E Test - Async Template Card",
                "desc": f"Async test at {datetime.now().isoformat()}",
            },
            template_card_card_action={
                "type": 1,
                "url": "https://github.com/loonghao/notify-bridge",
            },
        )
        assert response.success is True
        assert response.data.get("errcode") == 0


class TestWeComDirectNotifier:
    """Test using WeComNotifier directly without NotifyBridge."""

    def test_direct_notifier_text(self, notifier: WeComNotifier, webhook_url: str) -> None:
        """Test sending text message using notifier directly."""
        response = notifier.send(
            {
                "webhook_url": webhook_url,
                "msg_type": "text",
                "content": f"[E2E Test] Direct notifier text at {datetime.now().isoformat()}",
            }
        )
        assert response.success is True
        assert response.data.get("errcode") == 0

    def test_direct_notifier_markdown(self, notifier: WeComNotifier, webhook_url: str) -> None:
        """Test sending markdown message using notifier directly."""
        response = notifier.send(
            {
                "webhook_url": webhook_url,
                "msg_type": "markdown",
                "content": f"# Direct Notifier Test\n\n**Time**: {datetime.now().isoformat()}",
            }
        )
        assert response.success is True
        assert response.data.get("errcode") == 0

    def test_direct_notifier_markdown_v2(self, notifier: WeComNotifier, webhook_url: str) -> None:
        """Test sending markdown_v2 message using notifier directly."""
        response = notifier.send(
            {
                "webhook_url": webhook_url,
                "msg_type": "markdown_v2",
                "content": f"# Direct Notifier Test - Markdown V2\n\n_Underscored_ at {datetime.now().isoformat()}",
            }
        )
        assert response.success is True
        assert response.data.get("errcode") == 0

    def test_direct_notifier_with_schema(self, notifier: WeComNotifier, webhook_url: str) -> None:
        """Test sending message using WeComSchema directly."""
        schema = WeComSchema(
            webhook_url=webhook_url,
            msg_type="text",
            content=f"[E2E Test] Schema-based message at {datetime.now().isoformat()}",
        )
        response = notifier.send(schema)
        assert response.success is True
        assert response.data.get("errcode") == 0

    @pytest.mark.asyncio
    async def test_direct_notifier_async(self, notifier: WeComNotifier, webhook_url: str) -> None:
        """Test sending message asynchronously using notifier directly."""
        response = await notifier.send_async(
            {
                "webhook_url": webhook_url,
                "msg_type": "text",
                "content": f"[E2E Test] Direct async message at {datetime.now().isoformat()}",
            }
        )
        assert response.success is True
        assert response.data.get("errcode") == 0


class TestMarkdownVsMarkdownV2Comparison:
    """Compare markdown and markdown_v2 behavior."""

    def test_underscore_handling_comparison(self, bridge: NotifyBridge, webhook_url: str) -> None:
        """Test that underscores are handled differently in markdown vs markdown_v2."""
        # Send markdown message with underscores
        markdown_content = f"""# Markdown Test - {datetime.now().strftime("%H:%M:%S")}

Testing _underscore_handling_ in standard markdown.
"""
        response_md = bridge.send(
            "wecom",
            webhook_url=webhook_url,
            message=markdown_content,
            msg_type="markdown",
        )
        assert response_md.success is True

        # Send markdown_v2 message with underscores
        markdown_v2_content = f"""# Markdown V2 Test - {datetime.now().strftime("%H:%M:%S")}

Testing _underscore_handling_ in markdown_v2.
"""
        response_md_v2 = bridge.send(
            "wecom",
            webhook_url=webhook_url,
            message=markdown_v2_content,
            msg_type="markdown_v2",
        )
        assert response_md_v2.success is True

    def test_url_handling_comparison(self, bridge: NotifyBridge, webhook_url: str) -> None:
        """Test URL handling in markdown vs markdown_v2."""
        # Send markdown message with URL
        markdown_content = f"""# Markdown URL Test - {datetime.now().strftime("%H:%M:%S")}

[Link](https://github.com/loonghao/notify-bridge)
"""
        response_md = bridge.send(
            "wecom",
            webhook_url=webhook_url,
            message=markdown_content,
            msg_type="markdown",
        )
        assert response_md.success is True

        # Send markdown_v2 message with URL (forward slashes will be escaped)
        markdown_v2_content = f"""# Markdown V2 URL Test - {datetime.now().strftime("%H:%M:%S")}

[Link](https://github.com/loonghao/notify-bridge)
"""
        response_md_v2 = bridge.send(
            "wecom",
            webhook_url=webhook_url,
            message=markdown_v2_content,
            msg_type="markdown_v2",
        )
        assert response_md_v2.success is True
