"""Example script for Feishu notification.

This script demonstrates how to use the notify-bridge to send notifications to Feishu.
"""

# Import built-in modules
import asyncio
import os
from pathlib import Path

# Import local modules
from notify_bridge import NotifyBridge
from notify_bridge.exceptions import NotificationError


def test_text_message(bridge: NotifyBridge, url: str) -> None:
    """Test sending text message.

    Args:
        bridge: NotifyBridge instance
        url: Webhook URL
    """
    print("\nTesting text message...")
    try:
        response = bridge.send(
            "feishu",
            url=url,
            content="Hello from notify-bridge! This is a text message.",
            msg_type="text",
        )
        print(f"[+] Text message sent successfully: {response}")
    except NotificationError as e:
        print(f"[X] Failed to send text message: {e}")


def test_post_message(bridge: NotifyBridge, url: str) -> None:
    """Test sending post message.

    Args:
        bridge: NotifyBridge instance
        url: Webhook URL
    """
    print("\nTesting post message...")
    try:
        post_content = {
            "zh_cn": [
                [
                    {"tag": "text", "text": "Hello from notify-bridge!\n\n"},
                    {"tag": "text", "text": "This is a post message with rich text support:\n\n"},
                ],
                [
                    {"tag": "text", "text": "• Support "},
                    {"tag": "text", "text": "bold", "text_type": "bold"},
                    {"tag": "text", "text": " text\n"},
                ],
                [
                    {"tag": "text", "text": "• Support "},
                    {"tag": "text", "text": "italic", "text_type": "italic"},
                    {"tag": "text", "text": " text\n"},
                ],
                [
                    {"tag": "text", "text": "• Support "},
                    {"tag": "text", "text": "code", "text_type": "code"},
                    {"tag": "text", "text": " blocks\n"},
                ],
                [{"tag": "text", "text": "\n> This is a quote"}],
            ]
        }
        response = bridge.send(
            "feishu",
            url=url,
            post_content=post_content,
            msg_type="post",
        )
        print(f"[+] Post message sent successfully: {response}")
    except NotificationError as e:
        print(f"[X] Failed to send post message: {e}")


def test_image_message(bridge: NotifyBridge, url: str) -> None:
    """Test sending image message.

    Args:
        bridge: NotifyBridge instance
        url: Webhook URL
    """
    print("\nTesting image message...")

    # Get example image path
    image_path = Path(__file__).parent / "assets" / "example.png"
    if not image_path.exists():
        print(f"[X] Example image not found at {image_path}")
        return

    try:
        response = bridge.send(
            "feishu",
            url=url,
            msg_type="image",
            image_path=str(image_path),
        )
        print(f"[+] Image message sent successfully: {response}")
    except NotificationError as e:
        print(f"[X] Failed to send image message: {e}")


def test_file_message(bridge: NotifyBridge, url: str, token: str) -> None:
    """Test sending file message.

    Args:
        bridge: NotifyBridge instance
        url: Webhook URL
        token: Access token
    """
    print("\nTesting file message...")

    # Get example file path
    file_path = Path(__file__).parent / "assets" / "example.txt"
    if not file_path.exists():
        print(f"[X] Example file not found at {file_path}")
        return

    try:
        response = bridge.send(
            "feishu",
            url=url,
            token=token,
            msg_type="file",
            file_path=str(file_path),
        )
        print(f"[+] File message sent successfully: {response}")
    except NotificationError as e:
        print(f"[X] Failed to send file message: {e}")


def test_interactive_message(bridge: NotifyBridge, url: str) -> None:
    """Test sending interactive message.

    Args:
        bridge: NotifyBridge instance
        url: Webhook URL
    """
    print("\nTesting interactive message...")
    try:
        response = bridge.send(
            "feishu",
            url=url,
            msg_type="interactive",
            card_header={"title": "This is a test card", "template": "red"},
            card_elements=[
                {"tag": "div", "text": {"tag": "plain_text", "content": "This is a test card with some content."}},
                {"tag": "div", "text": {"tag": "lark_md", "content": "**Bold text** and *italic text*"}},
                {
                    "tag": "action",
                    "actions": [
                        {"tag": "button", "text": {"tag": "plain_text", "content": "Click me!"}, "type": "primary"}
                    ],
                },
            ],
        )
        print(f"[+] Interactive message sent successfully: {response}")
    except NotificationError as e:
        print(f"[X] Failed to send interactive message: {e}")


async def test_async_messages(bridge: NotifyBridge, url: str) -> None:
    """Test sending messages asynchronously.

    Args:
        bridge: NotifyBridge instance
        url: Webhook URL
    """
    print("\nTesting async messages...")
    try:
        tasks = [
            bridge.send_async(
                "feishu",
                url=url,
                content="Hello from notify-bridge! This is an async text message.",
                msg_type="text",
            ),
            bridge.send_async(
                "feishu",
                url=url,
                post_content={
                    "zh_cn": [[{"tag": "text", "text": "Hello from notify-bridge! This is an async post message."}]]
                },
                msg_type="post",
            ),
        ]
        results = await asyncio.gather(*tasks)
        for i, response in enumerate(results):
            print(f"[+] Async message {i+1} sent successfully: {response}")
    except NotificationError as e:
        print(f"[X] Failed to send async messages: {e}")


def setup_test_environment() -> None:
    """Setup test environment.

    This function creates the assets directory and example files if they don't exist.
    """
    # Create assets directory
    assets_dir = Path(__file__).parent / "assets"
    assets_dir.mkdir(exist_ok=True)

    # Create example text file
    example_file = assets_dir / "example.txt"
    if not example_file.exists():
        example_file.write_text("This is an example file for testing.")

    # Create example image file
    example_image = assets_dir / "example.png"
    if not example_image.exists():
        # Create a simple black square as example image
        # Import third-party modules
        from PIL import Image

        img = Image.new("RGB", (100, 100), color="black")
        img.save(example_image)


def run_feishu(url: str = None, token: str = None) -> None:
    """Run all Feishu notification tests.

    Args:
        url: Webhook URL, if not provided will try to get from environment
        token: Access token, if not provided will try to get from environment
    """
    # Get webhook URL from environment if not provided
    url = url or os.getenv("FEISHU_WEBHOOK_URL")
    if not url:
        print("[X] No webhook URL provided and FEISHU_WEBHOOK_URL not set")
        return

    # Get access token from environment if not provided
    token = token or os.getenv("FEISHU_ACCESS_TOKEN")

    print("Setting up test environment...")
    setup_test_environment()

    print(f"\nUsing webhook URL: {url}")
    if token:
        print(f"Using access token: {token}")
    else:
        print("[!] No access token provided, skipping file tests")

    print("\nInitializing NotifyBridge...")
    bridge = NotifyBridge()
    print(f"Available notifiers: {bridge._factory._notifiers}")

    print("\nRunning synchronous tests...")
    test_text_message(bridge, url)
    test_post_message(bridge, url)
    test_image_message(bridge, url)
    test_interactive_message(bridge, url)
    if token:
        test_file_message(bridge, url, token)
    else:
        print("[!] Skipping file tests (no token provided)")

    print("\nRunning asynchronous tests...")
    asyncio.run(test_async_messages(bridge, url))

    print("\nAll tests completed!")


if __name__ == "__main__":
    run_feishu()
