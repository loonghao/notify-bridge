# 错误处理

notify-bridge 提供了全面的异常层次结构，帮助你优雅地处理错误。

## 异常层次结构

```
NotifyBridgeError (基类)
├── ValidationError
├── NotificationError
├── NoSuchNotifierError
├── PluginError
└── ConfigurationError
```

## 异常类型

### NotifyBridgeError

所有 notify-bridge 错误的基类异常。

```python
from notify_bridge.exceptions import NotifyBridgeError

try:
    response = bridge.send(...)
except NotifyBridgeError as e:
    print(f"notify-bridge 错误: {e}")
```

### ValidationError

数据验证失败时抛出。

```python
from notify_bridge.exceptions import ValidationError

try:
    response = bridge.send(
        "wecom",
        webhook_url="invalid-url",
        message="测试",
        msg_type="text"
    )
except ValidationError as e:
    print(f"验证失败: {e}")
```

### NotificationError

发送通知失败时抛出。

```python
from notify_bridge.exceptions import NotificationError

try:
    response = bridge.send(
        "wecom",
        webhook_url="https://invalid.endpoint.com",
        message="测试",
        msg_type="text"
    )
except NotificationError as e:
    print(f"发送通知失败: {e}")
    print(f"通知器: {e.notifier_name}")
```

### NoSuchNotifierError

请求不存在的通知器时抛出。

```python
from notify_bridge.exceptions import NoSuchNotifierError

try:
    response = bridge.send(
        "nonexistent",
        webhook_url="https://example.com",
        message="测试"
    )
except NoSuchNotifierError as e:
    print(f"通知器未找到: {e}")
```

## 全面的错误处理

```python
from notify_bridge import NotifyBridge
from notify_bridge.exceptions import (
    NotifyBridgeError,
    ValidationError,
    NotificationError,
    NoSuchNotifierError,
)

def send_notification(platform: str, **kwargs):
    """带全面错误处理的发送通知。"""
    bridge = NotifyBridge()
    
    try:
        response = bridge.send(platform, **kwargs)
        
        # 检查平台特定的成功状态
        if platform == "wecom" and response.data.get("errcode") != 0:
            print(f"企业微信错误: {response.data.get('errmsg')}")
            return None
            
        return response
        
    except ValidationError as e:
        print(f"无效数据: {e}")
        
    except NoSuchNotifierError as e:
        print(f"未知平台 '{platform}': {e}")
        print(f"可用平台: {list(bridge.notifiers.keys())}")
        
    except NotificationError as e:
        print(f"通过 {e.notifier_name} 发送失败: {e}")
        
    except NotifyBridgeError as e:
        print(f"意外错误: {e}")
        
    return None
```

## 重试逻辑

为瞬时故障实现重试逻辑：

```python
import time
from notify_bridge import NotifyBridge
from notify_bridge.exceptions import NotificationError

def send_with_retry(max_retries: int = 3, delay: float = 1.0, **kwargs):
    """带重试逻辑的发送通知。"""
    bridge = NotifyBridge()
    
    for attempt in range(max_retries):
        try:
            response = bridge.send(**kwargs)
            return response
            
        except NotificationError as e:
            if attempt < max_retries - 1:
                print(f"第 {attempt + 1} 次尝试失败，{delay}秒后重试...")
                time.sleep(delay)
                delay *= 2  # 指数退避
            else:
                print(f"所有 {max_retries} 次尝试都失败了")
                raise
```

## 最佳实践

1. **先捕获特定异常** 再捕获通用异常
2. **记录错误** 用于调试和监控
3. **实现重试逻辑** 处理瞬时故障
4. **检查平台特定的错误码**
5. **向用户提供有意义的错误消息**
