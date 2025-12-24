# Exceptions Reference

This page documents all exceptions in notify-bridge.

## Exception Hierarchy

```
NotifyBridgeError
├── ValidationError
├── NotificationError
├── NoSuchNotifierError
├── PluginError
└── ConfigurationError
```

## NotifyBridgeError

Base exception for all notify-bridge errors.

```python
from notify_bridge.exceptions import NotifyBridgeError

class NotifyBridgeError(Exception):
    """Base exception for notify-bridge."""
    pass
```

### Usage

```python
from notify_bridge.exceptions import NotifyBridgeError

try:
    bridge.send(...)
except NotifyBridgeError as e:
    print(f"Error: {e}")
```

## ValidationError

Raised when data validation fails.

```python
from notify_bridge.exceptions import ValidationError

class ValidationError(NotifyBridgeError):
    """Raised when validation fails."""
    pass
```

### Common Causes

- Missing required fields
- Invalid field types
- Invalid field values
- Schema constraint violations

### Example

```python
from notify_bridge.exceptions import ValidationError

try:
    bridge.send(
        "wecom",
        webhook_url="",  # Empty URL
        msg_type="text"
    )
except ValidationError as e:
    print(f"Validation failed: {e}")
```

## NotificationError

Raised when sending a notification fails.

```python
from notify_bridge.exceptions import NotificationError

class NotificationError(NotifyBridgeError):
    """Raised when notification fails."""
    
    def __init__(
        self, 
        message: str, 
        notifier_name: str = None
    ):
        self.notifier_name = notifier_name
        super().__init__(message)
```

### Attributes

| Attribute | Type | Description |
|-----------|------|-------------|
| `notifier_name` | str | Name of the notifier that failed |

### Common Causes

- Network errors
- Invalid webhook URL
- API rate limits
- Authentication failures
- Server errors

### Example

```python
from notify_bridge.exceptions import NotificationError

try:
    bridge.send(
        "wecom",
        webhook_url="https://invalid.url",
        message="Test",
        msg_type="text"
    )
except NotificationError as e:
    print(f"Notification failed: {e}")
    print(f"Notifier: {e.notifier_name}")
```

## NoSuchNotifierError

Raised when requesting a notifier that doesn't exist.

```python
from notify_bridge.exceptions import NoSuchNotifierError

class NoSuchNotifierError(NotifyBridgeError):
    """Raised when notifier is not found."""
    pass
```

### Common Causes

- Typo in notifier name
- Notifier not installed
- Plugin not registered

### Example

```python
from notify_bridge.exceptions import NoSuchNotifierError

try:
    bridge.send(
        "nonexistent",  # Invalid notifier
        webhook_url="https://example.com"
    )
except NoSuchNotifierError as e:
    print(f"Notifier not found: {e}")
    print(f"Available: {list(bridge.notifiers.keys())}")
```

## PluginError

Raised when there's an issue with plugin loading or registration.

```python
from notify_bridge.exceptions import PluginError

class PluginError(NotifyBridgeError):
    """Raised when plugin loading fails."""
    pass
```

### Common Causes

- Invalid plugin entry point
- Import errors in plugin module
- Missing dependencies
- Invalid plugin class

### Example

```python
from notify_bridge.exceptions import PluginError

try:
    bridge = NotifyBridge()
except PluginError as e:
    print(f"Plugin error: {e}")
```

## ConfigurationError

Raised when there's a configuration issue.

```python
from notify_bridge.exceptions import ConfigurationError

class ConfigurationError(NotifyBridgeError):
    """Raised when configuration is invalid."""
    pass
```

### Common Causes

- Invalid configuration values
- Missing required configuration
- Incompatible settings

### Example

```python
from notify_bridge.exceptions import ConfigurationError

try:
    config = HTTPClientConfig(timeout=-1)  # Invalid timeout
except ConfigurationError as e:
    print(f"Configuration error: {e}")
```

## Best Practices

### Catch Specific Exceptions

```python
from notify_bridge.exceptions import (
    ValidationError,
    NotificationError,
    NoSuchNotifierError,
)

try:
    response = bridge.send(...)
except ValidationError:
    # Handle validation errors
    pass
except NoSuchNotifierError:
    # Handle unknown notifier
    pass
except NotificationError:
    # Handle send failures
    pass
```

### Use Exception Attributes

```python
from notify_bridge.exceptions import NotificationError

try:
    response = bridge.send(...)
except NotificationError as e:
    logger.error(
        f"Failed to send via {e.notifier_name}: {e}",
        exc_info=True
    )
```

### Re-raise with Context

```python
from notify_bridge.exceptions import NotificationError

try:
    response = bridge.send(...)
except NotificationError as e:
    # Add context and re-raise
    raise NotificationError(
        f"Failed to notify user {user_id}: {e}",
        notifier_name=e.notifier_name
    ) from e
```

## Error Codes

### WeCom Error Codes

| Code | Description |
|------|-------------|
| 0 | Success |
| 40014 | Invalid access_token |
| 40035 | Invalid parameter |
| 45002 | Message content too long |
| 45009 | API call frequency limit |

### Feishu Error Codes

| Code | Description |
|------|-------------|
| 0 | Success |
| 19001 | Invalid webhook |
| 19002 | Invalid signature |
| 19003 | Invalid timestamp |

### GitHub Error Codes

| Code | Description |
|------|-------------|
| 401 | Unauthorized |
| 403 | Forbidden |
| 404 | Not found |
| 422 | Validation failed |
