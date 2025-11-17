"""WeCom notifier implementation.

This module provides the WeCom (WeChat Work) notification implementation.
"""

# Import built-in modules
import base64
import logging
import re
from pathlib import Path
from typing import Any, ClassVar, Dict, List, Optional, Union

# Import third-party modules
from pydantic import BaseModel, Field, ValidationInfo, field_validator

# Import local modules
from notify_bridge.components import BaseNotifier, HTTPClientConfig, MessageType, NotificationError
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
    """Schema for WeCom notifications.

    Args:
        webhook_url: Webhook URL
        content: Message content
        mentioned_list: List of mentioned users
        mentioned_mobile_list: List of mentioned mobile numbers
        image_path: Path to image file
        media_id: Media ID for file/voice message
        media_path: Path to media file for file/voice message
        articles: List of articles
        color_map: Custom color mapping for markdown messages
    """

    webhook_url: str = Field(..., description="Webhook URL", alias="base_url")
    content: Optional[str] = Field(None, description="Message content", alias="message")
    mentioned_list: Optional[List[str]] = Field(default_factory=list, description="List of mentioned users")
    mentioned_mobile_list: Optional[List[str]] = Field(
        default_factory=list, description="List of mentioned mobile numbers"
    )
    image_path: Optional[str] = Field(None, description="Path to image file")
    media_id: Optional[str] = Field(None, description="Media ID for file/voice message")
    media_path: Optional[str] = Field(None, description="Path to media file for file/voice message")
    articles: Optional[List[Dict[str, Any]]] = Field(default_factory=list, description="List of articles")
    color_map: Optional[Dict[str, str]] = Field(
        default_factory=dict, description="Custom color mapping for markdown messages"
    )

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
        MessageType.MARKDOWN_V2,
        MessageType.IMAGE,
        MessageType.NEWS,
        MessageType.FILE,  #
        MessageType.VOICE,  #
    }

    def __init__(self, config: Optional[HTTPClientConfig] = None) -> None:
        """Initialize notifier.

        Args:
            config: HTTP client configuration.
        """
        super().__init__(config)
        self._webhook_key: Optional[str] = None

    def validate(self, data: Union[Dict[str, Any], WeComSchema]) -> WeComSchema:
        """Validate notification data.

        Args:
            data: Notification data.

        Returns:
            WeComSchema: Validated notification schema.

        Raises:
            NotificationError: If validation fails.
        """
        notification = super().validate(data)
        if not isinstance(notification, WeComSchema):
            raise NotificationError("data must be a WeComSchema instance")

        # Extract webhook key from webhook_url
        webhook_url = notification.webhook_url
        if webhook_url:
            self._webhook_key = webhook_url.split("key=")[-1].split("&")[0]

        return notification

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

    def _upload_media(self, file_path: str, media_type: str) -> str:
        """Upload media file to WeChat Work.

        Args:
            file_path: Path to media file
            media_type: Type of media file (file/voice)

        Returns:
            str: media_id

        Raises:
            NotificationError: If file not found or upload fails
        """
        path = Path(file_path)
        if not path.exists():
            raise NotificationError(f"File not found: {file_path}")

        # Check file size
        file_size = path.stat().st_size
        if file_size < 5:
            raise NotificationError("File size must be greater than 5 bytes")

        if media_type == "file" and file_size > 20 * 1024 * 1024:  # 20MB
            raise NotificationError("File size must not exceed 20MB")
        elif media_type == "voice" and file_size > 2 * 1024 * 1024:  # 2MB
            raise NotificationError("Voice file size must not exceed 2MB")

        # Extract webhook key from webhook_url
        if not hasattr(self, "_webhook_key"):
            raise NotificationError("Webhook URL not set")

        try:
            # Prepare multipart form data
            url = f"https://qyapi.weixin.qq.com/cgi-bin/webhook/upload_media?key={self._webhook_key}&type={media_type}"

            with open(file_path, "rb") as f:
                files = {"media": (path.name, f, "application/octet-stream")}
                response = self._ensure_sync_client().post(url, files=files)

            result = response.json()
            if result.get("errcode") != 0:
                raise NotificationError(f"Failed to upload file: {result.get('errmsg')}")

            media_id = result.get("media_id")
            if not media_id or not isinstance(media_id, str):
                raise NotificationError("Failed to upload media: invalid media_id")
            return media_id
        except Exception as e:
            raise NotificationError(f"Failed to upload file: {str(e)}")

    def _format_markdown(self, content: str, color_map: Optional[Dict[str, str]] = None) -> str:
        """Format markdown content.

        Args:
            content: The markdown content to format.
            color_map: Optional color mapping for text.

        Returns:
            str: The formatted markdown content.
        """
        # type: ignore[return]
        if not isinstance(content, str):
            raise NotificationError("Content must be a string")

        # Replace horizontal rules
        content = re.sub(r"^-{3,}$", "\n---\n", content, flags=re.MULTILINE)

        # Add support for colored text
        default_colors = {"info": "green", "comment": "gray", "warning": "orange-red"}
        colors = {**default_colors, **(color_map or {})}
        for color, _ in colors.items():
            content = content.replace(f'<font color="{color}">', f'<font color="{color}">')

        # Replace list markers for better visual effect
        content = re.sub(r"^\s*[-*+]\s+", "• ", content, flags=re.MULTILINE)  # Unordered lists

        # Convert ordered lists to use Chinese numbers for better visual effect
        def replace_ordered_list(match: re.Match[str]) -> str:
            num = int(match.group(1))
            chinese_nums = ["一", "二", "三", "四", "五", "六", "七", "八", "九", "十"]
            if 1 <= num <= 10:
                return f"{chinese_nums[num - 1]}、"
            return f"{num}."

        content = re.sub(r"^\s*(\d+)\.\s+", replace_ordered_list, content, flags=re.MULTILINE)

        # Format blockquotes
        content = re.sub(r"^\s*>\s*(.+)$", r"> \1", content, flags=re.MULTILINE)

        # Format inline code
        content = re.sub(r"`([^`]+)`", r"`\1`", content)

        # Format links
        content = re.sub(r"\[([^\]]+)\]\(([^)]+)\)", r"[\1](\2)", content)

        # Format bold text
        content = re.sub(r"\*\*([^*]+)\*\*", r"**\1**", content)

        # Format italic text
        content = re.sub(r"\*([^*]+)\*", r"*\1*", content)
        # Note: Preserve underscores as-is, do not convert to italic

        return content

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

        formatted_content = self._format_markdown(notification.content, notification.color_map)
        return {
            "msgtype": "markdown",
            "markdown": {
                "content": formatted_content,
                "mentioned_list": notification.mentioned_list,
                "mentioned_mobile_list": notification.mentioned_mobile_list,
            },
        }

    def _escape_markdown_v2(self, text: str) -> str:
        r"""Escape special characters for markdown_v2 format.

        According to WeCom official documentation example, only forward slash (/)
        needs to be escaped in markdown_v2 format.

        Args:
            text: The text to escape.

        Returns:
            str: The escaped text with forward slashes escaped.
        """
        # Based on official example, only forward slash needs to be escaped
        # Example from docs: [这是一个链接](https:work.weixin.qq.com\/api\/doc)
        return text.replace("/", r"\/")

    def _build_markdown_v2_payload(self, notification: WeComSchema) -> Dict[str, Any]:
        """Build markdown_v2 message payload.

        This method escapes special characters according to WeCom markdown_v2 specification.

        Args:
            notification: Notification data.

        Returns:
            Dict[str, Any]: Markdown_v2 message payload.

        Raises:
            NotificationError: If content is missing.
        """
        if not notification.content:
            raise NotificationError("content is required for markdown_v2 messages")

        # Escape special characters for markdown_v2
        escaped_content = self._escape_markdown_v2(notification.content)

        return {
            "msgtype": "markdown",
            "markdown": {
                "content": escaped_content,
                "mentioned_list": notification.mentioned_list,
                "mentioned_mobile_list": notification.mentioned_mobile_list,
            },
        }

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

    def _build_file_payload(self, notification: WeComSchema) -> Dict[str, Any]:
        """Build file message payload.

        Args:
            notification: Notification data.

        Returns:
            Dict[str, Any]: File message payload.

        Raises:
            NotificationError: If media_id is missing.
        """
        if not notification.media_id and not notification.media_path:
            raise NotificationError("Either media_id or media_path is required for file message")

        media_id = notification.media_id
        if not media_id and notification.media_path:
            media_id = self._upload_media(notification.media_path, "file")

        return {"msgtype": "file", "file": {"media_id": media_id}}

    def _build_voice_payload(self, notification: WeComSchema) -> Dict[str, Any]:
        """Build voice message payload.

        Args:
            notification: Notification data.

        Returns:
            Dict[str, Any]: Voice message payload.

        Raises:
            NotificationError: If media_id is missing.
        """
        if not notification.media_id and not notification.media_path:
            raise NotificationError("Either media_id or media_path is required for voice message")

        media_id = notification.media_id
        if not media_id and notification.media_path:
            media_id = self._upload_media(notification.media_path, "voice")

        return {"msgtype": "voice", "voice": {"media_id": media_id}}

    def assemble_data(self, data: WeComSchema) -> Dict[str, Any]:
        """Assemble data data.

        Args:
            data: Notification data

        Returns:
            Dict[str, Any]: API payload
        """
        if not isinstance(data, WeComSchema):
            raise NotificationError("data must be a WeComSchema instance")

        # For MARKDOWN_V2, the msgtype should still be "markdown"
        msgtype = "markdown" if data.msg_type == MessageType.MARKDOWN_V2 else data.msg_type
        payload = {"msgtype": msgtype}
        if data.msg_type == MessageType.TEXT:
            payload.update(self._build_text_payload(data))
        elif data.msg_type == MessageType.MARKDOWN:
            payload.update(self._build_markdown_payload(data))
        elif data.msg_type == MessageType.MARKDOWN_V2:
            payload.update(self._build_markdown_v2_payload(data))
        elif data.msg_type == MessageType.IMAGE:
            payload.update(self._build_image_payload(data))
        elif data.msg_type == MessageType.NEWS:
            payload.update(self._build_news_payload(data))
        elif data.msg_type == MessageType.FILE:
            payload.update(self._build_file_payload(data))
        elif data.msg_type == MessageType.VOICE:
            payload.update(self._build_voice_payload(data))
        else:
            raise NotificationError(f"Unsupported message type: {data.msg_type}")

        return payload
