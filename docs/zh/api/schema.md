# Schema 参考

本页记录了用于数据验证的 schema 类。

## 基础 Schema

### NotificationSchema

通知的基础 schema。

```python
from notify_bridge.schema import NotificationSchema

class NotificationSchema(HTTPSchema):
    title: Optional[str] = None    # 消息标题
    content: Optional[str] = None  # 消息内容
    msg_type: str = "text"         # 消息类型
```

### WebhookSchema

基于 webhook 的通知 schema。

```python
from notify_bridge.schema import WebhookSchema

class WebhookSchema(NotificationSchema):
    webhook_url: Optional[str] = None
    title: Optional[str] = None
    content: Optional[str] = None
```

## 平台 Schema

### WeComSchema

企业微信通知 schema。

```python
from notify_bridge.notifiers.wecom import WeComSchema

schema = WeComSchema(
    webhook_url="https://qyapi.weixin.qq.com/...",
    content="消息内容",
    msg_type="text",
    mentioned_list=["@all"],
    mentioned_mobile_list=["13800138000"],
    # ... 更多字段
)
```

#### 字段

| 字段 | 类型 | 描述 |
|------|------|------|
| `webhook_url` | str | 企业微信 webhook URL |
| `content` | str | 消息内容 |
| `msg_type` | str | 消息类型 |
| `mentioned_list` | List[str] | 要提及的用户 |
| `mentioned_mobile_list` | List[str] | 要提及的手机号 |
| `image_path` | str | 图片文件路径 |
| `media_id` | str | 文件/语音的媒体 ID |
| `articles` | List[Dict] | 图文文章 |

## NotificationResponse

通知操作的响应。

```python
from notify_bridge.schema import NotificationResponse

response = NotificationResponse(
    success=True,
    name="wecom",
    message="通知发送成功",
    data={"errcode": 0, "errmsg": "ok"}
)
```

### 字段

| 字段 | 类型 | 描述 |
|------|------|------|
| `success` | bool | 成功状态 |
| `name` | str | 通知器名称 |
| `message` | str | 响应消息 |
| `data` | Dict | 响应数据 |
