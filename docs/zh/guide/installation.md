# 安装

## 要求

- Python 3.8 或更高版本
- pip、uv 或其他 Python 包管理器

## 从 PyPI 安装

推荐从 PyPI 安装 notify-bridge：

```bash
pip install notify-bridge
```

或使用 uv（更快）：

```bash
uv pip install notify-bridge
```

## 从源码安装

从源码安装用于开发：

```bash
# 克隆仓库
git clone https://github.com/loonghao/notify-bridge.git
cd notify-bridge

# 以开发模式安装
pip install -e ".[dev]"
```

## 依赖

notify-bridge 有以下自动安装的依赖：

| 包 | 版本 | 描述 |
|---|------|------|
| anyio | >=4.0.0 | 异步 I/O 支持 |
| httpx | >=0.26.0 | HTTP 客户端 |
| pydantic | >=2.5.3 | 数据验证 |
| pillow | >=10.0.0 | 图像处理 |
| aiofiles | >=23.2.1 | 异步文件操作 |

## 验证安装

安装后，验证是否正常工作：

```python
from notify_bridge import NotifyBridge

bridge = NotifyBridge()
print(f"可用的通知器: {list(bridge.notifiers.keys())}")
```

预期输出：
```
可用的通知器: ['feishu', 'wecom', 'github', 'notify']
```
