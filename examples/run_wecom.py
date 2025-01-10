"""Manual test script for WeCom notifier."""

# Import built-in modules
import asyncio
import os
import sys
from datetime import datetime

# Import third-party modules
from PIL import Image, ImageDraw

# Import local modules
from notify_bridge.notifiers.wecom import WeComNotifier, WeComSchema


def create_test_image(path: str, size: tuple = (800, 600)) -> str:
    """Create a test image.

    Args:
        path: Path to save the image.
        size: Image size (width, height).

    Returns:
        str: Path to the created image.
    """
    # Create a solid color image
    img = Image.new("RGB", size, color="white")

    # Draw a red rectangle in the middle
    draw = ImageDraw.Draw(img)
    rect_size = (size[0] // 4, size[1] // 4, size[0] * 3 // 4, size[1] * 3 // 4)
    draw.rectangle(rect_size, fill="red")

    # Save as JPEG format
    img.save(path, "JPEG", quality=95)
    return path


async def send_text_message(notifier: WeComNotifier, webhook_url: str, current_time: str) -> None:
    """Send a text message.

    Args:
        notifier: The notifier instance
        webhook_url: The webhook URL
        current_time: Current time string
    """
    print("\n1. Sending text message...")
    response = await notifier.asend(
        WeComSchema(
            webhook_url=webhook_url,
            title="Test Notification",
            body=f"This is a test message\nSend time: {current_time}",
            msg_type="text",
            mentioned_list=["@all"],  # Mention everyone
        )
    )
    print(f"Text message sent {'successfully' if response.success else 'failed'}")
    if not response.success:
        print(f"Error message: {response.error}")


async def send_markdown_message(notifier: WeComNotifier, webhook_url: str, current_time: str) -> None:
    """Send a markdown message.

    Args:
        notifier: The notifier instance
        webhook_url: The webhook URL
        current_time: Current time string
    """
    print("\n2. Sending Markdown message...")
    response = await notifier.asend(
        WeComSchema(
            webhook_url=webhook_url,
            title="Markdown Test",
            body=f"""**Test Notification**
> This is a test message in Markdown format

- Support Markdown syntax
- Send time: {current_time}
- Support multiple formats

[Click for details](https://work.weixin.qq.com/api/doc/90000/90136/91770)""",
            msg_type="markdown",
        )
    )
    print(f"Markdown message sent {'successfully' if response.success else 'failed'}")
    if not response.success:
        print(f"Error message: {response.error}")


async def send_news_message(notifier: WeComNotifier, webhook_url: str, current_time: str) -> None:
    """Send a news message.

    Args:
        notifier: The notifier instance
        webhook_url: The webhook URL
        current_time: Current time string
    """
    print("\n3. Sending news message...")
    response = await notifier.asend(
        WeComSchema(
            webhook_url=webhook_url,
            title="News Message Test",
            body="Test news message",
            msg_type="news",
            articles=[
                {
                    "title": "News Message Test",
                    "description": f"This is a news message\nSend time: {current_time}",
                    "url": "https://work.weixin.qq.com/",
                    "picurl": "https://avatars.githubusercontent.com/u/153965?v=4",
                }
            ],
        )
    )
    print(f"News message sent {'successfully' if response.success else 'failed'}")
    if not response.success:
        print(f"Error message: {response.error}")


async def send_image_message(notifier: WeComNotifier, webhook_url: str, test_image: str) -> None:
    """Send an image message.

    Args:
        notifier: The notifier instance
        webhook_url: The webhook URL
        test_image: Path to the test image
    """
    print("\n4. Sending image message (from local file)...")
    response = await notifier.asend(
        WeComSchema(
            webhook_url=webhook_url, title="Image Test", body="Test image", msg_type="image", file_path=test_image
        )
    )
    print(f"Image message sent {'successfully' if response.success else 'failed'}")
    if not response.success:
        print(f"Error message: {response.error}")


async def send_file_message(notifier: WeComNotifier, webhook_url: str, current_time: str) -> None:
    """Send a file message.

    Args:
        notifier: The notifier instance
        webhook_url: The webhook URL
        current_time: Current time string
    """
    # Create and send text file
    test_file = "test.txt"
    if not os.path.exists(test_file):
        with open(test_file, "w", encoding="utf-8") as f:
            f.write(f"This is a test file\nCreation time: {current_time}")

    print("\n5. Sending file message...")
    try:
        response = await notifier.asend(
            WeComSchema(
                webhook_url=webhook_url, title="File Test", body="Test file", msg_type="file", file_path=test_file
            )
        )
        print(f"File message sent {'successfully' if response.success else 'failed'}")
        if not response.success:
            print(f"Error message: {response.error}")
    finally:
        # Clean up test file
        if os.path.exists(test_file):
            os.remove(test_file)


async def main():
    """Run manual tests for WeCom notifier."""
    # Replace with your WeCom robot webhook URL
    webhook_url = "https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key=xxxxxx"

    if len(sys.argv) > 1:
        webhook_url = sys.argv[1]

    # Create notifier instance
    notifier = WeComNotifier(webhook_url=webhook_url)
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # Create test image
    test_image = "test_image.jpg"
    create_test_image(test_image)

    try:
        # Send various types of messages
        await send_text_message(notifier, webhook_url, current_time)
        await send_markdown_message(notifier, webhook_url, current_time)
        await send_news_message(notifier, webhook_url, current_time)
        await send_image_message(notifier, webhook_url, test_image)
        await send_file_message(notifier, webhook_url, current_time)

    except Exception as e:
        print(f"Error sending message: {str(e)}")
    finally:
        # Clean up test image
        if os.path.exists(test_image):
            os.remove(test_image)
        await notifier.aclose()


if __name__ == "__main__":
    asyncio.run(main())
