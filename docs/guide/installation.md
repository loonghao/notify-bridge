# Installation

## Requirements

- Python 3.8 or higher
- pip, uv, or another Python package manager

## Install from PyPI

The recommended way to install notify-bridge is from PyPI:

```bash
pip install notify-bridge
```

Or using uv (faster):

```bash
uv pip install notify-bridge
```

## Install from Source

To install from source for development:

```bash
# Clone the repository
git clone https://github.com/loonghao/notify-bridge.git
cd notify-bridge

# Install in development mode
pip install -e ".[dev]"
```

## Dependencies

notify-bridge has the following dependencies that are automatically installed:

| Package | Version | Description |
|---------|---------|-------------|
| anyio | >=4.0.0 | Async I/O support |
| httpx | >=0.26.0 | HTTP client |
| pydantic | >=2.5.3 | Data validation |
| pillow | >=10.0.0 | Image processing |
| aiofiles | >=23.2.1 | Async file operations |

## Optional Dependencies

For development, install additional dependencies:

```bash
pip install notify-bridge[dev]
```

This includes:
- pytest - Testing framework
- pytest-cov - Code coverage
- pytest-asyncio - Async test support
- black - Code formatting
- ruff - Linting
- mypy - Type checking
- pre-commit - Git hooks

## Verify Installation

After installation, verify it works:

```python
from notify_bridge import NotifyBridge

bridge = NotifyBridge()
print(f"Available notifiers: {list(bridge.notifiers.keys())}")
```

Expected output:
```
Available notifiers: ['feishu', 'wecom', 'github', 'notify']
```
