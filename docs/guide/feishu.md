# Feishu (飞书)

Feishu (Lark) is a collaboration platform by ByteDance. notify-bridge provides support for Feishu webhook notifications.

## Supported Message Types

| Type | Description |
|------|-------------|
| `text` | Plain text messages |
| `post` | Rich text (post) messages |
| `image` | Image messages |
| `file` | File attachments |
| `interactive` | Interactive card messages |

## Getting Your Webhook URL

1. Open Feishu and go to your group chat
2. Click the group settings (gear icon)
3. Select **Bots** > **Add Bot** > **Custom Bot**
4. Copy the webhook URL

The URL format is:
```
https://open.feishu.cn/open-apis/bot/v2/hook/YOUR_KEY
```

## Basic Usage

### Text Message

```python
from notify_bridge import NotifyBridge

bridge = NotifyBridge()

response = bridge.send(
    "feishu",
    webhook_url="YOUR_WEBHOOK_URL",
    content="Hello from notify-bridge!",
    msg_type="text"
)
```

### Text with At Mentions

```python
response = bridge.send(
    "feishu",
    webhook_url="YOUR_WEBHOOK_URL",
    content="Hello <at user_id=\"all\">everyone</at>!",
    msg_type="text"
)
```

## Rich Text (Post) Messages

```python
response = bridge.send(
    "feishu",
    webhook_url="YOUR_WEBHOOK_URL",
    title="Project Update",
    content="This is the main content of the post message.",
    msg_type="post"
)
```

## Image Messages

```python
# Using local file
response = bridge.send(
    "feishu",
    webhook_url="YOUR_WEBHOOK_URL",
    msg_type="image",
    image_path="/path/to/image.png"
)

# Or using image_key (if you already have one)
response = bridge.send(
    "feishu",
    webhook_url="YOUR_WEBHOOK_URL",
    msg_type="image",
    image_key="img_xxx"
)
```

## File Messages

```python
# Using local file
response = bridge.send(
    "feishu",
    webhook_url="YOUR_WEBHOOK_URL",
    msg_type="file",
    file_path="/path/to/document.pdf"
)

# Or using file_key
response = bridge.send(
    "feishu",
    webhook_url="YOUR_WEBHOOK_URL",
    msg_type="file",
    file_key="file_xxx"
)
```

## Interactive Cards

```python
response = bridge.send(
    "feishu",
    webhook_url="YOUR_WEBHOOK_URL",
    msg_type="interactive",
    card={
        "config": {
            "wide_screen_mode": True
        },
        "header": {
            "title": {
                "tag": "plain_text",
                "content": "Card Title"
            },
            "template": "blue"
        },
        "elements": [
            {
                "tag": "div",
                "text": {
                    "tag": "lark_md",
                    "content": "**Bold** and *italic* text"
                }
            },
            {
                "tag": "action",
                "actions": [
                    {
                        "tag": "button",
                        "text": {
                            "tag": "plain_text",
                            "content": "Click Me"
                        },
                        "type": "primary",
                        "url": "https://example.com"
                    }
                ]
            }
        ]
    }
)
```

## Async Support

```python
import asyncio
from notify_bridge import NotifyBridge

async def send_feishu_notification():
    bridge = NotifyBridge()
    
    response = await bridge.send_async(
        "feishu",
        webhook_url="YOUR_WEBHOOK_URL",
        content="Async message!",
        msg_type="text"
    )
    
    return response

asyncio.run(send_feishu_notification())
```

## Error Handling

```python
from notify_bridge import NotifyBridge
from notify_bridge.exceptions import NotificationError, ValidationError

bridge = NotifyBridge()

try:
    response = bridge.send(
        "feishu",
        webhook_url="YOUR_WEBHOOK_URL",
        content="Test message",
        msg_type="text"
    )
    
    if response.data.get("code") != 0:
        print(f"Feishu API error: {response.data.get('msg')}")
        
except ValidationError as e:
    print(f"Validation error: {e}")
except NotificationError as e:
    print(f"Notification error: {e}")
```

## Best Practices

1. **Use environment variables** for webhook URLs
2. **Choose appropriate message types** for your content
3. **Handle API errors** gracefully
4. **Test in development groups** before production
