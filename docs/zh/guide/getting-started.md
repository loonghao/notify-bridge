# 快速开始

本指南将帮助你开始使用 notify-bridge。

## 前置要求

- Python 3.8 或更高版本
- pip 或 uv 包管理器

## 安装

使用 pip 安装：

```bash
pip install notify-bridge
```

或使用 uv：

```bash
uv pip install notify-bridge
```

## 基本用法

### 创建桥接器实例

```python
from notify_bridge import NotifyBridge

# 创建桥接器实例
bridge = NotifyBridge()

# 列出可用的通知器
print(bridge.notifiers)
```

### 发送简单消息

```python
# 向企业微信发送文本消息
response = bridge.send(
    "wecom",
    webhook_url="YOUR_WEBHOOK_URL",
    message="来自 notify-bridge 的问候！",
    msg_type="text"
)

print(f"成功: {response.success}")
print(f"响应: {response.data}")
```

### 异步支持

notify-bridge 完全支持异步操作：

```python
import asyncio
from notify_bridge import NotifyBridge

async def send_notification():
    bridge = NotifyBridge()
    
    response = await bridge.send_async(
        "wecom",
        webhook_url="YOUR_WEBHOOK_URL",
        message="来自异步 notify-bridge 的问候！",
        msg_type="text"
    )
    
    return response

# 运行异步函数
response = asyncio.run(send_notification())
```

## 环境变量

为了安全起见，建议将 webhook URL 和令牌存储在环境变量中：

```python
import os
from dotenv import load_dotenv
from notify_bridge import NotifyBridge

load_dotenv()

bridge = NotifyBridge()

response = bridge.send(
    "wecom",
    webhook_url=os.getenv("WECOM_WEBHOOK_URL"),
    message="你好！",
    msg_type="text"
)
```

## 下一步

- 了解 [企业微信集成](/zh/guide/wecom)
- 了解 [飞书集成](/zh/guide/feishu)
- 了解 [创建自定义插件](/zh/guide/plugins)
- 探索 [API 参考](/zh/api/core)
