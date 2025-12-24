# Core API

The core API provides the main interface for sending notifications.

## NotifyBridge

The main class for sending notifications to various platforms.

### Constructor

```python
from notify_bridge import NotifyBridge

bridge = NotifyBridge()
```

### Properties

#### notifiers

Returns a dictionary of available notifiers.

```python
bridge.notifiers
# {'feishu': <FeishuNotifier>, 'wecom': <WeComNotifier>, ...}
```

### Methods

#### send()

Send a notification synchronously.

```python
def send(
    self,
    notifier_name: str,
    **kwargs
) -> NotificationResponse
```

**Parameters:**
- `notifier_name` (str): Name of the notifier to use
- `**kwargs`: Notification parameters (varies by platform)

**Returns:** `NotificationResponse`

**Example:**
```python
response = bridge.send(
    "wecom",
    webhook_url="YOUR_URL",
    message="Hello!",
    msg_type="text"
)
```

#### send_async()

Send a notification asynchronously.

```python
async def send_async(
    self,
    notifier_name: str,
    **kwargs
) -> NotificationResponse
```

**Parameters:**
- `notifier_name` (str): Name of the notifier to use
- `**kwargs`: Notification parameters (varies by platform)

**Returns:** `NotificationResponse`

**Example:**
```python
response = await bridge.send_async(
    "wecom",
    webhook_url="YOUR_URL",
    message="Hello!",
    msg_type="text"
)
```

#### get_notifier()

Get a specific notifier instance.

```python
def get_notifier(self, name: str) -> BaseNotifier
```

**Parameters:**
- `name` (str): Name of the notifier

**Returns:** `BaseNotifier` instance

**Raises:** `NoSuchNotifierError` if notifier not found

**Example:**
```python
notifier = bridge.get_notifier("wecom")
```

## NotificationResponse

Response object returned by notification operations.

### Attributes

| Attribute | Type | Description |
|-----------|------|-------------|
| `success` | bool | Whether the notification was sent successfully |
| `name` | str | Name of the notifier used |
| `message` | str | Response message |
| `data` | dict | Response data from the platform |

### Example

```python
response = bridge.send("wecom", ...)

print(response.success)   # True
print(response.name)      # "wecom"
print(response.message)   # "Notification sent successfully"
print(response.data)      # {"errcode": 0, "errmsg": "ok"}
```

## BaseNotifier

Abstract base class for all notifiers.

### Class Attributes

| Attribute | Type | Description |
|-----------|------|-------------|
| `name` | str | Unique identifier for the notifier |
| `schema_class` | Type | Pydantic schema class for validation |
| `supported_types` | set | Set of supported `MessageType` values |
| `http_method` | str | HTTP method for requests (default: "POST") |

### Methods

#### validate()

Validate notification data.

```python
def validate(
    self, 
    data: Union[Dict[str, Any], NotificationSchema]
) -> NotificationSchema
```

#### assemble_data()

Assemble the API payload.

```python
def assemble_data(
    self, 
    data: NotificationSchema
) -> Dict[str, Any]
```

#### send()

Send notification synchronously.

```python
def send(
    self, 
    notification_data: Union[Dict[str, Any], NotificationSchema]
) -> NotificationResponse
```

#### send_async()

Send notification asynchronously.

```python
async def send_async(
    self, 
    notification_data: Union[Dict[str, Any], NotificationSchema]
) -> NotificationResponse
```

#### close()

Close the HTTP client (sync).

```python
def close(self) -> None
```

#### close_async()

Close the HTTP client (async).

```python
async def close_async(self) -> None
```

## MessageType

Enum of supported message types.

```python
from notify_bridge.schema import MessageType

class MessageType(str, Enum):
    TEXT = "text"
    MARKDOWN = "markdown"
    MARKDOWN_V2 = "markdown_v2"
    NEWS = "news"
    POST = "post"
    IMAGE = "image"
    FILE = "file"
    VOICE = "voice"
    INTERACTIVE = "interactive"
    UPLOAD_MEDIA = "upload_media"
    TEMPLATE_CARD = "template_card"
```

## HTTPClientConfig

Configuration for the HTTP client.

```python
from notify_bridge.utils import HTTPClientConfig

config = HTTPClientConfig(
    timeout=30.0,
    verify_ssl=True,
    max_retries=3
)
```

### Attributes

| Attribute | Type | Default | Description |
|-----------|------|---------|-------------|
| `timeout` | float | 30.0 | Request timeout in seconds |
| `verify_ssl` | bool | True | Whether to verify SSL certificates |
| `max_retries` | int | 0 | Maximum number of retries |

## NotifierFactory

Factory for creating notifier instances.

```python
from notify_bridge.factory import NotifierFactory

factory = NotifierFactory()

# Register a custom notifier
factory.register("custom", CustomNotifier)

# Create a notifier instance
notifier = factory.create("wecom")
```

### Methods

#### register()

Register a notifier class.

```python
def register(self, name: str, notifier_class: Type[BaseNotifier]) -> None
```

#### create()

Create a notifier instance.

```python
def create(
    self, 
    name: str, 
    config: Optional[HTTPClientConfig] = None
) -> BaseNotifier
```

#### list_notifiers()

List all registered notifiers.

```python
def list_notifiers(self) -> List[str]
```
