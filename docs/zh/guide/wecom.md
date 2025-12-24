# 企业微信 (WeCom)

企业微信是中国流行的企业通讯平台。notify-bridge 提供了对企业微信 webhook 通知的全面支持。

## 支持的消息类型

| 类型 | 描述 |
|------|------|
| `text` | 纯文本消息 |
| `markdown` | 标准 markdown 格式 |
| `markdown_v2` | 增强的 markdown，更好地处理下划线 |
| `image` | 图片消息（base64 编码） |
| `news` | 图文卡片 |
| `file` | 文件附件 |
| `voice` | 语音消息 |
| `template_card` | 丰富的模板卡片 |

## 获取 Webhook URL

1. 打开企业微信管理后台
2. 导航到 **应用管理** > **群机器人**
3. 创建新机器人或选择现有机器人
4. 复制 webhook URL

URL 格式为：
```
https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key=YOUR_KEY
```

## 基本用法

### 文本消息

```python
from notify_bridge import NotifyBridge

bridge = NotifyBridge()

response = bridge.send(
    "wecom",
    webhook_url="YOUR_WEBHOOK_URL",
    message="来自 notify-bridge 的问候！",
    msg_type="text"
)
```

### 带 @ 提及的文本

```python
response = bridge.send(
    "wecom",
    webhook_url="YOUR_WEBHOOK_URL",
    message="重要公告！",
    msg_type="text",
    mentioned_list=["@all"],  # 提及所有人
    # 或通过企业微信用户 ID 提及特定用户
    # mentioned_list=["user1", "user2"],
    # 或通过手机号
    # mentioned_mobile_list=["13800138000"],
)
```

## Markdown 消息

### 标准 Markdown

```python
content = """# 项目更新

**状态**: ✅ 已完成

## 变更
- 功能 A 已实现
- Bug B 已修复
- 性能已优化

> 这是一段引用

<font color="info">信息提示</font>
<font color="warning">警告提示</font>
<font color="comment">备注</font>
"""

response = bridge.send(
    "wecom",
    webhook_url="YOUR_WEBHOOK_URL",
    message=content,
    msg_type="markdown"
)
```

### Markdown V2

`markdown_v2` 提供增强的 markdown 支持，更好地处理下划线和 URL：

```python
content = """# Markdown V2 特性

## 下划线处理
_这段文本有下划线_ 会被保留。

## URL
[点击这里](https://github.com/loonghao/notify-bridge)

## 代码
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
- 对于标准 markdown 内容使用 `markdown`
- 当内容包含需要保留的下划线时使用 `markdown_v2`
- 在 `markdown_v2` 中，URL 中的斜杠会自动转义
:::

## 图片消息

```python
response = bridge.send(
    "wecom",
    webhook_url="YOUR_WEBHOOK_URL",
    msg_type="image",
    image_path="/path/to/image.png"  # 本地文件路径
)
```

## 图文消息

```python
response = bridge.send(
    "wecom",
    webhook_url="YOUR_WEBHOOK_URL",
    msg_type="news",
    articles=[
        {
            "title": "文章标题",
            "description": "文章描述",
            "url": "https://example.com/article",
            "picurl": "https://example.com/image.jpg"  # 可选
        }
    ]
)
```

## 模板卡片

### 文本通知卡片

```python
response = bridge.send(
    "wecom",
    webhook_url="YOUR_WEBHOOK_URL",
    msg_type="template_card",
    template_card_type="text_notice",
    template_card_source={
        "icon_url": "https://example.com/icon.png",
        "desc": "来源名称",
        "desc_color": 0  # 0=灰色, 1=黑色, 2=红色, 3=绿色
    },
    template_card_main_title={
        "title": "卡片标题",
        "desc": "卡片描述"
    },
    template_card_emphasis_content={
        "title": "100%",
        "desc": "完成率"
    },
    template_card_sub_title_text="附加信息",
    template_card_horizontal_content_list=[
        {"keyname": "状态", "value": "活跃"},
        {"keyname": "优先级", "value": "高"}
    ],
    template_card_jump_list=[
        {
            "type": 1,
            "url": "https://example.com",
            "title": "查看详情"
        }
    ],
    template_card_card_action={
        "type": 1,
        "url": "https://example.com/action"
    }
)
```

## 错误处理

```python
from notify_bridge import NotifyBridge
from notify_bridge.exceptions import NotificationError, ValidationError

bridge = NotifyBridge()

try:
    response = bridge.send(
        "wecom",
        webhook_url="YOUR_WEBHOOK_URL",
        message="测试消息",
        msg_type="text"
    )
    
    if response.data.get("errcode") != 0:
        print(f"企业微信 API 错误: {response.data.get('errmsg')}")
        
except ValidationError as e:
    print(f"验证错误: {e}")
except NotificationError as e:
    print(f"通知错误: {e}")
```

## 常见错误码

| 错误码 | 描述 |
|--------|------|
| 0 | 成功 |
| 40014 | 无效的 access_token |
| 40035 | 无效的参数 |
| 45002 | 消息内容过长 |
| 45009 | API 调用频率超限 |
