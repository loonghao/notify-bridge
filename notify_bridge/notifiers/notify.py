"""Notify notifier implementation.

This module provides the Notify notification implementation.
"""

# Import built-in modules
import logging
from typing import Any
from typing import Dict
from typing import Optional

# Import third-party modules
from pydantic import Field

# Import local modules
from notify_bridge.components import BaseNotifier
from notify_bridge.components import MessageType
from notify_bridge.components import NotificationSchema
from notify_bridge.exceptions import NotificationError


logger = logging.getLogger(__name__)


class NotifySchema(NotificationSchema):
    """Schema for Notify notifications."""

    base_url: str = Field(..., description="Base URL for notify service")
    token: Optional[str] = Field(None, description="Bearer token")
    tags: Optional[list[str]] = Field(None, description="Tags for the notification")
    icon: Optional[str] = Field(None, description="Icon URL")
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

        # Add optional fields
        if notification.icon:
            payload["icon"] = notification.icon
        if notification.tags:
            payload["tags"] = notification.tags

        return payload
