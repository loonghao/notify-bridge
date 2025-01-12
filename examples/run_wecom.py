"""Test script for WeCom notifier."""

# Import built-in modules
import asyncio
from datetime import datetime
import os
from pathlib import Path

# Import local modules
from notify_bridge import NotifyBridge


def test_sync(url: str) -> None:
    """Test synchronous notifications.

    Args:
        url: Webhook URL.
    """
    print("\nTesting synchronous notifications...")
    print("-" * 50)

    bridge = NotifyBridge()
    print(bridge.notifiers)

    # Send a text message
    print("\nTesting text message...")
    response = bridge.send(
        "wecom", webhook_url=url, message="Hello from notify-bridge!", msg_type="text", mentioned_list=["@all"]
    )
    print(f"Response: {response}")

    # Send a markdown message
    print("\nTesting markdown message...")
    response = bridge.send(
        "wecom",
        webhook_url=url,
        message="# Hello from notify-bridge!\n\n**Time**: {}\n\nThis is a *markdown* message.".format(
            datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        ),
        msg_type="markdown",
    )
    print(f"Response: {response}")

    # Send an image message
    print("\nTesting image message...")
    image_path = Path(__file__).parent / "assets" / "example.png"
    if image_path.exists():
        response = bridge.send("wecom", webhook_url=url, msg_type="image", image_path=str(image_path))
        print(f"Response: {response}")
    else:
        print(f"[X] Example image not found at {image_path}")

    # Send a news message
    print("\nTesting news message...")
    response = bridge.send(
        "wecom",
        webhook_url=url,
        msg_type="news",
        mentioned_list=["@all"],
        articles=[
            {
                "title": "Hello from notify-bridge!",
                "description": "This is a news message sent at {}".format(datetime.now().strftime("%Y-%m-%d %H:%M:%S")),
                "url": "https://github.com/loonghao/notify-bridge",
                "picurl": "https://github.githubassets.com/images/modules/logos_page/GitHub-Mark.png",
            }
        ],
    )
    print(f"Response: {response}")


async def test_async(url: str) -> None:
    """Test asynchronous notifications.

    Args:
        url: Webhook URL.
    """
    print("\nTesting asynchronous notifications...")
    print("-" * 50)

    bridge = NotifyBridge()
    print(bridge.notifiers)

    # Send a text message
    print("\nTesting async text message...")
    response = await bridge.send_async(
        "wecom", webhook_url=url, message="Hello from notify-bridge! (async)", msg_type="text", mentioned_list=["@all"]
    )
    print(f"Response: {response}")

    # Send a markdown message
    print("\nTesting async markdown message...")
    response = await bridge.send_async(
        "wecom",
        webhook_url=url,
        message="# Hello from notify-bridge! (async)\n\n**Time**: {}\n\nThis is an *async markdown* message.".format(
            datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        ),
        msg_type="markdown",
    )
    print(f"Response: {response}")

    # Send an image message
    print("\nTesting async image message...")
    image_path = Path(__file__).parent / "assets" / "example.png"
    if image_path.exists():
        response = await bridge.send_async("wecom", webhook_url=url, msg_type="image", image_path=str(image_path))
        print(f"Response: {response}")
    else:
        print(f"[X] Example image not found at {image_path}")

    # Send a news message
    print("\nTesting async news message...")
    response = await bridge.send_async(
        "wecom",
        webhook_url=url,
        msg_type="news",
        mentioned_list=["@all"],
        articles=[
            {
                "title": "Hello from notify-bridge! (async)",
                "description": "This is an async news message sent at {}".format(
                    datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                ),
                "url": "https://github.com/loonghao/notify-bridge",
                "picurl": "https://github.githubassets.com/images/modules/logos_page/GitHub-Mark.png",
            }
        ],
    )
    print(f"Response: {response}")


def setup_test_environment() -> None:
    """Setup test environment.

    This function creates the assets directory and example files if they don't exist.
    """
    print("Setting up test environment...")

    # Create assets directory
    assets_dir = Path(__file__).parent / "assets"
    assets_dir.mkdir(exist_ok=True)

    # Create example image if it doesn't exist
    example_image = assets_dir / "example.png"
    if not example_image.exists():
        # Create a simple colored image using PIL
        try:
            # Import third-party modules
            from PIL import Image
            from PIL import ImageDraw

            # Create a 200x200 image with white background
            img = Image.new("RGB", (200, 200), "white")
            draw = ImageDraw.Draw(img)

            # Draw some shapes
            draw.rectangle([50, 50, 150, 150], fill="blue")
            draw.ellipse([75, 75, 125, 125], fill="white")

            # Save the image
            img.save(example_image)
            print(f"Created example image at {example_image}")
        except ImportError:
            print("PIL not installed, skipping example image creation")


def run_wecom(url: str = None) -> None:
    """Run the test script.

    Args:
        url: Webhook URL.
    """
    # Setup test environment
    setup_test_environment()

    # Get webhook URL from environment if not provided
    webhook_url = url or os.getenv("WECOM_WEBHOOK_URL")
    if not webhook_url:
        print("Please provide webhook URL via argument or WECOM_WEBHOOK_URL environment variable")
        return

    print(f"\nUsing webhook URL: {webhook_url}")

    print("\nInitializing NotifyBridge...")
    bridge = NotifyBridge()
    print(bridge.notifiers)

    # Run tests
    test_sync(webhook_url)
    asyncio.run(test_async(webhook_url))


if __name__ == "__main__":
    run_wecom()
