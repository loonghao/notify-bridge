"""WeChat Work (WeCom) notifier."""

# Import built-in modules
import base64
import hashlib
import os
from typing import Any, Dict, List, Optional

# Import third-party modules
import httpx
from pydantic import Field

# Import local modules
from notify_bridge.exceptions import NotificationError
from notify_bridge.types import BaseNotifier, NotificationSchema


class WeComSchema(NotificationSchema):
    """Schema for WeCom notifications."""

    url: str = Field(..., description="WeCom webhook URL")
    msg_type: str = Field(default="text", description="Message type")
    content: str = Field(description="Message content")
    mentioned_list: Optional[List[str]] = Field(default=None, description="List of mentioned users")
    mentioned_mobile_list: Optional[List[str]] = Field(default=None, description="List of mentioned mobile numbers")
    articles: Optional[List[Dict[str, str]]] = Field(default=None, description="Articles for news message type")
    image_path: Optional[str] = Field(default=None, description="Path to image file")
    file_path: Optional[str] = Field(default=None, description="Path to file")


class WeComNotifier(BaseNotifier):
    """WeCom notifier implementation."""

    name = "wecom"
    schema = WeComSchema

    def _build_content_payload(self, notification: WeComSchema) -> Dict[str, Any]:
        """Build the content payload for the WeCom API.

        Args:
            notification: Notification data.

        Returns:
            Dict[str, Any]: Content API payload.

        Raises:
            NotificationError: If building the payload fails.
        """
        payload = {"msgtype": notification.msg_type}
        if notification.msg_type == "text":
            payload["text"] = {
                "content": notification.content,
                "mentioned_list": notification.mentioned_list,
                "mentioned_mobile_list": notification.mentioned_mobile_list,
            }
        elif notification.msg_type == "markdown":
            payload["markdown"] = {"content": notification.content}
        elif notification.msg_type == "news":
            if not notification.articles:
                raise NotificationError("Articles are required for news message type")
            payload["news"] = {"articles": notification.articles}
        elif notification.msg_type == "image":
            if not notification.image_path or not os.path.exists(notification.image_path):
                raise NotificationError("Image file not found")
            with open(notification.image_path, "rb") as f:
                content = f.read()
                b64_content = base64.b64encode(content).decode()
                md5_content = hashlib.md5(content).hexdigest()
            payload["image"] = {
                "base64": b64_content,
                "md5": md5_content,
            }
        elif notification.msg_type == "file":
            if not notification.file_path or not os.path.exists(notification.file_path):
                raise NotificationError("File not found")
            with open(notification.file_path, "rb") as f:
                files = {"file": f}
                client = self.client or httpx.Client()
                response = client.post(
                    "https://qyapi.weixin.qq.com/cgi-bin/webhook/upload_media",
                    params={"key": self._key(notification.url), "type": "file"},
                    files=files,
                )
                response.raise_for_status()
                data = response.json()
                if data.get("errcode") != 0:
                    raise NotificationError(f"Failed to upload file: {data.get('errmsg')}")
                payload["file"] = {"media_id": data["media_id"]}
        else:
            raise NotificationError(f"Unsupported message type: {notification.msg_type}")

        return {"json": payload}

    async def _build_content_payload_async(self, notification: WeComSchema) -> Dict[str, Any]:
        """Build the content payload for the WeCom API asynchronously.

        Args:
            notification: Notification data.

        Returns:
            Dict[str, Any]: Content API payload.

        Raises:
            NotificationError: If building the payload fails.
        """
        payload = {"msgtype": notification.msg_type}
        if notification.msg_type == "text":
            payload["text"] = {
                "content": notification.content,
                "mentioned_list": notification.mentioned_list,
                "mentioned_mobile_list": notification.mentioned_mobile_list,
            }
        elif notification.msg_type == "markdown":
            payload["markdown"] = {"content": notification.content}
        elif notification.msg_type == "news":
            if not notification.articles:
                raise NotificationError("Articles are required for news message type")
            payload["news"] = {"articles": notification.articles}
        elif notification.msg_type == "image":
            if not notification.image_path or not os.path.exists(notification.image_path):
                raise NotificationError("Image file not found")
            with open(notification.image_path, "rb") as f:
                content = f.read()
                b64_content = base64.b64encode(content).decode()
                md5_content = hashlib.md5(content).hexdigest()
            payload["image"] = {
                "base64": b64_content,
                "md5": md5_content,
            }
        elif notification.msg_type == "file":
            if not notification.file_path or not os.path.exists(notification.file_path):
                raise NotificationError("File not found")
            with open(notification.file_path, "rb") as f:
                files = {"file": f}
                async with httpx.AsyncClient() as client:
                    response = await client.post(
                        "https://qyapi.weixin.qq.com/cgi-bin/webhook/upload_media",
                        params={"key": self._key(notification.url), "type": "file"},
                        files=files,
                    )
                    response.raise_for_status()
                    try:
                        data = response.json()
                    except AttributeError:
                        data = await response.json()
                    if data.get("errcode") != 0:
                        raise NotificationError(f"Failed to upload file: {data.get('errmsg')}")
                    payload["file"] = {"media_id": data["media_id"]}
        else:
            raise NotificationError(f"Unsupported message type: {notification.msg_type}")

        return {"json": payload}

    def build_payload(self, notification: WeComSchema) -> Dict[str, Any]:
        """Build the payload for the WeCom API.

        Args:
            notification: Notification data.

        Returns:
            Dict[str, Any]: API payload.

        Raises:
            NotificationError: If building the payload fails.
        """
        return {"url": notification.url, **self._build_content_payload(notification)}

    async def build_payload_async(self, notification: WeComSchema) -> Dict[str, Any]:
        """Build the payload for the WeCom API asynchronously.

        Args:
            notification: Notification data.

        Returns:
            Dict[str, Any]: API payload.

        Raises:
            NotificationError: If building the payload fails.
        """
        return {"url": notification.url, **await self._build_content_payload_async(notification)}

    def _key(self, url: str) -> str:
        """Get the WeCom webhook key.

        Args:
            url: Webhook URL.

        Returns:
            str: Webhook key.

        Raises:
            NotificationError: If no webhook URL is provided.
        """
        try:
            return url.split("key=")[1]
        except IndexError:
            raise NotificationError("Invalid webhook URL format")
