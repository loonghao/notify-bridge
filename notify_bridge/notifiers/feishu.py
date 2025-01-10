"""Feishu notifier module."""

# Import built-in modules
import logging
from typing import Any, Dict, Optional, Union

# Import third-party modules
import httpx
from pydantic import Field, model_validator, ValidationError as PydanticValidationError

# Import local modules
from notify_bridge.exceptions import NotificationError, ValidationError
from notify_bridge.types import BaseNotifier, NotificationSchema

logger = logging.getLogger(__name__)


class FeishuSchema(NotificationSchema):
    """Schema for Feishu notifications."""

    url: str = Field(..., description="Feishu webhook URL")
    msg_type: str = Field(default="text", description="Message type")
    content: Optional[str] = Field(default=None, description="Message content")
    title: Optional[str] = Field(default=None, description="Title for card message")
    image_path: Optional[str] = Field(default=None, description="Path to image file")
    file_path: Optional[str] = Field(default=None, description="Path to file")

    @model_validator(mode="before")
    @classmethod
    def convert_fields(cls, data: Dict[str, Any]) -> Dict[str, Any]:
        """Convert webhook_url to url and body to content.

        Args:
            data: Data to validate.

        Returns:
            Dict[str, Any]: Validated data.
        """
        if "webhook_url" in data and "url" not in data:
            data["url"] = data["webhook_url"]
        if "body" in data and "content" not in data:
            data["content"] = data["body"]
        return data

    @model_validator(mode="before")
    @classmethod
    def validate_data(cls, data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate notification data.

        Args:
            data: Data to validate.

        Returns:
            Dict[str, Any]: Validated data.

        Raises:
            ValidationError: If validation fails.
        """
        # Convert webhook_url to url and body to content
        if "webhook_url" in data and "url" not in data:
            data["url"] = data["webhook_url"]
        if "body" in data and "content" not in data:
            data["content"] = data["body"]

        # Validate message type
        msg_type = data.get("msg_type", "text")
        valid_types = ["text", "post", "image", "file"]
        if msg_type not in valid_types:
            raise ValidationError(f"Invalid message type: {msg_type}. Must be one of: {valid_types}")

        # Validate content
        content = data.get("content")
        if msg_type in ["text", "post"] and not content:
            data["content"] = data.get("title", "")

        # Validate image path
        image_path = data.get("image_path")
        if msg_type == "image" and not image_path:
            raise ValidationError("Image path is required for image messages")

        # Validate file path
        file_path = data.get("file_path")
        if msg_type == "file" and not file_path:
            raise ValidationError("File path is required for file messages")

        return data


class FeishuNotifier(BaseNotifier):
    """Feishu notifier."""

    name = "feishu"
    schema = FeishuSchema

    def __init__(self, **kwargs):
        """Initialize the notifier.

        Args:
            **kwargs: Keyword arguments.
        """
        super().__init__(schema=FeishuSchema, **kwargs)

    def _build_text_payload(self, notification: Dict[str, Any]) -> Dict[str, Any]:
        """Build text message payload.

        Args:
            notification: Notification data.

        Returns:
            Dict[str, Any]: Text message payload.
        """
        return {
            "msg_type": "text",
            "content": {
                "text": notification.get("content", notification.get("title", ""))
            }
        }

    def _build_post_payload(self, notification: Dict[str, Any]) -> Dict[str, Any]:
        """Build post message payload.

        Args:
            notification: Notification data.

        Returns:
            Dict[str, Any]: Post message payload.
        """
        return {
            "msg_type": "post",
            "content": {
                "post": {
                    "zh_cn": {
                        "title": notification.get("title", ""),
                        "content": [
                            [
                                {
                                    "tag": "text",
                                    "text": notification.get("content", "")
                                }
                            ]
                        ]
                    }
                }
            }
        }

    def _build_image_payload(self, notification: Dict[str, Any]) -> Dict[str, Any]:
        """Build image message payload.

        Args:
            notification: Notification data.

        Returns:
            Dict[str, Any]: Image message payload.
        """
        return {
            "msg_type": "image",
            "content": {
                "image_key": notification.get("image_path", "")
            }
        }

    def _build_file_payload(self, notification: Dict[str, Any]) -> Dict[str, Any]:
        """Build file message payload.

        Args:
            notification: Notification data.

        Returns:
            Dict[str, Any]: File message payload.
        """
        return {
            "msg_type": "file",
            "content": {
                "file_key": notification.get("file_path", "")
            }
        }

    def _build_payload(self, notification: Dict[str, Any]) -> Dict[str, Any]:
        """Build payload for the notification.

        Args:
            notification: Notification data.

        Returns:
            Dict[str, Any]: Notification payload.

        Raises:
            NotificationError: If message type is invalid.
        """
        msg_type = notification.get("msg_type", "text")
        if msg_type == "text":
            payload = self._build_text_payload(notification)
        elif msg_type == "post":
            payload = self._build_post_payload(notification)
        elif msg_type == "image":
            payload = self._build_image_payload(notification)
        elif msg_type == "file":
            payload = self._build_file_payload(notification)
        else:
            raise NotificationError(f"Invalid message type: {msg_type}")

        return {
            "url": notification.get("url", ""),
            "json": payload
        }

    def build_payload(self, notification: Union[Dict[str, Any], NotificationSchema]) -> Dict[str, Any]:
        """Build payload for the notification.

        Args:
            notification: Notification data.

        Returns:
            Dict[str, Any]: Notification payload.

        Raises:
            NotificationError: If message type is invalid.
        """
        if isinstance(notification, NotificationSchema):
            notification = notification.model_dump()
        return self._build_payload(notification)

    async def build_payload_async(self, notification: Union[Dict[str, Any], NotificationSchema]) -> Dict[str, Any]:
        """Build payload for the notification asynchronously.

        Args:
            notification: Notification data.

        Returns:
            Dict[str, Any]: Notification payload.

        Raises:
            NotificationError: If message type is invalid.
        """
        if isinstance(notification, NotificationSchema):
            notification = notification.model_dump()
        return self._build_payload(notification)
