# Getting Started

This guide will help you get started with notify-bridge.

## Prerequisites

- Python 3.8 or higher
- pip or uv package manager

## Installation

Install notify-bridge using pip:

```bash
pip install notify-bridge
```

Or using uv:

```bash
uv pip install notify-bridge
```

## Basic Usage

### Creating a Bridge Instance

```python
from notify_bridge import NotifyBridge

# Create a bridge instance
bridge = NotifyBridge()

# List available notifiers
print(bridge.notifiers)
```

### Sending a Simple Message

```python
# Send a text message to WeCom
response = bridge.send(
    "wecom",
    webhook_url="YOUR_WEBHOOK_URL",
    message="Hello from notify-bridge!",
    msg_type="text"
)

print(f"Success: {response.success}")
print(f"Response: {response.data}")
```

### Async Support

notify-bridge fully supports async operations:

```python
import asyncio
from notify_bridge import NotifyBridge

async def send_notification():
    bridge = NotifyBridge()
    
    response = await bridge.send_async(
        "wecom",
        webhook_url="YOUR_WEBHOOK_URL",
        message="Hello from async notify-bridge!",
        msg_type="text"
    )
    
    return response

# Run the async function
response = asyncio.run(send_notification())
```

## Environment Variables

For security, it's recommended to store webhook URLs and tokens in environment variables:

```python
import os
from dotenv import load_dotenv
from notify_bridge import NotifyBridge

load_dotenv()

bridge = NotifyBridge()

response = bridge.send(
    "wecom",
    webhook_url=os.getenv("WECOM_WEBHOOK_URL"),
    message="Hello!",
    msg_type="text"
)
```

## Next Steps

- Learn about [WeCom integration](/guide/wecom)
- Learn about [Feishu integration](/guide/feishu)
- Learn about [creating custom plugins](/guide/plugins)
- Explore the [API reference](/api/core)
