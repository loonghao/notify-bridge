# notify-bridge

<div align="center">

[![Python Version](https://img.shields.io/pypi/pyversions/notify-bridge)](https://img.shields.io/pypi/pyversions/notify-bridge)
[![Nox](https://img.shields.io/badge/%F0%9F%A6%8A-Nox-D85E00.svg)](https://github.com/wntrblm/nox)
[![PyPI Version](https://img.shields.io/pypi/v/notify-bridge?color=green)](https://pypi.org/project/notify-bridge/)
[![Downloads](https://static.pepy.tech/badge/notify-bridge)](https://pepy.tech/project/notify-bridge)
[![Downloads](https://static.pepy.tech/badge/notify-bridge/month)](https://pepy.tech/project/notify-bridge)
[![Downloads](https://static.pepy.tech/badge/notify-bridge/week)](https://pepy.tech/project/notify-bridge)
[![License](https://img.shields.io/pypi/l/notify-bridge)](https://pypi.org/project/notify-bridge/)
[![PyPI Format](https://img.shields.io/pypi/format/notify-bridge)](https://pypi.org/project/notify-bridge/)
[![Maintenance](https://img.shields.io/badge/Maintained%3F-yes-green.svg)](https://github.com/loonghao/notify-bridge/graphs/commit-activity)
![Codecov](https://img.shields.io/codecov/c/github/loonghao/notify-bridge)
</div>


A flexible notification bridge for sending messages to various platforms.

## Features

- 🚀 Simple and intuitive API
- 🔌 Plugin system for easy extension
- 🔄 Both synchronous and asynchronous support
- 🛡️ Type-safe with Pydantic models
- 📝 Rich message formats (text, markdown, etc.)
- 🌐 Multiple platform support

## Installation

```bash
pip install notify-bridge
```

## Quick Start

```python
from notify_bridge import NotifyBridge

# Create a bridge instance
bridge = NotifyBridge()

# Send a notification synchronously
response = bridge.notify(
    "feishu",
    webhook_url="YOUR_WEBHOOK_URL",
    title="Test Message",
    body="Hello from notify-bridge!",
    msg_type="text"
)
print(response)

# Send a notification asynchronously
async def send_async():
    response = await bridge.anotify(
        "feishu",
        webhook_url="YOUR_WEBHOOK_URL",
        title="Async Test Message",
        body="# Hello from notify-bridge!\n\nThis is a **markdown** message.",
        msg_type="interactive"
    )
    print(response)
```

## Supported Platforms

- [x] Feishu (飞书)
- [ ] DingTalk (钉钉)
- [x] WeChat Work (企业微信)
- [ ] Email
- [ ] Slack
- [ ] Discord

## Creating a Plugin

1. Create a new notifier class:

```python
from notify_bridge.types import BaseNotifier, NotificationSchema
from pydantic import Field

class MySchema(NotificationSchema):
    webhook_url: str = Field(..., description="Webhook URL")
    title: str = Field(..., description="Message title")
    body: str = Field(..., description="Message body")

class MyNotifier(BaseNotifier):
    name = "my_notifier"
    schema = MySchema

    def send(self, notification: NotificationSchema):
        # Implement your notification logic here
        pass

    async def asend(self, notification: NotificationSchema):
        # Implement your async notification logic here
        pass
```

2. Register your plugin in `pyproject.toml`:

```toml
[project.entry-points."notify_bridge.notifiers"]
my_notifier = "my_package.my_module:MyNotifier"
```

## Configuration

Each notifier has its own configuration schema. Here are some examples:

### Feishu Example
```python
# Send a text message
bridge.notify(
    "feishu",
    webhook_url="YOUR_WEBHOOK_URL",
    title="Message Title",
    body="Message Body",
    msg_type="text"
)

# Send an interactive (markdown) message with @mentions
bridge.notify(
    "feishu",
    webhook_url="YOUR_WEBHOOK_URL",
    title="Message Title",
    body="Message Body",
    msg_type="interactive",
    at_all=True,  # @所有人
    at_users=["user1", "user2"]  # @特定用户
)
```

### WeChat Work Example
```python
# Send a text message
bridge.notify(
    "wecom",
    webhook_url="YOUR_WEBHOOK_URL",
    title="Message Title",
    body="Message Body",
    msg_type="text",
    mentioned_list=["user1", "user2"],  # Optional: mention users by ID
    mentioned_mobile_list=["13800138000"]  # Optional: mention users by mobile
)

# Send a markdown message
bridge.notify(
    "wecom",
    webhook_url="YOUR_WEBHOOK_URL",
    title="Message Title",
    body="**Bold Text**\n> Quote\n[Link](https://example.com)",
    msg_type="markdown"
)

# Send an image
bridge.notify(
    "wecom",
    webhook_url="YOUR_WEBHOOK_URL",
    title="Image Message",
    body="Image Description",
    msg_type="image",
    file_path="path/to/image.jpg"  # or use file_url="https://example.com/image.jpg"
)

# Send a file
bridge.notify(
    "wecom",
    webhook_url="YOUR_WEBHOOK_URL",
    title="File Message",
    body="File Description",
    msg_type="file",
    file_path="path/to/document.pdf"  # or use file_url="https://example.com/document.pdf"
)
```

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
