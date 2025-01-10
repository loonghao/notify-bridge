"""Test script for notify-bridge."""

# Import built-in modules
import asyncio
import os

# Import local modules
from notify_bridge import NotifyBridge


def test_sync(url):
    """Test synchronous notifications."""
    print("Testing sync notifications...")

    bridge = NotifyBridge()
    # Send a text message
    response = bridge.notify(
        "feishu",
        webhook_url=url,
        title="Test Message",
        body="Hello from notify-bridge!",
        msg_type="text",
    )
    print(f"Text message response: {response}")

    # Send a markdown message
    response = bridge.notify(
        "feishu",
        webhook_url=url,
        title="Test Message",
        body="# Hello from notify-bridge!\n\nThis is a **markdown** message.",
        msg_type="post",
    )
    print(f"Markdown message response: {response}")


async def test_async(url):
    """Test asynchronous notifications."""
    print("Testing async notifications...")

    bridge = NotifyBridge()
    # Send a text message
    response = await bridge.anotify(
        "feishu",
        webhook_url=url,
        title="Test Message",
        body="Hello from notify-bridge!",
        msg_type="text",
    )
    print(f"Text message response: {response}")

    # Send a markdown message
    response = await bridge.anotify(
        "feishu",
        webhook_url=url,
        title="Test Message",
        body="# Hello from notify-bridge!\n\nThis is a **markdown** message.",
        msg_type="post",
    )
    print(f"Markdown message response: {response}")


def run_feishu(url=None):
    """Run the test script."""
    if url is None:
        url = os.environ.get("FEISHU_URL", "https://open.feishu.cn/open-apis/bot/v2/hook/YOUR_KEY")
    test_sync(url)
    asyncio.run(test_async(url))
