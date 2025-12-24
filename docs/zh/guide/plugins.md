# 创建插件

notify-bridge 使用插件系统，允许你轻松添加对新通知平台的支持。

## 插件架构

每个通知器插件包含：
1. **Schema 类** - 定义数据结构和验证
2. **Notifier 类** - 实现通知逻辑

## 创建自定义通知器

### 步骤 1：定义 Schema

```python
from typing import Optional, List
from pydantic import Field
from notify_bridge.schema import WebhookSchema

class MyPlatformSchema(WebhookSchema):
    """MyPlatform 通知 Schema。"""
    
    webhook_url: str = Field(..., description="Webhook URL")
    content: Optional[str] = Field(None, description="消息内容")
    title: Optional[str] = Field(None, description="消息标题")
    tags: Optional[List[str]] = Field(default_factory=list, description="消息标签")
    
    class Config:
        populate_by_name = True
```

### 步骤 2：实现 Notifier

```python
from typing import Any, ClassVar, Dict, Optional, Union

from notify_bridge.components import BaseNotifier, HTTPClientConfig, MessageType
from notify_bridge.schema import NotificationResponse

class MyPlatformNotifier(BaseNotifier):
    """MyPlatform 通知器实现。"""
    
    name = "myplatform"  # 唯一标识符
    schema_class = MyPlatformSchema
    supported_types: ClassVar[set[MessageType]] = {
        MessageType.TEXT,
        MessageType.MARKDOWN,
    }
    
    def __init__(self, config: Optional[HTTPClientConfig] = None) -> None:
        super().__init__(config)
    
    def assemble_data(self, data: MyPlatformSchema) -> Dict[str, Any]:
        """组装 API 负载。"""
        return {
            "content": data.content,
            "title": data.title,
            "tags": data.tags,
        }
```

### 步骤 3：注册插件

在 `pyproject.toml` 中添加入口点：

```toml
[project.entry-points."notify_bridge.notifiers"]
myplatform = "my_package.notifiers:MyPlatformNotifier"
```

## 使用自定义通知器

注册后，可以像其他通知器一样使用：

```python
from notify_bridge import NotifyBridge

bridge = NotifyBridge()

response = bridge.send(
    "myplatform",
    webhook_url="https://api.myplatform.com/webhook",
    title="警报",
    content="发生了一些事情！",
    tags=["alert", "production"]
)
```

## 最佳实践

1. **使用描述性名称** 作为通知器标识
2. **验证所有必需字段** 在 schema 中
3. **优雅地处理错误** 并提供有意义的消息
4. **编写全面的测试** 覆盖你的插件
5. **详细记录你的插件**
6. **遵循 notify-bridge 中的现有模式**
