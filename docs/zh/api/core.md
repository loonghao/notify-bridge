# 核心 API

核心 API 提供了发送通知的主要接口。

## NotifyBridge

发送通知到各种平台的主类。

### 构造函数

```python
from notify_bridge import NotifyBridge

bridge = NotifyBridge()
```

### 属性

#### notifiers

返回可用通知器的字典。

```python
bridge.notifiers
# {'feishu': <FeishuNotifier>, 'wecom': <WeComNotifier>, ...}
```

### 方法

#### send()

同步发送通知。

```python
def send(
    self,
    notifier_name: str,
    **kwargs
) -> NotificationResponse
```

**参数:**
- `notifier_name` (str): 要使用的通知器名称
- `**kwargs`: 通知参数（因平台而异）

**返回:** `NotificationResponse`

**示例:**
```python
response = bridge.send(
    "wecom",
    webhook_url="YOUR_URL",
    message="你好！",
    msg_type="text"
)
```

#### send_async()

异步发送通知。

```python
async def send_async(
    self,
    notifier_name: str,
    **kwargs
) -> NotificationResponse
```

**参数:**
- `notifier_name` (str): 要使用的通知器名称
- `**kwargs`: 通知参数（因平台而异）

**返回:** `NotificationResponse`

**示例:**
```python
response = await bridge.send_async(
    "wecom",
    webhook_url="YOUR_URL",
    message="你好！",
    msg_type="text"
)
```

## NotificationResponse

通知操作返回的响应对象。

### 属性

| 属性 | 类型 | 描述 |
|------|------|------|
| `success` | bool | 通知是否发送成功 |
| `name` | str | 使用的通知器名称 |
| `message` | str | 响应消息 |
| `data` | dict | 平台返回的响应数据 |

### 示例

```python
response = bridge.send("wecom", ...)

print(response.success)   # True
print(response.name)      # "wecom"
print(response.message)   # "Notification sent successfully"
print(response.data)      # {"errcode": 0, "errmsg": "ok"}
```

## MessageType

支持的消息类型枚举。

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
