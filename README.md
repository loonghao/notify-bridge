# notify-bridge

<div align="center">

[![Python Version](https://img.shields.io/pypi/pyversions/notify-bridge)](https://img.shields.io/pypi/pyversions/notify-bridge)
[![Nox](https://img.shields.io/badge/%F0%9F%A6%8A-Nox-D85E00.svg)](https://github.com/wntrblm/nox)
[![PyPI Version](https://img.shields.io/pypi/v/notify-bridge?color=green)](https://pypi.org/project/notify-bridge/)
[![Downloads](https://static.pepy.tech/badge/notify-bridge)](https://pepy.tech/project/notify-bridge)
[![Downloads](https://static.pepy.tech/badge/notify-bridge/month)](https://pepy.tech/project/notify-bridge)
[![Downloads](https://static.pepy.tech/badge/notify-bridge/week)](https://pepy.tech/project/notify-bridge)
[![License](https://img.shields.io/pypi/l/notify-bridge)](https://pypi.org/project/notify-bridge/)
[![PyPI Format](https://img.shields.io/pypi/format/notify-bridge)](https://pypi.org/project/notify-bridge/)
[![Maintenance](https://img.shields.io/badge/Maintained%3F-yes-green.svg)](https://github.com/loonghao/notify-bridge/graphs/commit-activity)
![Codecov](https://img.shields.io/codecov/c/github/loonghao/notify-bridge)
</div>

一个灵活的通知桥接器，用于向各种平台发送消息。

## 特性

- 🚀 简单直观的 API
- 🔌 插件系统，方便扩展
- 🔄 同时支持同步和异步操作
- 🛡️ 使用 Pydantic 模型进行类型安全验证
- 📝 丰富的消息格式（文本、Markdown 等）
- 🌐 支持多个平台

## 安装

```bash
pip install notify-bridge
```

## 快速开始

```python
from notify_bridge import NotifyBridge

# 创建桥接器实例
bridge = NotifyBridge()

# 同步发送通知
response = bridge.send(
    "feishu",
    webhook_url="YOUR_WEBHOOK_URL",
    title="测试消息",
    content="来自 notify-bridge 的问候！",
    msg_type="text"
)
print(response)


# 异步发送通知
async def send_async():
    response = await bridge.notify_async(
        "feishu",
        webhook_url="YOUR_WEBHOOK_URL",
        title="异步测试消息",
        content="# 来自 notify-bridge 的问候！\n\n这是一条 **Markdown** 消息。",
        msg_type="post"
    )
    print(response)
```

## 支持的平台

- [x] 飞书 (Feishu)
- [x] 企业微信 (WeCom)
- [ ] 钉钉 (DingTalk)
- [ ] 电子邮件 (Email)
- [ ] Slack
- [ ] Discord

## 使用示例

### 飞书 (Feishu)

```python
# 发送文本消息
bridge.send(
    "feishu",
    webhook_url="YOUR_WEBHOOK_URL",
    content="这是一条文本消息",
    msg_type="text"
)

# 发送富文本消息
bridge.send(
    "feishu",
    webhook_url="YOUR_WEBHOOK_URL",
    title="消息标题",
    content="这是一条富文本消息的内容",
    msg_type="post"
)

# 发送图片消息
bridge.send(
    "feishu",
    webhook_url="YOUR_WEBHOOK_URL",
    image_path="path/to/image.jpg",  # 或者使用 image_key
    msg_type="image"
)

# 发送文件消息
bridge.send(
    "feishu",
    webhook_url="YOUR_WEBHOOK_URL",
    file_path="path/to/document.pdf",  # 或者使用 file_key
    msg_type="file"
)
```

### 企业微信 (WeCom)

```python
# 发送文本消息
bridge.send(
    "wecom",
    webhook_url="YOUR_WEBHOOK_URL",
    content="这是一条文本消息",
    msg_type="text"
)

# 发送 Markdown 消息
bridge.send(
    "wecom",
    webhook_url="YOUR_WEBHOOK_URL",
    content="**粗体文本**\n> 引用\n[链接](https://example.com)",
    msg_type="markdown"
)

# 发送图文消息
bridge.send(
    "wecom",
    webhook_url="YOUR_WEBHOOK_URL",
    title="图文消息标题",
    content="图文消息描述",
    msg_type="news",
    articles=[{
        "title": "文章标题",
        "description": "文章描述",
        "url": "https://example.com",
        "picurl": "https://example.com/image.jpg"
    }]
)
```

## 创建插件

1. 创建通知器类：

```python
from notify_bridge.schema import BaseNotifier, NotificationSchema
from pydantic import Field


class MySchema(NotificationSchema):
    """自定义通知模式。"""
    webhook_url: str = Field(..., description="Webhook URL")
    title: str = Field(None, description="消息标题")
    content: str = Field(..., description="消息内容")
    msg_type: str = Field("text", description="消息类型")


class MyNotifier(BaseNotifier):
    """自定义通知器。"""
    name = "my_notifier"  # 通知器名称
    schema = MySchema  # 通知器模式

    def notify(self, notification: NotificationSchema) -> NotificationResponse:
        """同步发送通知。"""
        # 实现你的通知逻辑
        pass

    async def notify_async(self, notification: NotificationSchema) -> NotificationResponse:
        """异步发送通知。"""
        # 实现你的异步通知逻辑
        pass
```

2. 在 `pyproject.toml` 中注册你的插件：

```toml
[project.entry-points."notify_bridge.notifiers"]
my_notifier = "my_package.my_module:MyNotifier"
```

## 错误处理

```python
from notify_bridge.exceptions import NotificationError, ValidationError

try:
    response = bridge.send(
        "feishu",
        webhook_url="YOUR_WEBHOOK_URL",
        content="测试消息",
        msg_type="text"
    )
except ValidationError as e:
    print(f"验证错误：{e}")
except NotificationError as e:
    print(f"通知错误：{e}")
```

## 环境变量

你可以使用环境变量来存储敏感信息，比如 webhook URL：

```python
# .env
FEISHU_WEBHOOK_URL = https: // open.feishu.cn / open - apis / bot / v2 / hook / xxx
WECOM_WEBHOOK_URL = https: // qyapi.weixin.qq.com / cgi - bin / webhook / send?key = xxx

# Python 代码
import os
from dotenv import load_dotenv

load_dotenv()

bridge.send(
    "feishu",
    webhook_url=os.getenv("FEISHU_WEBHOOK_URL"),
    content="测试消息",
    msg_type="text"
)
```

## 开发指南

1. 克隆仓库：
```bash
git clone https://github.com/loonghao/notify-bridge.git
cd notify-bridge
```

2. 安装依赖：
```bash
pip install -e ".[dev]"
```

3. 运行测试：
```bash
pytest
```

4. 运行代码检查：
```bash
nox
```

## 贡献

欢迎贡献！请随时提交 Pull Request。

1. Fork 仓库
2. 创建你的功能分支：`git checkout -b feature/my-feature`
3. 提交你的更改：`git commit -am 'Add some feature'`
4. 推送到分支：`git push origin feature/my-feature`
5. 提交 Pull Request

## 许可证

本项目基于 MIT 许可证 - 详见 [LICENSE](LICENSE) 文件。
