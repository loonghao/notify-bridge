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
