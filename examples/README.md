# notify-bridge 示例

这个目录包含了 notify-bridge 的各种使用示例。你可以通过这些示例了解如何使用 notify-bridge 向不同平台发送消息。

## 目录结构

```
examples/
├── assets/                 # 示例资源文件（图片等）
├── .env                    # 环境变量配置文件
├── .env.example           # 环境变量示例文件
├── requirements.txt       # 示例代码的依赖包
├── run_test.py           # 主测试脚本（运行所有示例）
├── run_feishu.py         # 飞书机器人示例
├── run_github.py         # GitHub 通知示例
├── run_notify.py         # 通用通知示例
└── run_wecom.py          # 企业微信机器人示例
```

## 快速开始

1. 首先安装依赖：
```bash
pip install -r requirements.txt
```

2. 配置环境变量：
   - 复制 `.env.example` 为 `.env`
   - 在 `.env` 文件中填入你的配置信息：
```bash
# .env 文件示例
WECOM_WEBHOOK_URL=https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key=YOUR_KEY
FEISHU_WEBHOOK_URL=https://open.feishu.cn/open-apis/bot/v2/hook/YOUR_KEY
NOTIFY_BASE_URL=https://notify-demo.deno.dev
```

3. 运行示例：
```bash
# 运行所有示例
python run_test.py

# 或者运行单个平台的示例
python run_feishu.py   # 运行飞书示例
python run_wecom.py    # 运行企业微信示例
python run_github.py   # 运行 GitHub 示例
python run_notify.py   # 运行通用通知示例
```

## 示例说明

### run_test.py

这是主测试脚本，它会：
1. 加载环境变量（优先从 `.env` 文件加载，如果没有则使用 `.env.example` 中的默认值）
2. 设置默认的 webhook URL（如果环境变量中没有设置）
3. 依次运行所有平台的示例

### run_feishu.py

飞书机器人示例，展示了如何：
- 发送文本消息
- 发送富文本消息
- 发送图片消息
- 发送文件消息

### run_wecom.py

企业微信机器人示例，展示了如何：
- 发送文本消息
- 发送 Markdown 消息
- 发送图文消息

### run_github.py

GitHub 通知示例，展示了如何：
- 发送 Issue 相关通知
- 发送 PR 相关通知
- 发送其他 GitHub 事件通知

### run_notify.py

通用通知示例，展示了如何：
- 使用统一的接口发送通知
- 处理不同类型的消息
- 处理错误和异常

## 注意事项

1. 请确保在运行示例之前已经正确配置了相应平台的 webhook URL
2. 某些示例可能需要额外的配置或权限，请参考各平台的文档
3. 示例中的图片和文件资源都存放在 `assets` 目录下
4. 建议先阅读每个示例文件的代码注释，了解具体的使用方法和注意事项
