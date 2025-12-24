# Schema Reference

This page documents the schema classes used for data validation.

## Base Schemas

### BaseSchema

The base schema for all data schemas.

```python
from notify_bridge.schema import BaseSchema

class BaseSchema(BaseModel):
    """Base schema with extra fields allowed."""
    
    model_config = {"extra": "allow", "populate_by_name": True}
    
    def to_payload(self) -> Dict[str, Any]:
        """Convert schema to payload dictionary."""
```

### HTTPSchema

Schema for HTTP-based operations.

```python
from notify_bridge.schema import HTTPSchema

class HTTPSchema(BaseSchema):
    url: str              # HTTP URL
    method: str = "POST"  # HTTP method
    headers: Dict = {}    # HTTP headers
    timeout: float = None # Request timeout
    verify_ssl: bool = True
```

### NotificationSchema

Base schema for notifications.

```python
from notify_bridge.schema import NotificationSchema

class NotificationSchema(HTTPSchema):
    title: Optional[str] = None    # Message title
    content: Optional[str] = None  # Message content
    msg_type: str = "text"         # Message type
```

### WebhookSchema

Schema for webhook-based notifications.

```python
from notify_bridge.schema import WebhookSchema

class WebhookSchema(NotificationSchema):
    webhook_url: Optional[str] = None
    title: Optional[str] = None
    content: Optional[str] = None
```

## Platform Schemas

### WeComSchema

Schema for WeCom notifications.

```python
from notify_bridge.notifiers.wecom import WeComSchema

schema = WeComSchema(
    webhook_url="https://qyapi.weixin.qq.com/...",
    content="Message content",
    msg_type="text",
    mentioned_list=["@all"],
    mentioned_mobile_list=["13800138000"],
    image_path="/path/to/image.png",
    media_id="media_id",
    media_path="/path/to/file",
    articles=[{"title": "...", "url": "..."}],
    color_map={"info": "blue"},
    upload_media_type="file",
    # Template card fields
    template_card_type="text_notice",
    template_card_source={...},
    template_card_main_title={...},
    # ... more template card fields
)
```

#### Fields

| Field | Type | Description |
|-------|------|-------------|
| `webhook_url` | str | WeCom webhook URL |
| `content` | str | Message content |
| `msg_type` | str | Message type |
| `mentioned_list` | List[str] | Users to mention |
| `mentioned_mobile_list` | List[str] | Mobile numbers to mention |
| `image_path` | str | Path to image file |
| `media_id` | str | Media ID for file/voice |
| `media_path` | str | Path to media file |
| `articles` | List[Dict] | News articles |
| `color_map` | Dict | Color mapping for markdown |
| `upload_media_type` | str | Media type (file/voice) |

#### Template Card Fields

| Field | Type | Description |
|-------|------|-------------|
| `template_card_type` | str | Card type (text_notice/news_notice) |
| `template_card_source` | Dict | Source information |
| `template_card_main_title` | Dict | Main title |
| `template_card_emphasis_content` | Dict | Emphasis content |
| `template_card_quote_area` | Dict | Quote area |
| `template_card_sub_title_text` | str | Sub title text |
| `template_card_horizontal_content_list` | List | Horizontal content |
| `template_card_jump_list` | List | Jump links |
| `template_card_card_action` | Dict | Card action |
| `template_card_image` | Dict | Card image (news_notice) |
| `template_card_image_text_area` | Dict | Image text area |
| `template_card_vertical_content_list` | List | Vertical content |

### FeishuSchema

Schema for Feishu notifications.

```python
from notify_bridge.notifiers.feishu import FeishuSchema

schema = FeishuSchema(
    webhook_url="https://open.feishu.cn/...",
    content="Message content",
    title="Message title",
    msg_type="text",
    image_path="/path/to/image.png",
    image_key="img_xxx",
    file_path="/path/to/file",
    file_key="file_xxx",
    card={...},  # Interactive card
)
```

