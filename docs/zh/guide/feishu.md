# 飞书 (Feishu)

飞书是字节跳动推出的协作平台。notify-bridge 提供了对飞书 webhook 通知的支持。

## 支持的消息类型

| 类型 | 描述 |
|------|------|
| `text` | 纯文本消息 |
| `post` | 富文本消息 |
| `image` | 图片消息 |
| `file` | 文件附件 |
| `interactive` | 交互式卡片消息 |

## 获取 Webhook URL

1. 打开飞书，进入群聊
2. 点击群设置（齿轮图标）
3. 选择 **机器人** > **添加机器人** > **自定义机器人**
4. 复制 webhook URL

URL 格式为：
```
https://open.feishu.cn/open-apis/bot/v2/hook/YOUR_KEY
```

## 基本用法

### 文本消息

```python
from notify_bridge import NotifyBridge

bridge = NotifyBridge()

response = bridge.send(
    "feishu",
    webhook_url="YOUR_WEBHOOK_URL",
    content="来自 notify-bridge 的问候！",
    msg_type="text"
)
```

### 富文本消息

```python
response = bridge.send(
    "feishu",
    webhook_url="YOUR_WEBHOOK_URL",
    title="项目更新",
    content="这是富文本消息的主要内容。",
    msg_type="post"
)
```

## 图片消息

```python
response = bridge.send(
    "feishu",
    webhook_url="YOUR_WEBHOOK_URL",
    msg_type="image",
    image_path="/path/to/image.png"
)
```

## 交互式卡片

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
                "content": "卡片标题"
            },
            "template": "blue"
        },
        "elements": [
            {
                "tag": "div",
                "text": {
                    "tag": "lark_md",
                    "content": "**粗体** 和 *斜体* 文本"
                }
            }
        ]
    }
)
```

## 异步支持

```python
import asyncio
from notify_bridge import NotifyBridge

async def send_feishu_notification():
    bridge = NotifyBridge()
    
    response = await bridge.send_async(
        "feishu",
        webhook_url="YOUR_WEBHOOK_URL",
        content="异步消息！",
        msg_type="text"
    )
    
    return response

asyncio.run(send_feishu_notification())
```
