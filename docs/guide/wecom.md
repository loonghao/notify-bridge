# WeCom (企业微信)

WeCom (WeChat Work) is a popular enterprise communication platform in China. notify-bridge provides comprehensive support for WeCom webhook notifications.

## Supported Message Types

| Type | Description |
|------|-------------|
| `text` | Plain text messages |
| `markdown` | Standard markdown format |
| `markdown_v2` | Enhanced markdown with better underscore handling |
| `image` | Image messages (base64 encoded) |
| `news` | News/article cards |
| `file` | File attachments |
| `voice` | Voice messages |
| `template_card` | Rich template cards |

## Getting Your Webhook URL

1. Open WeCom (企业微信) admin console
2. Navigate to **Application Management** > **Group Robot**
3. Create a new robot or select an existing one
4. Copy the webhook URL

The URL format is:
```
https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key=YOUR_KEY
```

## Basic Usage

### Text Message

```python
from notify_bridge import NotifyBridge

bridge = NotifyBridge()

response = bridge.send(
    "wecom",
    webhook_url="YOUR_WEBHOOK_URL",
    message="Hello from notify-bridge!",
    msg_type="text"
)
```

### Text with Mentions (@Users)

For text messages, you can mention users using the `mentioned_list` and `mentioned_mobile_list` parameters:

```python
response = bridge.send(
    "wecom",
    webhook_url="YOUR_WEBHOOK_URL",
    message="Important announcement!",
    msg_type="text",
    mentioned_list=["@all"],  # Mention all users
    # Or mention specific users by their WeCom user ID
    # mentioned_list=["user1", "user2"],
    # Or by mobile number
    # mentioned_mobile_list=["13800138000"],
)
```

### Using MentionHelper

The `MentionHelper` class provides convenient methods for building mention syntax:

```python
from notify_bridge.notifiers.wecom import MentionHelper

# Mention a specific user in markdown content
content = f"Hello {MentionHelper.mention_user('zhangsan')}, please review this!"
# Result: "Hello <@zhangsan>, please review this!"

# Mention multiple users
mentions = MentionHelper.mention_users(["user1", "user2", "user3"])
content = f"{mentions} Please check this urgent issue!"
# Result: "<@user1> <@user2> <@user3> Please check this urgent issue!"

# Mention all users
content = f"{MentionHelper.mention_all()} System maintenance scheduled!"
# Result: "<@all> System maintenance scheduled!"

# Get mention parameters for text messages
params = MentionHelper.get_mention_params(
    user_ids=["user1", "user2"],
    mobile_numbers=["13800138000"]
)
# Use with bridge.send()
response = bridge.send(
    "wecom",
    webhook_url="YOUR_WEBHOOK_URL",
    message="Important!",
    msg_type="text",
    **params
)

# Check if content contains mentions
has_mentions = MentionHelper.has_mentions("Hello <@user1>!")  # True
no_mentions = MentionHelper.has_mentions("Hello everyone!")   # False

# Extract user IDs from content
users = MentionHelper.extract_mentions("Hi <@admin> and <@user123>")
# Result: ["admin", "user123"]
```

## Markdown Messages

### Standard Markdown

```python
content = """# Project Update

**Status**: ✅ Completed

## Changes
- Feature A implemented
- Bug B fixed
- Performance improved

> This is a quote

<font color="info">Info message</font>
<font color="warning">Warning message</font>
<font color="comment">Comment</font>
"""

response = bridge.send(
    "wecom",
    webhook_url="YOUR_WEBHOOK_URL",
    message=content,
    msg_type="markdown"
)
```

### Markdown with Mentions (@Users)

In markdown messages, you can use the `<@userid>` syntax to mention specific users directly in the content:

```python
from notify_bridge.notifiers.wecom import MentionHelper

# Using MentionHelper (recommended)
content = f"""# Urgent Review Required

Hi {MentionHelper.mention_user('zhangsan')}, 
please review the deployment request from {MentionHelper.mention_user('lisi')}.

> Priority: High
> Deadline: EOD
"""

response = bridge.send(
    "wecom",
    webhook_url="YOUR_WEBHOOK_URL",
    message=content,
    msg_type="markdown"
)

# Or manually write mention syntax
content = """# Daily Report

<@all> Today's metrics:
- New users: 100
- Active users: 500

Thanks <@manager> for the support!
"""

response = bridge.send(
    "wecom",
    webhook_url="YOUR_WEBHOOK_URL",
    message=content,
    msg_type="markdown"
)
```

::: tip Note on Mentions in Markdown
- Use `<@userid>` syntax to mention users in markdown content
- `mentioned_list` and `mentioned_mobile_list` parameters are **not effective** in markdown mode
- To mention users, include the `<@userid>` syntax directly in your content
:::

### Markdown V2

`markdown_v2` provides enhanced markdown support with better handling of underscores and URLs:

```python
content = """# Markdown V2 Features

## Underscore Handling
_This text has underscores_ that are preserved.

## URLs
[Click here](https://github.com/loonghao/notify-bridge)

## Code
`code_with_underscores`
"""

response = bridge.send(
    "wecom",
    webhook_url="YOUR_WEBHOOK_URL",
    message=content,
    msg_type="markdown_v2"
)
```

::: tip Markdown vs Markdown V2
- Use `markdown` for standard markdown content
- Use `markdown_v2` when your content contains underscores that should be preserved
- In `markdown_v2`, forward slashes in URLs are automatically escaped
:::

