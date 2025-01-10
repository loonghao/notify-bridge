"""Test script for notify-bridge."""

# Import built-in modules
import asyncio

# Import local modules
from notify_bridge import NotifyBridge


def test_sync():
    """Test synchronous notifications."""
    print("Testing sync notifications...")

    bridge = NotifyBridge()
    try:
        # Send a text message
        response = bridge.notify(
            "feishu",
            webhook_url="https://open.feishu.cn/open-apis/bot/v2/hook/xxxxxx",
            title="Test Message",
            body="Hello from notify-bridge!",
            msg_type="text",
        )
        print(f"Text message response: {response}")

        # Send a markdown message
        response = bridge.notify(
            "feishu",
            webhook_url="https://open.feishu.cn/open-apis/bot/v2/hook/xxxxxx",
            title="Test Message",
            body="# Hello from notify-bridge!\n\nThis is a **markdown** message.",
            msg_type="interactive",
        )
        print(f"Markdown message response: {response}")
    finally:
        bridge.close()


async def test_async():
    """Test asynchronous notifications."""
    print("Testing async notifications...")

    bridge = NotifyBridge()
    try:
        # Send a text message
        response = await bridge.anotify(
            "feishu",
            webhook_url="https://open.feishu.cn/open-apis/bot/v2/hook/xxxxxx",
            title="Async Test Message",
            body="Hello from notify-bridge (async)!",
            msg_type="text",
        )
        print(f"Async text message response: {response}")

        # Send a markdown message
        response = await bridge.anotify(
            "feishu",
            webhook_url="https://open.feishu.cn/open-apis/bot/v2/hook/xxxxxx",
            title="Async Test Message",
            body="# Hello from notify-bridge (async)!\n\nThis is a **markdown** message.",
            msg_type="interactive",
        )
        print(f"Async markdown message response: {response}")
    finally:
        await bridge.aclose()


def main():
    """Run the test script."""
    # Test sync notifications
    test_sync()

    # Test async notifications
    asyncio.run(test_async())


if __name__ == "__main__":
    main()
