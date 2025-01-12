"""Notify notifier implementation.

This module provides the Notify data implementation.
"""

# Import built-in modules
import logging
from typing import Any
from typing import ClassVar
from typing import Dict
from typing import Optional

# Import third-party modules
from pydantic import Field
from pydantic import model_validator

# Import local modules
from notify_bridge.components import BaseNotifier
from notify_bridge.components import MessageType
from notify_bridge.exceptions import NotificationError
from notify_bridge.schema import APISchema


logger = logging.getLogger(__name__)


class NotifySchema(APISchema):
    """Schema for Notify notifications."""

    base_url: str = Field("https://notify-demo.deno.dev", description="Base URL for notify service")
    token: Optional[str] = Field(None, description="Bearer token")
    tags: Optional[list[str]] = Field(None, description="Tags for the data")
    icon: Optional[str] = Field(None, description="Icon URL")
    color: Optional[str] = Field(None, description="Color hex code")
    webhook_url: Optional[str] = Field(None, description="Webhook URL")
    headers: Dict[str, str] = Field(default_factory=dict, description="HTTP headers")
    message: Optional[str] = Field(None, description="Message content")
    content: Optional[str] = Field(None, description="Message content")

    @model_validator(mode="before")
    @classmethod
    def set_webhook_url(cls, values: Dict[str, Any]) -> Dict[str, Any]:
        """Set webhook URL if not provided.

        Args:
            values: Field values

        Returns:
            Dict[str, Any]: Updated field values
        """
        if not values.get("webhook_url"):
            base_url = values.get("base_url", "https://notify-demo.deno.dev").rstrip("/")
            values["webhook_url"] = f"{base_url}/api/notify"
        return values

    @model_validator(mode="before")
    @classmethod
    def set_content(cls, values: Dict[str, Any]) -> Dict[str, Any]:
        """Set content from message if not provided.

        Args:
            values: Field values

        Returns:
            Dict[str, Any]: Updated field values
        """
        message = values.get("message")
        if message and not values.get("content"):
            values["content"] = message
        return values

    @model_validator(mode="before")
    @classmethod
    def set_headers(cls, values: Dict[str, Any]) -> Dict[str, Any]:
        """Set authorization header if token is provided.

        Args:
            values: Field values

        Returns:
            Dict[str, Any]: Updated field values
        """
        headers = values.get("headers", {})
        if token := values.get("token"):
            headers["Authorization"] = f"Bearer {token}"
        values["headers"] = headers
        return values

    class Config:
        """Pydantic model configuration."""

        populate_by_name = True


class NotifyNotifier(BaseNotifier):
    """Notify notifier implementation."""

    name = "notify"
    schema_class = NotifySchema
    supported_types: ClassVar[set[MessageType]] = {MessageType.TEXT}

    def assemble_data(self, data: NotifySchema) -> Dict[str, Any]:
        """Assemble data data.

        Args:
            data: Notification data.

        Returns:
            Dict[str, Any]: API payload.

        Raises:
            NotificationError: If payload building fails.
        """
        text = data.content or data.message
        if not text:
            raise NotificationError("content or message is required", notifier_name=self.name)

        payload = {
            "title": data.title or "",
            "message": text,
            "type": data.msg_type,
        }

        # Add optional fields
        if data.tags:
            payload["tags"] = data.tags
        if data.icon:
            payload["icon"] = data.icon
        if data.color:
            payload["color"] = data.color

        return payload
