"""Feishu notifier."""

# Import built-in modules
import logging
from typing import Any, Dict, Optional, Union

# Import third-party modules
import httpx
from pydantic import Field, ValidationInfo, field_validator, model_validator

# Import local modules
from notify_bridge.exceptions import NotificationError, ValidationError
from notify_bridge.types import BaseNotifier, NotificationResponse, NotificationSchema

logger = logging.getLogger(__name__)


class FeishuSchema(NotificationSchema):
    """Feishu notification schema."""

    webhook_url: Optional[str] = Field(None, description="Webhook URL")
    url: str = Field(..., description="URL")
    msg_type: str = Field("text", description="Message type")
    content: Optional[str] = Field(None, description="Message content")
    title: Optional[str] = Field(None, description="Message title")
    body: Optional[str] = Field(None, description="Message body")
    image_path: Optional[str] = Field(None, description="Image path")
    file_path: Optional[str] = Field(None, description="File path")

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

    @field_validator("msg_type")
    def validate_msg_type(cls, v: str) -> str:
        """Validate message type.

        Args:
            v: Message type value.

        Returns:
            str: Message type value.

        Raises:
            ValidationError: If message type is not supported.
        """
        if v not in ["text", "post", "image", "file"]:
            raise ValidationError("Invalid message type")
        return v

    @field_validator("url", mode="before")
    def validate_url(cls, v: Optional[str], info: ValidationInfo) -> str:
        """Validate URL.

        Args:
            v: URL value.
            info: Validation info.

        Returns:
            str: URL value.

        Raises:
            ValidationError: If URL is not provided.
        """
        if v is None:
            v = info.data.get("webhook_url")
        if not v:
            raise ValidationError("URL is required")
        return v

    @field_validator("content", mode="before")
    def validate_content(cls, v: Optional[str], info: ValidationInfo) -> Optional[str]:
        """Validate content.

        Args:
            v: Content value.
            info: Validation info.

        Returns:
            str: Content value.
        """
        if v is None:
            v = info.data.get("body")
        return v


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

    async def notify_async(self, notification: Union[Dict[str, Any], NotificationSchema]) -> NotificationResponse:
        """Send notification asynchronously.

        Args:
            notification: Notification data.

        Returns:
            NotificationResponse: Notification response.

        Raises:
            NotificationError: If notification fails.
        """
        try:
            payload = self.build_payload(notification)
            async with httpx.AsyncClient() as client:
                response = await client.post(payload["url"], json=payload["json"])
                response_data = await response.json()
                if response.status_code >= 400:
                    raise NotificationError(f"Failed to send {self.name} notification: {response_data}")
                return NotificationResponse(
                    success=True,
                    name=self.name,
                    data=response_data
                )
        except Exception as e:
            raise NotificationError(f"Failed to send {self.name} notification: {e}") from e
