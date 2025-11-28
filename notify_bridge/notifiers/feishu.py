"""Feishu notifier implementation.

This module provides the Feishu (Lark) data implementation.
"""

# Import built-in modules
import base64
import logging
from pathlib import Path
from typing import Any, ClassVar, Dict, List, Optional

# Import third-party modules
from pydantic import AliasChoices, BaseModel, Field

# Import local modules
from notify_bridge.components import BaseNotifier, MessageType, NotificationError
from notify_bridge.schema import WebhookSchema

logger = logging.getLogger(__name__)


class CardConfig(BaseModel):
    """Schema for Feishu card config."""

    wide_screen_mode: bool = Field(True, description="Wide screen mode")


class CardHeader(BaseModel):
    """Schema for Feishu card header."""

    title: str = Field(..., description="Header title")
    template: str = Field("blue", description="Header template color")


class FeishuSchema(WebhookSchema):
    """Schema for Feishu notifications."""

    webhook_url: str = Field(
        ..., description="Webhook URL", validation_alias=AliasChoices("url", "webhook_url", "base_url")
    )
    content: Optional[str] = Field(None, description="Message content")
    post_content: Optional[Dict[str, List[List[Dict[str, str]]]]] = Field(None, description="Post message content")
    image_path: Optional[str] = Field(None, description="Path to image file")
    file_path: Optional[str] = Field(None, description="Path to file")
    token: Optional[str] = Field(None, description="Access token for file upload")
    card_config: Optional[CardConfig] = Field(None, description="Card config")
    card_header: Optional[CardHeader] = Field(None, description="Card header")
    card_elements: Optional[List[Dict[str, Any]]] = Field(None, description="Card elements")


class FeishuNotifier(BaseNotifier):
    """Feishu notifier implementation."""

    name = "feishu"
    schema_class = FeishuSchema
    supported_types: ClassVar[set[MessageType]] = {
        MessageType.TEXT,
        MessageType.POST,
        MessageType.IMAGE,
        MessageType.FILE,
        MessageType.INTERACTIVE,
    }

    def _build_text_payload(self, notification: FeishuSchema) -> Dict[str, Any]:
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

        return {"msg_type": "text", "content": {"text": notification.content}}

    def _build_post_payload(self, notification: FeishuSchema) -> Dict[str, Any]:
        """Build post message payload.

        Args:
            notification: Notification data.

        Returns:
            Dict[str, Any]: Post message payload.

        Raises:
            NotificationError: If post_content is missing.
        """
        if not notification.post_content:
            raise NotificationError("post_content is required for post messages")

        return {"msg_type": "post", "content": {"post": notification.post_content}}

    def _encode_image(self, image_path: str) -> str:
        """Encode image to base64.

        Args:
            image_path: Path to image file.

        Returns:
            str: Base64 encoded image.

        Raises:
            NotificationError: If image file not found or encoding fails.
        """
        path = Path(image_path)
        if not path.exists():
            raise NotificationError(f"Image file not found: {image_path}")

        try:
            with open(image_path, "rb") as f:
                return base64.b64encode(f.read()).decode()
        except Exception as e:
            raise NotificationError(f"Failed to encode image: {str(e)}")

    def _build_image_payload(self, notification: FeishuSchema) -> Dict[str, Any]:
        """Build image message payload.

        Args:
            notification: Notification data.

        Returns:
            Dict[str, Any]: Image message payload.
        """
        if not notification.image_path:
            raise NotificationError("image_path is required for image message")

        try:
            image_content = self._encode_image(notification.image_path)
            return {"msg_type": "image", "content": {"base64": image_content}}
        except Exception as e:
            raise NotificationError(f"Failed to build image payload: {str(e)}")

    def _build_file_payload(self, notification: FeishuSchema) -> Dict[str, Any]:
        """Build file message payload.

        Args:
            notification: Notification data.

        Returns:
            Dict[str, Any]: File message payload.
        """
        if not notification.file_path:
            raise NotificationError("file_path is required for file message")

        if not notification.token:
            raise NotificationError("token is required for uploading file")

        path = Path(notification.file_path)
        if not path.exists():
            raise NotificationError(f"File not found: {notification.file_path}")

        try:
            with open(notification.file_path, "rb") as f:
                content = f.read()
                file_key = self._upload_file(content, notification.token)
                return {"msg_type": "file", "content": {"file_key": file_key}}
        except Exception as e:
            raise NotificationError(f"Failed to upload file: {str(e)}")

    def _upload_image(self, content: bytes, token: str) -> str:
        """Upload image to Feishu.

        Args:
            content: Image content.
            token: Access token.

        Returns:
            str: Image key.

        Raises:
            NotificationError: If upload fails.
        """
        # TODO: Implement image upload
        raise NotImplementedError("Image upload not implemented yet")

    def _upload_file(self, content: bytes, token: str) -> str:
        """Upload file to Feishu.

        Args:
            content: File content.
            token: Access token.

        Returns:
            str: File key.

        Raises:
            NotificationError: If upload fails.
        """
        # TODO: Implement file upload
        raise NotImplementedError("File upload not implemented yet")

    def _assemble_interactive_data(self, notification: FeishuSchema) -> Dict[str, Any]:
        """Assemble interactive message data.

        Args:
            notification: Notification data.

        Returns:
            Dict[str, Any]: Interactive message data.

        Raises:
            NotificationError: If card_header or card_elements is missing.
        """
        if not notification.card_header:
            raise NotificationError("card_header is required for interactive messages", notifier_name=self.name)
        if not notification.card_elements:
            raise NotificationError("card_elements is required for interactive messages", notifier_name=self.name)

        return {
            "msg_type": "interactive",
            "card": {
                "header": {
                    "title": {
                        "tag": "plain_text",
                        "content": notification.card_header.title,
                        "template": notification.card_header.template,
                    }
                },
                "elements": notification.card_elements,
                "config": {
                    "wide_screen_mode": notification.card_config.wide_screen_mode if notification.card_config else True
                },
            },
        }

    def assemble_data(self, data: FeishuSchema) -> Dict[str, Any]:
        """Assemble data data.

        Args:
            data: Notification data.

        Returns:
            Dict[str, Any]: API payload.

        Raises:
            NotificationError: If message type is not supported.
        """
        # Convert string to MessageType enum for consistent comparison
        msg_type = MessageType(data.msg_type) if isinstance(data.msg_type, str) else data.msg_type

        if msg_type == MessageType.TEXT:
            return self._build_text_payload(data)
        elif msg_type == MessageType.POST:
            return self._build_post_payload(data)
        elif msg_type == MessageType.IMAGE:
            return self._build_image_payload(data)
        elif msg_type == MessageType.FILE:
            return self._build_file_payload(data)
        elif msg_type == MessageType.INTERACTIVE:
            return self._assemble_interactive_data(data)
        raise NotificationError(f"Unsupported message type: {data.msg_type}", notifier_name=self.name)
