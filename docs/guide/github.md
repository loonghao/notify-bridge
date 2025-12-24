# GitHub

notify-bridge supports creating GitHub Issues as a notification mechanism.

## Supported Message Types

| Type | Description |
|------|-------------|
| `text` | Plain text issue body |
| `markdown` | Markdown formatted issue body |

## Getting Your GitHub Token

1. Go to GitHub Settings > Developer settings > Personal access tokens
2. Generate a new token with `repo` scope
3. Copy the token

## Basic Usage

### Create a Text Issue

```python
from notify_bridge import NotifyBridge

bridge = NotifyBridge()

response = bridge.send(
    "github",
    owner="username",
    repo="repository",
    token="YOUR_GITHUB_TOKEN",
    title="Bug Report",
    message="Found a bug in the application.",
    msg_type="text"
)
```

### Create a Markdown Issue

```python
response = bridge.send(
    "github",
    owner="username",
    repo="repository",
    token="YOUR_GITHUB_TOKEN",
    title="Feature Request",
    message="""# Feature Request

## Description
Add support for dark mode.

## Use Case
Users want to reduce eye strain when using the app at night.

## Proposed Solution
- Add a toggle in settings
- Detect system preference
- Remember user choice
""",
    msg_type="markdown"
)
```

### Add Labels

```python
response = bridge.send(
    "github",
    owner="username",
    repo="repository",
    token="YOUR_GITHUB_TOKEN",
    title="Bug: Login fails",
    message="Users cannot log in with correct credentials.",
    labels=["bug", "priority-high"],
    msg_type="text"
)
```

## Async Support

```python
import asyncio
from notify_bridge import NotifyBridge

async def create_issues():
    bridge = NotifyBridge()
    
    # Create multiple issues concurrently
    tasks = [
        bridge.send_async(
            "github",
            owner="username",
            repo="repository",
            token="YOUR_GITHUB_TOKEN",
            title=f"Issue {i}",
            message=f"This is issue number {i}",
            msg_type="text"
        )
        for i in range(3)
    ]
    
    responses = await asyncio.gather(*tasks)
    return responses

asyncio.run(create_issues())
```

## Error Handling

```python
from notify_bridge import NotifyBridge
from notify_bridge.exceptions import NotificationError

bridge = NotifyBridge()

try:
    response = bridge.send(
        "github",
        owner="username",
        repo="repository",
        token="YOUR_GITHUB_TOKEN",
        title="Test Issue",
        message="Test content",
        msg_type="text"
    )
except NotificationError as e:
    print(f"Failed to create issue: {e}")
```

## Best Practices

1. **Secure your token** - Never commit tokens to version control
2. **Use environment variables** for sensitive data
3. **Add appropriate labels** for better organization
4. **Use markdown** for well-formatted issues
