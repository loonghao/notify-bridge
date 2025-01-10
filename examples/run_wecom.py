"""Test script for notify-bridge."""

# Import built-in modules
import asyncio
import os
from datetime import datetime

# Import local modules
from notify_bridge import NotifyBridge


def test_sync(url: str):
    """Test synchronous notifications.

    Args:
        url: Webhook URL.
    """
    print("Testing sync notifications...")

    bridge = NotifyBridge()
    # Send a text message
    response = bridge.notify(
        "wecom",
        webhook_url=url,
        title="Test Message",
        body="Hello from notify-bridge!",
        msg_type="text",
        mentioned_list=["@all"],
    )
    print(f"Text message response: {response}")

    # Send a markdown message
    response = bridge.notify(
        "wecom",
        webhook_url=url,
        title="Test Message",
        body="# Hello from notify-bridge!\n\nThis is a **markdown** message.",
        msg_type="markdown",
    )
    print(f"Markdown message response: {response}")

    # Send a news message
    response = bridge.notify(
        "wecom",
        webhook_url=url,
        title="Test Message",
        body="Hello from notify-bridge!",
        msg_type="news",
        articles=[
            {
                "title": "News Message Test",
                "description": f"This is a news message\nSend time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
                "url": "https://work.weixin.qq.com/",
                "picurl": "https://avatars.githubusercontent.com/u/153965?v=4",
            }
        ],
    )
    print(f"News message response: {response}")


async def test_async(url: str):
    """Test asynchronous notifications.

    Args:
        url: Webhook URL.
    """
    print("Testing async notifications...")

    bridge = NotifyBridge()
    # Send a text message
    response = await bridge.anotify(
        "wecom",
        webhook_url=url,
        title="Test Message",
        body="Hello from notify-bridge!",
        msg_type="text",
        mentioned_list=["@all"],
    )
    print(f"Text message response: {response}")

    # Send a markdown message
    response = await bridge.anotify(
        "wecom",
        webhook_url=url,
        title="Test Message",
        body="# Hello from notify-bridge!\n\nThis is a **markdown** message.",
        msg_type="markdown",
    )
    print(f"Markdown message response: {response}")

    # Send a news message
    response = await bridge.anotify(
        "wecom",
        webhook_url=url,
        title="Test Message",
        body="Hello from notify-bridge!",
        msg_type="news",
        articles=[
            {
                "title": "News Message Test",
                "description": f"This is a news message\nSend time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
                "url": "https://work.weixin.qq.com/",
                "picurl": "https://avatars.githubusercontent.com/u/153965?v=4",
            }
        ],
    )
    print(f"News message response: {response}")


def run_wecom(url=None):
    """Run the test script.

    Args:
        url: Webhook URL.
    """
    if url is None:
        url = os.environ.get("WECOM_URL", "https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key=YOUR_KEY")
    test_sync(url)
    asyncio.run(test_async(url))
