# notify-bridge

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
- [ ] WeChat Work (企业微信)
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

Each notifier has its own configuration schema. Here's an example for Feishu:

```python
bridge.notify(
    "feishu",
    webhook_url="YOUR_WEBHOOK_URL",
    title="Message Title",
    body="Message Body",
    msg_type="interactive",  # or "text"
    at_all=True,  # @所有人
    at_users=["user1", "user2"]  # @特定用户
)
```

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
