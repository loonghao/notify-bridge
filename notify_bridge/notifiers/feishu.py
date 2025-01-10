"""Feishu notifier module."""

# Import built-in modules
import base64
import hashlib
import logging
import os
from typing import Any
from typing import Dict
from typing import List
from typing import Optional

# Import third-party modules
import httpx
from pydantic import Field
from pydantic import field_validator
from pydantic import ValidationInfo

# Import local modules
from notify_bridge.exceptions import NotificationError
from notify_bridge.exceptions import ValidationError
from notify_bridge.types import BaseNotifier
from notify_bridge.types import NotificationSchema


logger = logging.getLogger(__name__)


class FeishuSchema(NotificationSchema):
    """Schema for Feishu notifications."""

    url: str = Field(..., description="Feishu webhook URL")
    msg_type: str = Field(default="text", description="Message type")
    content: Optional[str] = Field(default=None, description="Message content")
    title: Optional[str] = Field(default=None, description="Title for card message")
    image_path: Optional[str] = Field(default=None, description="Path to image file")
    file_path: Optional[str] = Field(default=None, description="Path to file")

    @field_validator("msg_type")
    @classmethod
    def validate_msg_type(cls, value: str) -> str:
        """Validate message type.

        Args:
            value: Message type.

        Returns:
            str: Validated message type.

        Raises:
            ValidationError: If message type is invalid.
        """
        valid_types = ["text", "post", "image", "file"]
        if value not in valid_types:
            raise ValidationError(f"Invalid message type: {value}. Must be one of: {valid_types}")
        return value

    @field_validator("content")
    @classmethod
    def validate_content(cls, value: Optional[str], info: ValidationInfo) -> Optional[str]:
        """Validate content.

        Args:
            value: Content.
            info: Validation info.

        Returns:
            Optional[str]: Validated content.

        Raises:
            ValidationError: If content is required but not provided.
        """
        msg_type = info.data.get("msg_type", "text")
        if msg_type in ["text", "post"] and not value:
            raise ValidationError("Content is required for text and post messages")
        return value

    @field_validator("image_path")
    @classmethod
    def validate_image_path(cls, value: Optional[str], info: ValidationInfo) -> Optional[str]:
        """Validate image path.

        Args:
            value: Image path.
            info: Validation info.

        Returns:
            Optional[str]: Validated image path.

        Raises:
            ValidationError: If image path is required but not provided.
        """
        msg_type = info.data.get("msg_type")
        if msg_type == "image" and not value:
            raise ValidationError("Image path is required for image messages")
        return value

    @field_validator("file_path")
    @classmethod
    def validate_file_path(cls, value: Optional[str], info: ValidationInfo) -> Optional[str]:
        """Validate file path.

        Args:
            value: File path.
            info: Validation info.

        Returns:
            Optional[str]: Validated file path.

        Raises:
            ValidationError: If file path is required but not provided.
        """
        msg_type = info.data.get("msg_type")
        if msg_type == "file" and not value:
            raise ValidationError("File path is required for file messages")
        return value


