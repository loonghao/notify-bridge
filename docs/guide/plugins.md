# Creating Plugins

notify-bridge uses a plugin system that allows you to easily add support for new notification platforms.

## Plugin Architecture

Each notifier plugin consists of:
1. A **Schema class** - Defines the data structure and validation
2. A **Notifier class** - Implements the notification logic

## Creating a Custom Notifier

### Step 1: Define the Schema

```python
from typing import Optional, List
from pydantic import Field
from notify_bridge.schema import WebhookSchema

class MyPlatformSchema(WebhookSchema):
    """Schema for MyPlatform notifications."""
    
    webhook_url: str = Field(..., description="Webhook URL")
    content: Optional[str] = Field(None, description="Message content")
    title: Optional[str] = Field(None, description="Message title")
    tags: Optional[List[str]] = Field(default_factory=list, description="Message tags")
    
    class Config:
        populate_by_name = True
```

### Step 2: Implement the Notifier

```python
from typing import Any, ClassVar, Dict, Optional, Union

from notify_bridge.components import BaseNotifier, HTTPClientConfig, MessageType
from notify_bridge.schema import NotificationResponse

class MyPlatformNotifier(BaseNotifier):
    """MyPlatform notifier implementation."""
    
    name = "myplatform"  # Unique identifier
    schema_class = MyPlatformSchema
    supported_types: ClassVar[set[MessageType]] = {
        MessageType.TEXT,
        MessageType.MARKDOWN,
    }
    
    def __init__(self, config: Optional[HTTPClientConfig] = None) -> None:
        super().__init__(config)
    
    def assemble_data(self, data: MyPlatformSchema) -> Dict[str, Any]:
        """Assemble the API payload."""
        return {
            "content": data.content,
            "title": data.title,
            "tags": data.tags,
        }
```

### Step 3: Register the Plugin

Add an entry point in your `pyproject.toml`:

```toml
[project.entry-points."notify_bridge.notifiers"]
myplatform = "my_package.notifiers:MyPlatformNotifier"
```

## Complete Example

Here's a complete example of a custom notifier:

```python
"""Custom notifier for MyPlatform."""

from typing import Any, ClassVar, Dict, List, Optional, Union

from pydantic import Field

from notify_bridge.components import BaseNotifier, HTTPClientConfig, MessageType
from notify_bridge.exceptions import NotificationError
from notify_bridge.schema import NotificationResponse, WebhookSchema


class MyPlatformSchema(WebhookSchema):
    """Schema for MyPlatform notifications."""
    
    webhook_url: str = Field(..., description="Webhook URL")
    content: Optional[str] = Field(None, description="Message content")
    title: Optional[str] = Field(None, description="Message title")
    priority: str = Field("normal", description="Message priority")
    tags: Optional[List[str]] = Field(default_factory=list, description="Tags")
    
    class Config:
        populate_by_name = True


class MyPlatformNotifier(BaseNotifier):
    """MyPlatform notifier implementation."""
    
    name = "myplatform"
    schema_class = MyPlatformSchema
    supported_types: ClassVar[set[MessageType]] = {
        MessageType.TEXT,
        MessageType.MARKDOWN,
    }
    
    def __init__(self, config: Optional[HTTPClientConfig] = None) -> None:
        super().__init__(config)
    
    def validate(self, data: Union[Dict[str, Any], MyPlatformSchema]) -> MyPlatformSchema:
        """Validate notification data."""
        notification = super().validate(data)
        
        if not notification.content:
            raise NotificationError("content is required")
        
        return notification
    
    def assemble_data(self, data: MyPlatformSchema) -> Dict[str, Any]:
        """Assemble the API payload."""
        payload = {
            "message": {
                "content": data.content,
                "priority": data.priority,
            }
        }
        
        if data.title:
            payload["message"]["title"] = data.title
        
        if data.tags:
            payload["message"]["tags"] = data.tags
        
        return payload
```

## Using Your Custom Notifier

Once registered, you can use it like any other notifier:

```python
from notify_bridge import NotifyBridge

bridge = NotifyBridge()

response = bridge.send(
    "myplatform",
    webhook_url="https://api.myplatform.com/webhook",
    title="Alert",
    content="Something happened!",
    priority="high",
    tags=["alert", "production"]
)
```

## Advanced Features

### Custom HTTP Methods

Override `get_http_method()` for non-POST requests:

```python
class MyNotifier(BaseNotifier):
    http_method = "PUT"  # Default is POST
    
    def get_http_method(self) -> str:
        return self.http_method
```

### Custom Request Parameters

Override `prepare_request_params()` for custom request handling:

```python
def prepare_request_params(
    self, 
    notification: NotificationSchema, 
    payload: Dict[str, Any]
) -> Dict[str, Any]:
    params = super().prepare_request_params(notification, payload)
    
    # Add custom headers
    params["headers"]["X-Custom-Header"] = "value"
    
    return params
```

### Async Support

The base class provides async support automatically. You can override for custom behavior:

```python
async def send_async(
    self, 
    notification_data: Union[Dict[str, Any], MyPlatformSchema]
) -> NotificationResponse:
    # Custom async logic
    notification = self.validate(notification_data)
    
    # Your custom async implementation
    ...
    
    return NotificationResponse(
        success=True,
        name=self.name,
        message="Sent successfully",
        data={"status": "ok"}
    )
```

## Testing Your Plugin

```python
import pytest
from my_package.notifiers import MyPlatformNotifier, MyPlatformSchema

def test_notifier_initialization():
    notifier = MyPlatformNotifier()
    assert notifier.name == "myplatform"

def test_payload_assembly():
    notifier = MyPlatformNotifier()
    schema = MyPlatformSchema(
        webhook_url="https://example.com",
        content="Test message",
        title="Test"
    )
    
    payload = notifier.assemble_data(schema)
    
    assert payload["message"]["content"] == "Test message"
    assert payload["message"]["title"] == "Test"
```

## Best Practices

1. **Use descriptive names** for your notifier
2. **Validate all required fields** in the schema
3. **Handle errors gracefully** with meaningful messages
4. **Write comprehensive tests** for your plugin
5. **Document your plugin** thoroughly
6. **Follow the existing patterns** in notify-bridge