### GitHubSchema

Schema for GitHub notifications.

```python
from notify_bridge.notifiers.github import GitHubSchema

schema = GitHubSchema(
    owner="username",
    repo="repository",
    token="github_token",
    title="Issue title",
    message="Issue body",
    labels=["bug", "help wanted"],
    msg_type="text"
)
```

## Template Card Schemas

### TemplateCardSource

```python
from notify_bridge.notifiers.wecom import TemplateCardSource

source = TemplateCardSource(
    icon_url="https://example.com/icon.png",
    desc="Source description",
    desc_color=0  # 0=grey, 1=black, 2=red, 3=green
)
```

### TemplateCardMainTitle

```python
from notify_bridge.notifiers.wecom import TemplateCardMainTitle

title = TemplateCardMainTitle(
    title="Main title",
    desc="Description"
)
```

### TemplateCardEmphasisContent

```python
from notify_bridge.notifiers.wecom import TemplateCardEmphasisContent

emphasis = TemplateCardEmphasisContent(
    title="100",
    desc="Data meaning"
)
```

### TemplateCardQuoteArea

```python
from notify_bridge.notifiers.wecom import TemplateCardQuoteArea

quote = TemplateCardQuoteArea(
    type=1,  # 0=no click, 1=url, 2=mini program
    url="https://example.com",
    title="Quote title",
    quote_text="Quote text"
)
```

### TemplateCardHorizontalContentItem

```python
from notify_bridge.notifiers.wecom import TemplateCardHorizontalContentItem

item = TemplateCardHorizontalContentItem(
    keyname="Key",
    value="Value",
    type=1,  # 1=url, 2=file, 3=userid
    url="https://example.com"
)
```

### TemplateCardJumpItem

```python
from notify_bridge.notifiers.wecom import TemplateCardJumpItem

jump = TemplateCardJumpItem(
    type=1,  # 1=url, 2=mini program
    title="Jump title",
    url="https://example.com"
)
```

### TemplateCardAction

```python
from notify_bridge.notifiers.wecom import TemplateCardAction

action = TemplateCardAction(
    type=1,  # 1=url, 2=mini program
    url="https://example.com"
)
```

### TemplateCardImage

```python
from notify_bridge.notifiers.wecom import TemplateCardImage

image = TemplateCardImage(
    url="https://example.com/image.png",
    aspect_ratio=2.25
)
```

### TemplateCardImageTextArea

```python
from notify_bridge.notifiers.wecom import TemplateCardImageTextArea

area = TemplateCardImageTextArea(
    type=1,
    url="https://example.com",
    title="Title",
    desc="Description",
    image_url="https://example.com/image.png"
)
```

### TemplateCardVerticalContentItem

```python
from notify_bridge.notifiers.wecom import TemplateCardVerticalContentItem

item = TemplateCardVerticalContentItem(
    title="Title",
    desc="Description"
)
```

## NotificationResponse

Response from notification operations.

```python
from notify_bridge.schema import NotificationResponse

response = NotificationResponse(
    success=True,
    name="wecom",
    message="Notification sent successfully",
    data={"errcode": 0, "errmsg": "ok"}
)
```

### Fields

| Field | Type | Description |
|-------|------|-------------|
| `success` | bool | Success status |
| `name` | str | Notifier name |
| `message` | str | Response message |
| `data` | Dict | Response data |

## AuthSchema

Schema for authentication.

```python
from notify_bridge.schema import AuthSchema, AuthType

auth = AuthSchema(
    auth_type=AuthType.BEARER,
    token="your_token"
)

# Convert to headers
headers = auth.to_headers()
# {"Authorization": "Bearer your_token"}
```

### AuthType

```python
class AuthType(str, Enum):
    NONE = "none"
    BASIC = "basic"
    BEARER = "bearer"
    OAUTH = "oauth"
    API_KEY = "api_key"
    CUSTOM = "custom"
```