class FeishuNotifier(BaseNotifier):
    """Notifier for Feishu."""

    name = "feishu"
    schema = FeishuSchema

    def _build_content_payload(self, notification: FeishuSchema) -> Dict[str, Any]:
        """Build the content payload for the Feishu API.

        Args:
            notification: Notification data.

        Returns:
            Dict[str, Any]: Content API payload.

        Raises:
            NotificationError: If building the payload fails.
        """
        payload = {"msg_type": notification.msg_type}
        if notification.msg_type == "text":
            payload["content"] = {"text": notification.content}
        elif notification.msg_type == "post":
            payload["content"] = {
                "post": {
                    "zh_cn": {
                        "title": notification.title or "",
                        "content": [[{"tag": "text", "text": notification.content}]],
                    }
                }
            }
        elif notification.msg_type == "image":
            if not notification.image_path or not os.path.exists(notification.image_path):
                raise NotificationError("Image file not found")
            with open(notification.image_path, "rb") as f:
                content = f.read()
                b64_content = base64.b64encode(content).decode()
                md5_content = hashlib.md5(content).hexdigest()
            client = self.client or httpx.Client()
            response = client.post(
                f"https://open.feishu.cn/open-apis/bot/v2/hook/{self._key(notification.url)}/image",
                json={"image_type": "message", "image": b64_content},
            )
            response.raise_for_status()
            data = response.json()
            if data.get("code") != 0:
                raise NotificationError(f"Failed to upload image: {data.get('msg')}")
            payload["content"] = {"image_key": data["data"]["image_key"]}
        elif notification.msg_type == "file":
            if not notification.file_path or not os.path.exists(notification.file_path):
                raise NotificationError("File not found")
            with open(notification.file_path, "rb") as f:
                files = {"file": f}
                client = self.client or httpx.Client()
                response = client.post(
                    "https://open.feishu.cn/open-apis/bot/v2/hook/upload_file",
                    files=files,
                )
                response.raise_for_status()
                data = response.json()
                if data.get("code") != 0:
                    raise NotificationError(f"Failed to upload file: {data.get('msg')}")
                payload["content"] = {"file_key": data["data"]["file_key"]}
        else:
            raise NotificationError(f"Unsupported message type: {notification.msg_type}")

        return {"json": payload}

    async def _build_content_payload_async(self, notification: FeishuSchema) -> Dict[str, Any]:
        """Build the content payload for the Feishu API asynchronously.

        Args:
            notification: Notification data.

        Returns:
            Dict[str, Any]: Content API payload.

        Raises:
            NotificationError: If building the payload fails.
        """
        payload = {"msg_type": notification.msg_type}
        if notification.msg_type == "text":
            payload["content"] = {"text": notification.content}
        elif notification.msg_type == "post":
            payload["content"] = {
                "post": {
                    "zh_cn": {
                        "title": notification.title or "",
                        "content": [[{"tag": "text", "text": notification.content}]],
                    }
                }
            }
        elif notification.msg_type == "image":
            if not notification.image_path or not os.path.exists(notification.image_path):
                raise NotificationError("Image file not found")
            with open(notification.image_path, "rb") as f:
                content = f.read()
                b64_content = base64.b64encode(content).decode()
                md5_content = hashlib.md5(content).hexdigest()
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"https://open.feishu.cn/open-apis/bot/v2/hook/{self._key(notification.url)}/image",
                    json={"image_type": "message", "image": b64_content},
                )
                response.raise_for_status()
                try:
                    data = response.json()
                except AttributeError:
                    data = await response.json()
                if data.get("code") != 0:
                    raise NotificationError(f"Failed to upload image: {data.get('msg')}")
                payload["content"] = {"image_key": data["data"]["image_key"]}
        elif notification.msg_type == "file":
            if not notification.file_path or not os.path.exists(notification.file_path):
                raise NotificationError("File not found")
            with open(notification.file_path, "rb") as f:
                files = {"file": f}
                async with httpx.AsyncClient() as client:
                    response = await client.post(
                        "https://open.feishu.cn/open-apis/bot/v2/hook/upload_file",
                        files=files,
                    )
                    response.raise_for_status()
                    try:
                        data = response.json()
                    except AttributeError:
                        data = await response.json()
                    if data.get("code") != 0:
                        raise NotificationError(f"Failed to upload file: {data.get('msg')}")
                    payload["content"] = {"file_key": data["data"]["file_key"]}
        else:
            raise NotificationError(f"Unsupported message type: {notification.msg_type}")

        return {"json": payload}

    def build_payload(self, notification: FeishuSchema) -> Dict[str, Any]:
        """Build the payload for the Feishu API.

        Args:
            notification: Notification data.

        Returns:
            Dict[str, Any]: API payload.

        Raises:
            NotificationError: If building the payload fails.
        """
        return {"url": notification.url, **self._build_content_payload(notification)}

    async def build_payload_async(self, notification: FeishuSchema) -> Dict[str, Any]:
        """Build the payload for the Feishu API asynchronously.

        Args:
            notification: Notification data.

        Returns:
            Dict[str, Any]: API payload.

        Raises:
            NotificationError: If building the payload fails.
        """
        return {"url": notification.url, **await self._build_content_payload_async(notification)}

    def _key(self, url: str) -> str:
        """Get the Feishu webhook key.

        Args:
            url: Webhook URL.

        Returns:
            str: Webhook key.

        Raises:
            NotificationError: If no webhook URL is provided.
        """
        try:
            return url.split("hook/")[1]
        except IndexError:
            raise NotificationError("Invalid webhook URL format")
