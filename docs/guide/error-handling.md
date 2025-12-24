# Error Handling

notify-bridge provides a comprehensive exception hierarchy to help you handle errors gracefully.

## Exception Hierarchy

```
NotifyBridgeError (base)
├── ValidationError
├── NotificationError
├── NoSuchNotifierError
├── PluginError
└── ConfigurationError
```

## Exception Types

### NotifyBridgeError

The base exception for all notify-bridge errors.

```python
from notify_bridge.exceptions import NotifyBridgeError

try:
    # Any notify-bridge operation
    response = bridge.send(...)
except NotifyBridgeError as e:
    print(f"notify-bridge error: {e}")
```

### ValidationError

Raised when data validation fails.

```python
from notify_bridge.exceptions import ValidationError

try:
    response = bridge.send(
        "wecom",
        webhook_url="invalid-url",  # Invalid URL format
        message="Test",
        msg_type="text"
    )
except ValidationError as e:
    print(f"Validation failed: {e}")
```

### NotificationError

Raised when sending a notification fails.

```python
from notify_bridge.exceptions import NotificationError

try:
    response = bridge.send(
        "wecom",
        webhook_url="https://invalid.endpoint.com",
        message="Test",
        msg_type="text"
    )
except NotificationError as e:
    print(f"Failed to send notification: {e}")
    print(f"Notifier: {e.notifier_name}")  # Access notifier name
```

### NoSuchNotifierError

Raised when requesting a notifier that doesn't exist.

```python
from notify_bridge.exceptions import NoSuchNotifierError

try:
    response = bridge.send(
        "nonexistent",  # This notifier doesn't exist
        webhook_url="https://example.com",
        message="Test"
    )
except NoSuchNotifierError as e:
    print(f"Notifier not found: {e}")
```

### PluginError

Raised when there's an issue with plugin loading or registration.

```python
from notify_bridge.exceptions import PluginError

try:
    bridge = NotifyBridge()
except PluginError as e:
    print(f"Plugin error: {e}")
```

### ConfigurationError

Raised when there's a configuration issue.

```python
from notify_bridge.exceptions import ConfigurationError

try:
    # Configuration-related operation
    ...
except ConfigurationError as e:
    print(f"Configuration error: {e}")
```

## Comprehensive Error Handling

Here's a complete example of handling all error types:

```python
from notify_bridge import NotifyBridge
from notify_bridge.exceptions import (
    NotifyBridgeError,
    ValidationError,
    NotificationError,
    NoSuchNotifierError,
    PluginError,
    ConfigurationError,
)

def send_notification(platform: str, **kwargs):
    """Send notification with comprehensive error handling."""
    bridge = NotifyBridge()
    
    try:
        response = bridge.send(platform, **kwargs)
        
        # Check platform-specific success
        if platform == "wecom" and response.data.get("errcode") != 0:
            print(f"WeCom error: {response.data.get('errmsg')}")
            return None
            
        return response
        
    except ValidationError as e:
        print(f"Invalid data: {e}")
        # Log validation errors for debugging
        
    except NoSuchNotifierError as e:
        print(f"Unknown platform '{platform}': {e}")
        # Suggest available platforms
        print(f"Available: {list(bridge.notifiers.keys())}")
        
    except NotificationError as e:
        print(f"Failed to send via {e.notifier_name}: {e}")
        # Implement retry logic or fallback
        
    except ConfigurationError as e:
        print(f"Configuration issue: {e}")
        # Check configuration
        
    except PluginError as e:
        print(f"Plugin issue: {e}")
        # Check plugin installation
        
    except NotifyBridgeError as e:
        print(f"Unexpected error: {e}")
        # Generic fallback
        
    return None
```

## Async Error Handling

Error handling works the same way for async operations:

```python
import asyncio
from notify_bridge import NotifyBridge
from notify_bridge.exceptions import NotificationError

async def send_async_notification():
    bridge = NotifyBridge()
    
    try:
        response = await bridge.send_async(
            "wecom",
            webhook_url="YOUR_WEBHOOK_URL",
            message="Test",
            msg_type="text"
        )
        return response
        
    except NotificationError as e:
        print(f"Async notification failed: {e}")
        return None

asyncio.run(send_async_notification())
```

## Retry Logic

Implement retry logic for transient failures:

```python
import time
from notify_bridge import NotifyBridge
from notify_bridge.exceptions import NotificationError

def send_with_retry(max_retries: int = 3, delay: float = 1.0, **kwargs):
    """Send notification with retry logic."""
    bridge = NotifyBridge()
    
    for attempt in range(max_retries):
        try:
            response = bridge.send(**kwargs)
            return response
            
        except NotificationError as e:
            if attempt < max_retries - 1:
                print(f"Attempt {attempt + 1} failed, retrying in {delay}s...")
                time.sleep(delay)
                delay *= 2  # Exponential backoff
            else:
                print(f"All {max_retries} attempts failed")
                raise
```

## Logging Errors

Integrate with Python logging:

```python
import logging
from notify_bridge import NotifyBridge
from notify_bridge.exceptions import NotifyBridgeError

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def send_notification(**kwargs):
    bridge = NotifyBridge()
    
    try:
        response = bridge.send(**kwargs)
        logger.info(f"Notification sent successfully: {response.name}")
        return response
        
    except NotifyBridgeError as e:
        logger.error(f"Notification failed: {e}", exc_info=True)
        raise
```

## Best Practices

1. **Catch specific exceptions** before generic ones
2. **Log errors** for debugging and monitoring
3. **Implement retry logic** for transient failures
4. **Check platform-specific error codes** in the response
5. **Provide meaningful error messages** to users
6. **Use async error handling** for async operations
