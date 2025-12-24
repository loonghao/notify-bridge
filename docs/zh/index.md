---
layout: home

hero:
  name: "Notify Bridge"
  text: "灵活的通知桥接器"
  tagline: 轻松向各种平台发送消息
  image:
    src: /logo.svg
    alt: Notify Bridge
  actions:
    - theme: brand
      text: 快速开始
      link: /zh/guide/getting-started
    - theme: alt
      text: GitHub
      link: https://github.com/loonghao/notify-bridge

features:
  - icon: 🚀
    title: 简单直观的 API
    details: 简洁易用的 API 设计，只需几行代码即可发送通知。
  - icon: 🔌
    title: 插件系统
    details: 可扩展的插件架构，轻松添加对新平台的支持。
  - icon: 🔄
    title: 同步异步支持
    details: 完整支持同步和异步操作，满足各种应用需求。
  - icon: 🛡️
    title: 类型安全
    details: 基于 Pydantic 模型的强类型验证，提供出色的 IDE 支持。
  - icon: 📝
    title: 丰富的消息格式
    details: 支持文本、Markdown、图片、文件等多种消息类型。
  - icon: 🌐
    title: 多平台支持
    details: 支持企业微信、飞书、GitHub 等多个平台。
---

## 快速开始

```python
from notify_bridge import NotifyBridge

# 创建桥接器实例
bridge = NotifyBridge()

# 发送通知
response = bridge.send(
    "wecom",
    webhook_url="YOUR_WEBHOOK_URL",
    message="来自 notify-bridge 的问候！",
    msg_type="text"
)
```

## 支持的平台

| 平台 | 状态 | 消息类型 |
|------|------|----------|
| 企业微信 (WeCom) | ✅ | text, markdown, markdown_v2, image, news, file, voice, template_card |
| 飞书 (Feishu) | ✅ | text, post, image, file, interactive |
| GitHub | ✅ | text, markdown |
| Notify | ✅ | text |
| 钉钉 | 🚧 | 即将推出 |
| Slack | 🚧 | 即将推出 |
| Discord | 🚧 | 即将推出 |

## 安装

```bash
pip install notify-bridge
```