::: warning Important: Mentions Not Supported in Markdown V2
**Markdown V2 does NOT support the `<@userid>` mention syntax!** If you need to mention users:
- Use `markdown` message type with `<@userid>` syntax
- Use `text` message type with `mentioned_list` parameter
- Using `<@userid>` in `markdown_v2` will trigger a warning
:::

## Image Messages

```python
response = bridge.send(
    "wecom",
    webhook_url="YOUR_WEBHOOK_URL",
    msg_type="image",
    image_path="/path/to/image.png"  # Local file path
)
```

::: warning Image Requirements
- Supported formats: PNG, JPG
- Maximum size: 2MB
- The image is base64 encoded before sending
:::

## News Messages

```python
response = bridge.send(
    "wecom",
    webhook_url="YOUR_WEBHOOK_URL",
    msg_type="news",
    articles=[
        {
            "title": "Article Title",
            "description": "Article description text",
            "url": "https://example.com/article",
            "picurl": "https://example.com/image.jpg"  # Optional
        },
        {
            "title": "Second Article",
            "description": "Another article",
            "url": "https://example.com/article2"
        }
    ]
)
```

## Template Cards

### Text Notice Card

```python
response = bridge.send(
    "wecom",
    webhook_url="YOUR_WEBHOOK_URL",
    msg_type="template_card",
    template_card_type="text_notice",
    template_card_source={
        "icon_url": "https://example.com/icon.png",
        "desc": "Source Name",
        "desc_color": 0  # 0=grey, 1=black, 2=red, 3=green
    },
    template_card_main_title={
        "title": "Card Title",
        "desc": "Card description"
    },
    template_card_emphasis_content={
        "title": "100%",
        "desc": "Completion Rate"
    },
    template_card_sub_title_text="Additional information",
    template_card_horizontal_content_list=[
        {"keyname": "Status", "value": "Active"},
        {"keyname": "Priority", "value": "High"}
    ],
    template_card_jump_list=[
        {
            "type": 1,
            "url": "https://example.com",
            "title": "View Details"
        }
    ],
    template_card_card_action={
        "type": 1,
        "url": "https://example.com/action"
    }
)
```

### News Notice Card

```python
response = bridge.send(
    "wecom",
    webhook_url="YOUR_WEBHOOK_URL",
    msg_type="template_card",
    template_card_type="news_notice",
    template_card_source={
        "icon_url": "https://example.com/icon.png",
        "desc": "News Source"
    },
    template_card_main_title={
        "title": "Breaking News",
        "desc": "Important update"
    },
    template_card_vertical_content_list=[
        {
            "title": "Headline 1",
            "desc": "Description of headline 1"
        },
        {
            "title": "Headline 2",
            "desc": "Description of headline 2"
        }
    ],
    template_card_card_action={
        "type": 1,
        "url": "https://example.com/news"
    }
)
```

## File and Voice Messages

### File Message

```python
# First upload the file to get media_id
response = bridge.send(
    "wecom",
    webhook_url="YOUR_WEBHOOK_URL",
    msg_type="upload_media",
    media_path="/path/to/document.pdf",
    upload_media_type="file"
)
media_id = response.data["media_id"]

# Then send the file message
response = bridge.send(
    "wecom",
    webhook_url="YOUR_WEBHOOK_URL",
    msg_type="file",
    media_id=media_id
)
```

### Voice Message

```python
# Upload voice file
response = bridge.send(
    "wecom",
    webhook_url="YOUR_WEBHOOK_URL",
    msg_type="upload_media",
    media_path="/path/to/audio.amr",
    upload_media_type="voice"
)
media_id = response.data["media_id"]

# Send voice message
response = bridge.send(
    "wecom",
    webhook_url="YOUR_WEBHOOK_URL",
    msg_type="voice",
    media_id=media_id
)
```

::: warning File Limitations
- File: max 20MB, min 5 bytes
- Voice: max 2MB, AMR format only
:::

## Using WeComNotifier Directly

For more control, you can use the `WeComNotifier` class directly:

```python
from notify_bridge.notifiers.wecom import WeComNotifier, WeComSchema

notifier = WeComNotifier()

# Using dictionary
response = notifier.send({
    "webhook_url": "YOUR_WEBHOOK_URL",
    "msg_type": "text",
    "content": "Hello!"
})

# Using schema
schema = WeComSchema(
    webhook_url="YOUR_WEBHOOK_URL",
    msg_type="markdown",
    content="# Hello\n\nThis is **markdown**."
)
response = notifier.send(schema)
```

## Error Handling

```python
from notify_bridge import NotifyBridge
from notify_bridge.exceptions import NotificationError, ValidationError

bridge = NotifyBridge()

try:
    response = bridge.send(
        "wecom",
        webhook_url="YOUR_WEBHOOK_URL",
        message="Test message",
        msg_type="text"
    )
    
    if response.data.get("errcode") != 0:
        print(f"WeCom API error: {response.data.get('errmsg')}")
        
except ValidationError as e:
    print(f"Validation error: {e}")
except NotificationError as e:
    print(f"Notification error: {e}")
```

## Common Error Codes

| Error Code | Description |
|------------|-------------|
| 0 | Success |
| 40014 | Invalid access_token |
| 40035 | Invalid parameter |
| 45002 | Message content too long |
| 45009 | API call frequency limit exceeded |

## Best Practices

1. **Store webhook URLs securely** - Use environment variables
2. **Handle rate limits** - WeCom has API call frequency limits
3. **Validate content length** - Different message types have different limits
4. **Use appropriate message types** - Choose the right format for your content
5. **Test in development** - Use a test group before production
