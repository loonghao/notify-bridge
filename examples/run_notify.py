"""Example script for Notify notifications."""

# Import built-in modules
import asyncio
import os
from typing import Optional

from notify_bridge.components import NotificationError

# Import local modules
from notify_bridge import NotifyBridge


def test_text_message(bridge: NotifyBridge, base_url: str, token: Optional[str] = None) -> None:
    """Test sending text message.

    Args:
        bridge: NotifyBridge instance
        base_url: Base URL for Notify API
        token: Bearer token for authentication
    """
    print("\nTesting text message...")
    try:
        response = bridge.send(
            "notify",
            base_url=base_url,
            title="Test Message",
            message="Hello from notify-bridge! This is a test message.",
            # token=token,
            tags=["test", "notify-bridge"],
            msg_type="text",
        )
        print(f"[+] Text message sent successfully: {response}")
    except NotificationError as e:
        print(f"[X] Failed to send text message: {e}")


async def test_async_messages(bridge: NotifyBridge, base_url: str, token: Optional[str] = None) -> None:
    """Test sending messages asynchronously.

    Args:
        bridge: NotifyBridge instance
        base_url: Base URL for Notify API
        token: Bearer token for authentication
    """
    print("\nTesting async messages...")
    try:
        tasks = [
            bridge.send_async(
                "notify",
                base_url=base_url,
                title="Async Test Message 1",
                message="Hello from notify-bridge! This is an async text message.",
                # token=token,
                tags=["test", "notify-bridge", "async"],
                msg_type="text",
            ),
            bridge.send_async(
                "notify",
                base_url=base_url,
                title="Async Test Message 2",
                message="Hello from notify-bridge! This is another async text message.",
                # token=token,
                tags=["test", "notify-bridge", "async"],
                msg_type="text",
            ),
        ]
        results = await asyncio.gather(*tasks)
        for i, response in enumerate(results):
            print(f"[+] Async message {i+1} sent successfully: {response}")
    except NotificationError as e:
        print(f"[X] Failed to send async messages: {e}")


def run_notify() -> None:
    """Main function."""
    print("Setting up test environment...")

    base_url = os.getenv("NOTIFY_BASE_URL")
    if not base_url:
        print("[X] NOTIFY_BASE_URL environment variable not set")
        return

    token = os.getenv("NOTIFY_TOKEN")
    if token:
        print(f"Using token: {token}")
    else:
        print("[!] No token provided")

    print(f"\nUsing base URL: {base_url}")

    print("\nInitializing NotifyBridge...")
    with NotifyBridge() as bridge:
        print(f"Available notifiers: {bridge._factory._notifiers}")

        print("\nRunning synchronous tests...")
        test_text_message(bridge, base_url, token)

        print("\nRunning asynchronous tests...")
        asyncio.run(test_async_messages(bridge, base_url, token))

        print("\nAll tests completed!")


if __name__ == "__main__":
    run_notify()
