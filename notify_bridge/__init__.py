"""
Notify Bridge - A flexible notification framework."""

__version__ = "0.1.0"

# Import local modules
# Import core components
from notify_bridge.core import NotifyBridge

# Import exceptions
from notify_bridge.exceptions import (
    ConfigurationError,
    NoSuchNotifierError,
    NotificationError,
    NotifyBridgeError,
    PluginError,
    ValidationError,
)
from notify_bridge.factory import NotifierFactory

# Import core types
from notify_bridge.types import BaseNotifier, NotificationResponse, NotificationSchema

__all__ = [
    "NotifyBridge",
    "NotifierFactory",
    "BaseNotifier",
    "NotificationSchema",
    "NotificationResponse",
    "NotifyBridgeError",
    "ValidationError",
    "NotificationError",
    "NoSuchNotifierError",
    "PluginError",
    "ConfigurationError",
]
