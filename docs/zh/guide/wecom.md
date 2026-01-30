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

### 带 @ 人的文本消息

对于文本消息，您可以使用 `mentioned_list` 和 `mentioned_mobile_list` 参数来 @ 人：

```python
response = bridge.send(
    "wecom",
    webhook_url="YOUR_WEBHOOK_URL",
    message="重要公告！",
    msg_type="text",
    mentioned_list=["@all"],  # @ 所有人
    # 或通过企业微信用户 ID @ 特定用户
    # mentioned_list=["user1", "user2"],
    # 或通过手机号
    # mentioned_mobile_list=["13800138000"],
)
```

### 使用 MentionHelper

`MentionHelper` 类提供了便捷的 @ 人语法构建方法：

```python
from notify_bridge.notifiers.wecom import MentionHelper

# 在 Markdown 内容中 @ 特定用户
content = f"你好 {MentionHelper.mention_user('zhangsan')}，请审阅这个！"
# 结果："你好 <@zhangsan>，请审阅这个！"

# @ 多个用户
mentions = MentionHelper.mention_users(["user1", "user2", "user3"])
content = f"{mentions} 请检查这个紧急问题！"
# 结果："<@user1> <@user2> <@user3> 请检查这个紧急问题！"

# @ 所有人
content = f"{MentionHelper.mention_all()} 系统维护通知！"
# 结果："<@all> 系统维护通知！"

# 获取文本消息的 @ 人参数
params = MentionHelper.get_mention_params(
    user_ids=["user1", "user2"],
    mobile_numbers=["13800138000"]
)
# 配合 bridge.send() 使用
response = bridge.send(
    "wecom",
    webhook_url="YOUR_WEBHOOK_URL",
    message="重要通知！",
    msg_type="text",
    **params
)

# 检查内容是否包含 @ 人
has_mentions = MentionHelper.has_mentions("你好 <@user1>！")  # True
no_mentions = MentionHelper.has_mentions("大家好！")   # False

# 从内容中提取用户 ID
users = MentionHelper.extract_mentions("嗨 <@admin> 和 <@user123>")
# 结果：["admin", "user123"]
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

### Markdown 中 @ 人

在 Markdown 消息中，您可以使用 `<@userid>` 语法在内容中直接 @ 特定用户：

```python
from notify_bridge.notifiers.wecom import MentionHelper

# 使用 MentionHelper（推荐）
content = f"""# 紧急审阅请求

你好 {MentionHelper.mention_user('zhangsan')}，
请审阅来自 {MentionHelper.mention_user('lisi')} 的部署请求。

> 优先级：高
> 截止时间：今天下班前
"""

response = bridge.send(
    "wecom",
    webhook_url="YOUR_WEBHOOK_URL",
    message=content,
    msg_type="markdown"
)

# 或者手动编写 @ 人语法
content = """# 每日报告

<@all> 今日数据：
- 新用户：100
- 活跃用户：500

感谢 <@manager> 的支持！
"""

response = bridge.send(
    "wecom",
    webhook_url="YOUR_WEBHOOK_URL",
    message=content,
    msg_type="markdown"
)
```

::: tip Markdown 中 @ 人说明
- 使用 `<@userid>` 语法在 Markdown 内容中 @ 人
- `mentioned_list` 和 `mentioned_mobile_list` 参数在 Markdown 模式下**无效**
- 要 @ 人，请直接在内容中包含 `<@userid>` 语法
:::

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

::: warning 重要：Markdown V2 不支持 @ 人
**Markdown V2 不支持 `<@userid>` @ 人语法！** 如果您需要 @ 人：
- 使用 `markdown` 消息类型配合 `<@userid>` 语法
- 使用 `text` 消息类型配合 `mentioned_list` 参数
- 在 `markdown_v2` 中使用 `<@userid>` 会触发警告
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
