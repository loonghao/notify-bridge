---
layout: home

hero:
  name: "Notify Bridge"
  text: "A Flexible Notification Bridge"
  tagline: Send messages to various platforms with ease
  image:
    src: /logo.svg
    alt: Notify Bridge
  actions:
    - theme: brand
      text: Get Started
      link: /guide/getting-started
    - theme: alt
      text: View on GitHub
      link: https://github.com/loonghao/notify-bridge

features:
  - icon: 🚀
    title: Simple & Intuitive API
    details: Clean and easy-to-use API design that lets you send notifications in just a few lines of code.
  - icon: 🔌
    title: Plugin System
    details: Extensible plugin architecture allows you to easily add support for new platforms.
  - icon: 🔄
    title: Sync & Async Support
    details: Full support for both synchronous and asynchronous operations to fit your application needs.
  - icon: 🛡️
    title: Type Safe
    details: Built with Pydantic models for robust type validation and excellent IDE support.
  - icon: 📝
    title: Rich Message Formats
    details: Support for text, markdown, images, files, and platform-specific message types.
  - icon: 🌐
    title: Multi-Platform
    details: Send notifications to WeCom, Feishu, GitHub, and more platforms.
---

## Quick Start

```python
from notify_bridge import NotifyBridge

# Create a bridge instance
bridge = NotifyBridge()

# Send a notification
response = bridge.send(
    "wecom",
    webhook_url="YOUR_WEBHOOK_URL",
    message="Hello from notify-bridge!",
    msg_type="text"
)
```

## Supported Platforms

| Platform | Status | Message Types |
|----------|--------|---------------|
| WeCom (企业微信) | ✅ | text, markdown, markdown_v2, image, news, file, voice, template_card |
| Feishu (飞书) | ✅ | text, post, image, file, interactive |
| GitHub | ✅ | text, markdown |
| Notify | ✅ | text |
| DingTalk | 🚧 | Coming soon |
| Slack | 🚧 | Coming soon |
| Discord | 🚧 | Coming soon |

## Installation

```bash
pip install notify-bridge
```
