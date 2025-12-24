## v0.7.0 (2025-12-24)

### Feat

- add markdown/markdown_v2 e2e tests and VitePress documentation

### Fix

- **ci**: use nox for running tests to ensure proper environment
- **e2e**: correct parameter name template_card_image
- **e2e**: add required card_image for news_notice template card
- **ci**: install package with dev dependencies for unit tests
- add autoflake to pre-commit and remove unused import

## v0.6.2 (2025-11-28)

### Fix

- **wecom**: use correct payload key 'markdown_v2' for markdown_v2 message type

## v0.6.1 (2025-11-28)

### Fix

- add populate_by_name to model_config for field name support

## v0.6.0 (2025-11-28)

### Feat

- add debug logging for request payload and response

## v0.5.3 (2025-11-28)

### Refactor

- optimize code and fix async cleanup issues

## v0.5.2 (2025-11-27)

### Fix

- use markdown_v2 msgtype in _build_markdown_v2_payload
- preserve markdown_v2 msgtype in WeChat Work API requests

## v0.5.1 (2025-11-18)

### Fix

- correct upload_media endpoint handling in WeCom notifier

## v0.5.0 (2025-11-18)

### Feat

- add WeCom template card support for text_notice and news_notice

### Fix

- resolve black formatting and mypy type checking issues

## v0.4.0 (2025-11-18)

### Feat

- add UPLOAD_MEDIA message type for WeCom

## v0.3.2 (2025-11-17)

### Fix

- escape forward slashes in WeCom markdown_v2 format

## v0.3.1 (2025-11-17)

### Fix

- **wecom**: preserve underscores &amp; support markdown_v2

## v0.3.0 (2025-02-26)

### Feat

- **wecom**: enhance markdown support and add custom color mapping

## v0.2.0 (2025-01-12)

### Feat

- **notify-bridge**: add validation and error handling to notification sending
- **notify-bridge**: refactor notifier classes and add tests
- **notify-bridge**: add GitHub notifier implementation and example scripts
- **notify-bridge**: refactor notification sending logic and add unregister notifier method
- **notify-bridge**: refactor notification sending logic and add unregister notifier method
- **notify-bridge**: enhance Feishu notifier with improved payload handling and validation
- **notify-bridge**: add WeCom notifier and refactor core components

### Fix

- **notify-bridge**: ignore notifier class in plugin loading

### Refactor

- **tests**: simplify imports and rename methods for consistency
- **notify-bridge**: refactor code structure and import statements
- **notify-bridge**: refactor code structure and import statements

## v0.1.0 (2025-01-10)

### Feat

- **notify-bridge**: add core components and feishu notifier
