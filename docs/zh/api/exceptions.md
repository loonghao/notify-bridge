# 异常参考

本页记录了 notify-bridge 中的所有异常。

## 异常层次结构

```
NotifyBridgeError
├── ValidationError
├── NotificationError
├── NoSuchNotifierError
├── PluginError
└── ConfigurationError
```

## NotifyBridgeError

所有 notify-bridge 错误的基类异常。

```python
from notify_bridge.exceptions import NotifyBridgeError

try:
    bridge.send(...)
except NotifyBridgeError as e:
    print(f"错误: {e}")
```

## ValidationError

数据验证失败时抛出。

### 常见原因

- 缺少必需字段
- 无效的字段类型
- 无效的字段值
- Schema 约束违规

## NotificationError

发送通知失败时抛出。

```python
from notify_bridge.exceptions import NotificationError

try:
    response = bridge.send(...)
except NotificationError as e:
    print(f"通知失败: {e}")
    print(f"通知器: {e.notifier_name}")
```

### 属性

| 属性 | 类型 | 描述 |
|------|------|------|
| `notifier_name` | str | 失败的通知器名称 |

## NoSuchNotifierError

请求不存在的通知器时抛出。

## PluginError

插件加载或注册出现问题时抛出。

## ConfigurationError

配置出现问题时抛出。

## 错误码

### 企业微信错误码

| 错误码 | 描述 |
|--------|------|
| 0 | 成功 |
| 40014 | 无效的 access_token |
| 40035 | 无效的参数 |
| 45002 | 消息内容过长 |
| 45009 | API 调用频率超限 |

### 飞书错误码

| 错误码 | 描述 |
|--------|------|
| 0 | 成功 |
| 19001 | 无效的 webhook |
| 19002 | 无效的签名 |
| 19003 | 无效的时间戳 |
