"""WeCom notifier implementation.

This module provides the WeCom (WeChat Work) notification implementation.
"""

# Import built-in modules
import base64
import logging
from pathlib import Path
from typing import Any, ClassVar, Dict, List, Optional

# Import third-party modules
from pydantic import BaseModel, Field, ValidationInfo, field_validator

# Import local modules
from notify_bridge.components import BaseNotifier, MessageType, NotificationError
from notify_bridge.schema import WebhookSchema

logger = logging.getLogger(__name__)


class Article(BaseModel):
    """Article schema for WeCom news message."""

    title: str = Field(..., description="Article title")
    description: Optional[str] = Field(None, description="Article description")
    url: str = Field(..., description="Article URL")
    picurl: Optional[str] = Field(None, description="Article image URL")

    class Config:
        """Pydantic model configuration."""

        populate_by_name = True


class WeComSchema(WebhookSchema):
    """Schema for WeCom notifications."""

    webhook_url: str = Field(..., description="Webhook URL", alias="base_url")
    content: Optional[str] = Field(None, description="Message content", alias="message")
    mentioned_list: Optional[List[str]] = Field(default_factory=list, description="List of mentioned users")
    mentioned_mobile_list: Optional[List[str]] = Field(
        default_factory=list, description="List of mentioned mobile numbers"
    )
    image_path: Optional[str] = Field(None, description="Path to image file")
    articles: Optional[List[Dict[str, Any]]] = Field(default_factory=list, description="List of articles")

    @field_validator("content")
    @classmethod
    def validate_content(cls, v: Optional[str], info: ValidationInfo) -> Optional[str]:
        """Validate content field.

        Content is required for text and markdown messages, optional for others.
        """
        msg_type = info.data.get("msg_type")
        if msg_type in (MessageType.TEXT, MessageType.MARKDOWN) and not v:
            raise NotificationError("content is required for text and markdown messages")
        return v

    class Config:
        """Pydantic model configuration."""

        populate_by_name = True


class WeComNotifier(BaseNotifier):
    """WeCom notifier implementation."""

    name = "wecom"
    schema_class = WeComSchema
    supported_types: ClassVar[set[MessageType]] = {
        MessageType.TEXT,
        MessageType.MARKDOWN,
        MessageType.IMAGE,
        MessageType.NEWS,
    }

    def _encode_image(self, image_path: str) -> tuple[str, str]:
        """Encode image to base64.

        Args:
            image_path: Path to image file.

        Returns:
            tuple: (Base64 encoded image, MD5 hash)

        Raises:
            NotificationError: If image file not found or encoding fails.
        """
        path = Path(image_path)
        if not path.exists():
            raise NotificationError(f"Image file not found: {image_path}")

        try:
            # Import built-in modules
            import hashlib

            with open(image_path, "rb") as f:
                content = f.read()
                md5 = hashlib.md5(content).hexdigest()
                base64_data = base64.b64encode(content).decode()
                return base64_data, md5
        except Exception as e:
            raise NotificationError(f"Failed to encode image: {str(e)}")

    def _build_text_payload(self, notification: WeComSchema) -> Dict[str, Any]:
        """Build text message payload.

        Args:
            notification: Notification data.

        Returns:
            Dict[str, Any]: Text message payload.

        Raises:
            NotificationError: If content is missing.
        """
        if not notification.content:
            raise NotificationError("content is required for text messages")

        return {
            "msgtype": "text",
            "text": {
                "content": notification.content,
                "mentioned_list": notification.mentioned_list,
                "mentioned_mobile_list": notification.mentioned_mobile_list,
            },
        }

    def _build_markdown_payload(self, notification: WeComSchema) -> Dict[str, Any]:
        """Build markdown message payload.

        Args:
            notification: Notification data.

        Returns:
            Dict[str, Any]: Markdown message payload.

        Raises:
            NotificationError: If content is missing.
        """
        if not notification.content:
            raise NotificationError("content is required for markdown messages")

        return {"msgtype": "markdown", "markdown": {"content": notification.content}}

    def _build_image_payload(self, notification: WeComSchema) -> Dict[str, Any]:
        """Build image message payload.

        Args:
            notification: Notification data.

        Returns:
            Dict[str, Any]: Image message payload.
        """
        if not notification.image_path:
            raise NotificationError("image_path is required for image message")

        base64_data, md5 = self._encode_image(notification.image_path)
        return {"msgtype": "image", "image": {"base64": base64_data, "md5": md5}}

    def _build_news_payload(self, notification: WeComSchema) -> Dict[str, Any]:
        """Build news message payload.

        Args:
            notification: Notification data.

        Returns:
            Dict[str, Any]: News message payload.
        """
        if not notification.articles:
            raise NotificationError("articles is required for news message")

        return {
            "msgtype": "news",
            "news": {"articles": notification.articles},
            "text": {
                "mentioned_list": notification.mentioned_list,
                "mentioned_mobile_list": notification.mentioned_mobile_list,
            },
        }

    def assemble_data(self, data: WeComSchema) -> Dict[str, Any]:
        """Assemble data data.

        Args:
            data: Notification data

        Returns:
            Dict[str, Any]: API payload
        """
        if not isinstance(data, WeComSchema):
            raise NotificationError("data must be a WeComSchema instance")

        payload = {"msgtype": data.msg_type}
        if data.msg_type == MessageType.TEXT:
            payload.update(self._build_text_payload(data))
        elif data.msg_type == MessageType.MARKDOWN:
            payload.update(self._build_markdown_payload(data))
        elif data.msg_type == MessageType.IMAGE:
            payload.update(self._build_image_payload(data))
        elif data.msg_type == MessageType.NEWS:
            payload.update(self._build_news_payload(data))
        return payload
