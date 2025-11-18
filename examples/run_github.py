"""Example script for GitHub notifications."""

# Import built-in modules
import asyncio
import os

from notify_bridge.components import NotificationError

# Import local modules
from notify_bridge import NotifyBridge


def test_text_issue(bridge: NotifyBridge, owner: str, repo: str, token: str) -> None:
    """Test creating a text issue.

    Args:
        bridge: NotifyBridge instance
        owner: Repository owner
        repo: Repository name
        token: GitHub personal access token
    """
    print("\nTesting text issue...")
    try:
        response = bridge.send(
            "github",
            owner=owner,
            repo=repo,
            token=token,
            title="Test Issue",
            message="Hello from notify-bridge! This is a test issue.",
            labels=["test", "notify-bridge"],
            msg_type="text",
        )
        print(f"[+] Text issue created successfully: {response}")
    except NotificationError as e:
        print(f"[X] Failed to create text issue: {e}")


def test_markdown_issue(bridge: NotifyBridge, owner: str, repo: str, token: str) -> None:
    """Test creating a markdown issue.

    Args:
        bridge: NotifyBridge instance
        owner: Repository owner
        repo: Repository name
        token: GitHub personal access token
    """
    print("\nTesting markdown issue...")
    try:
        response = bridge.send(
            "github",
            owner=owner,
            repo=repo,
            token=token,
            title="Test Markdown Issue",
            message="# Hello from notify-bridge!\n\nThis is a **markdown** test issue.\n\n- Item 1\n- Item 2",
            labels=["test", "notify-bridge"],
            msg_type="markdown",
        )
        print(f"[+] Markdown issue created successfully: {response}")
    except NotificationError as e:
        print(f"[X] Failed to create markdown issue: {e}")


async def test_async_issues(bridge: NotifyBridge, owner: str, repo: str, token: str) -> None:
    """Test creating issues asynchronously.

    Args:
        bridge: NotifyBridge instance
        owner: Repository owner
        repo: Repository name
        token: GitHub personal access token
    """
    print("\nTesting async issues...")
    try:
        tasks = [
            bridge.send_async(
                "github",
                owner=owner,
                repo=repo,
                token=token,
                title="Async Test Issue 1",
                message="Hello from notify-bridge! This is an async test issue.",
                labels=["test", "notify-bridge", "async"],
                msg_type="text",
            ),
            bridge.send_async(
                "github",
                owner=owner,
                repo=repo,
                token=token,
                title="Async Test Issue 2",
                message="# Hello from notify-bridge!\n\nThis is an async **markdown** test issue.",
                labels=["test", "notify-bridge", "async"],
                msg_type="markdown",
            ),
        ]
        results = await asyncio.gather(*tasks)
        for i, response in enumerate(results):
            print(f"[+] Async issue {i+1} created successfully: {response}")
    except NotificationError as e:
        print(f"[X] Failed to create async issues: {e}")


def run_github() -> None:
    """Main function."""
    print("Setting up test environment...")

    owner = os.getenv("GITHUB_OWNER")
    if not owner:
        print("[X] GITHUB_OWNER environment variable not set")
        return

    repo = os.getenv("GITHUB_REPO")
    if not repo:
        print("[X] GITHUB_REPO environment variable not set")
        return

    token = os.getenv("GITHUB_TOKEN")
    if not token:
        print("[X] GITHUB_TOKEN environment variable not set")
        return

    print(f"\nUsing repository: {owner}/{repo}")

    print("\nInitializing NotifyBridge...")
    with NotifyBridge() as bridge:
        print(f"Available notifiers: {bridge._factory._notifiers}")

        print("\nRunning synchronous tests...")
        test_text_issue(bridge, owner, repo, token)
        test_markdown_issue(bridge, owner, repo, token)

        print("\nRunning asynchronous tests...")
        asyncio.run(test_async_issues(bridge, owner, repo, token))

        print("\nAll tests completed!")


if __name__ == "__main__":
    run_github()
