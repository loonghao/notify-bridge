"""Notify notifier implementation.

This module provides the Notify notification implementation.
"""

# Import built-in modules
import logging
from typing import Any, Dict, Optional

# Import third-party modules
from pydantic import Field

# Import local modules
from notify_bridge.components import BaseNotifier, MessageType, NotificationError, NotificationSchema
from notify_bridge.exceptions import NotificationError

logger = logging.getLogger(__name__)


class NotifySchema(NotificationSchema):
    """Schema for Notify notifications."""
    base_url: str
    token: Optional[str] = None
    tags: Optional[list[str]] = None
    icon: Optional[str] = None
    webhook_url: Optional[str] = None
    headers: Dict[str, str] = Field(default_factory=dict)


class NotifyNotifier(BaseNotifier):
    """Notify notifier implementation."""

    name = "notify"
    schema_class = NotifySchema
    supported_types = {MessageType.TEXT}

    def _get_headers(self, token: Optional[str] = None) -> Dict[str, str]:
        """Get request headers.

        Args:
            token: Bearer token

        Returns:
            Dict[str, str]: Request headers
        """
        headers = {"Content-Type": "application/json"}
        if token:
            headers["Authorization"] = f"Bearer {token}"
        return headers

    def build_payload(self, notification: NotificationSchema) -> Dict[str, Any]:
        """Build notification payload.

        Args:
            notification: Notification data.

        Returns:
            Dict[str, Any]: API payload.

        Raises:
            NotificationError: If payload building fails.
        """
        if not isinstance(notification, NotifySchema):
            raise NotificationError("Invalid notification schema")

        # Set webhook URL if not set
        if not notification.webhook_url:
            notification.webhook_url = f"{notification.base_url}/api/notify"

        # Set headers with token if provided
        if notification.token:
            notification.headers.update(self._get_headers(notification.token))

        payload = {
            "title": notification.title or "",
            "message": notification.content,
        }

        # Only add optional fields if they exist and have values
        notify_schema = notification if isinstance(notification, NotifySchema) else None
        if notify_schema and notify_schema.icon:
            payload["icon"] = notify_schema.icon
        if notify_schema and notify_schema.tags:
            payload["tags"] = notify_schema.tags

        return payload
