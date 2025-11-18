"""WeCom notifier implementation.

This module provides the WeCom (WeChat Work) notification implementation.
"""

# Import built-in modules
import base64
import logging
import re
from pathlib import Path
from typing import Any, Callable, ClassVar, Dict, List, Optional, Union

# Import third-party modules
from pydantic import BaseModel, Field, ValidationInfo, field_validator

# Import local modules
from notify_bridge.components import BaseNotifier, HTTPClientConfig, MessageType, NotificationError
from notify_bridge.schema import NotificationResponse, WebhookSchema

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


class TemplateCardSource(BaseModel):
    """Source schema for template card."""

    icon_url: Optional[str] = Field(None, description="Icon URL")
    desc: Optional[str] = Field(None, description="Description, max 13 characters")
    desc_color: Optional[int] = Field(None, description="Description color: 0(grey), 1(black), 2(red), 3(green)")

    class Config:
        """Pydantic model configuration."""

        populate_by_name = True


class TemplateCardMainTitle(BaseModel):
    """Main title schema for template card."""

    title: Optional[str] = Field(None, description="Title, max 26 characters")
    desc: Optional[str] = Field(None, description="Description, max 30 characters")

    class Config:
        """Pydantic model configuration."""

        populate_by_name = True


class TemplateCardEmphasisContent(BaseModel):
    """Emphasis content schema for template card."""

    title: Optional[str] = Field(None, description="Title, max 10 characters")
    desc: Optional[str] = Field(None, description="Description, max 15 characters")

    class Config:
        """Pydantic model configuration."""

        populate_by_name = True


class TemplateCardQuoteArea(BaseModel):
    """Quote area schema for template card."""

    type: Optional[int] = Field(None, description="Quote type: 0(no click), 1(url), 2(mini program)")
    url: Optional[str] = Field(None, description="Click URL, required when type=1")
    appid: Optional[str] = Field(None, description="Mini program appid, required when type=2")
    pagepath: Optional[str] = Field(None, description="Mini program pagepath, required when type=2")
    title: Optional[str] = Field(None, description="Quote title")
    quote_text: Optional[str] = Field(None, description="Quote text")

    class Config:
        """Pydantic model configuration."""

        populate_by_name = True


class TemplateCardHorizontalContentItem(BaseModel):
    """Horizontal content item schema for template card."""

    keyname: str = Field(..., description="Key name, max 5 characters")
    value: Optional[str] = Field(None, description="Value, max 26 characters (including file type)")
    type: Optional[int] = Field(None, description="Type: 1(url), 2(file), 3(userid)")
    url: Optional[str] = Field(None, description="Click URL, required when type=1")
    media_id: Optional[str] = Field(None, description="Media ID, required when type=2")
    userid: Optional[str] = Field(None, description="User ID, required when type=3")

    class Config:
        """Pydantic model configuration."""

        populate_by_name = True


class TemplateCardJumpItem(BaseModel):
    """Jump item schema for template card."""

    type: int = Field(..., description="Jump type: 1(url), 2(mini program)")
    title: str = Field(..., description="Jump title, max 13 characters")
    url: Optional[str] = Field(None, description="Jump URL, required when type=1")
    appid: Optional[str] = Field(None, description="Mini program appid, required when type=2")
    pagepath: Optional[str] = Field(None, description="Mini program pagepath, required when type=2")

    class Config:
        """Pydantic model configuration."""

        populate_by_name = True


class TemplateCardAction(BaseModel):
    """Card action schema for template card."""

    type: int = Field(..., description="Action type: 1(url), 2(mini program)")
    url: Optional[str] = Field(None, description="Action URL, required when type=1")
    appid: Optional[str] = Field(None, description="Mini program appid, required when type=2")
    pagepath: Optional[str] = Field(None, description="Mini program pagepath, required when type=2")

    class Config:
        """Pydantic model configuration."""

        populate_by_name = True


class TemplateCardImage(BaseModel):
    """Card image schema for template card."""

    url: str = Field(..., description="Image URL")
    aspect_ratio: Optional[float] = Field(None, description="Image aspect ratio, default 2.25, max 1.3")

    class Config:
        """Pydantic model configuration."""

        populate_by_name = True


class TemplateCardImageTextArea(BaseModel):
    """Image text area schema for template card."""

    type: Optional[int] = Field(None, description="Type: 0(no click), 1(url), 2(mini program)")
    url: Optional[str] = Field(None, description="Click URL, required when type=1")
    appid: Optional[str] = Field(None, description="Mini program appid, required when type=2")
    pagepath: Optional[str] = Field(None, description="Mini program pagepath, required when type=2")
    title: Optional[str] = Field(None, description="Left and right style title")
    desc: Optional[str] = Field(None, description="Left and right style description")
    image_url: str = Field(..., description="Left and right style image URL")

    class Config:
        """Pydantic model configuration."""

        populate_by_name = True


class TemplateCardVerticalContentItem(BaseModel):
    """Vertical content item schema for template card."""

    title: str = Field(..., description="Secondary title, max 26 characters")
    desc: Optional[str] = Field(None, description="Secondary description, max 112 characters")

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
        upload_media_type: Media type for upload_media message (file/voice)
        template_card_type: Template card type (text_notice/news_notice)
        template_card_source: Template card source information
        template_card_main_title: Template card main title
        template_card_emphasis_content: Template card emphasis content (text_notice only)
        template_card_quote_area: Template card quote area
        template_card_sub_title_text: Template card sub title text (text_notice only)
        template_card_horizontal_content_list: Template card horizontal content list
        template_card_jump_list: Template card jump list
        template_card_card_action: Template card action
        template_card_image: Template card image (news_notice only)
        template_card_image_text_area: Template card image text area (news_notice only)
        template_card_vertical_content_list: Template card vertical content list (news_notice only)
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
    upload_media_type: Optional[str] = Field("file", description="Media type for upload_media message (file/voice)")
    # Template card fields
    template_card_type: Optional[str] = Field("text_notice", description="Template card type")
    template_card_source: Optional[Union[Dict[str, Any], TemplateCardSource]] = Field(
        None, description="Template card source"
    )
    template_card_main_title: Optional[Union[Dict[str, Any], TemplateCardMainTitle]] = Field(
        None, description="Template card main title"
    )
    template_card_emphasis_content: Optional[Union[Dict[str, Any], TemplateCardEmphasisContent]] = Field(
        None, description="Template card emphasis content"
    )
    template_card_quote_area: Optional[Union[Dict[str, Any], TemplateCardQuoteArea]] = Field(
        None, description="Template card quote area"
    )
    template_card_sub_title_text: Optional[str] = Field(None, description="Template card sub title text, max 112 chars")
    template_card_horizontal_content_list: Optional[List[Union[Dict[str, Any], TemplateCardHorizontalContentItem]]] = (
        Field(None, description="Template card horizontal content list, max 6 items")
    )
    template_card_jump_list: Optional[List[Union[Dict[str, Any], TemplateCardJumpItem]]] = Field(
        None, description="Template card jump list, max 3 items"
    )
    template_card_card_action: Optional[Union[Dict[str, Any], TemplateCardAction]] = Field(
        None, description="Template card action"
    )
    # Template card fields for news_notice type
    template_card_image: Optional[Union[Dict[str, Any], TemplateCardImage]] = Field(
        None, description="Template card image (news_notice only)"
    )
    template_card_image_text_area: Optional[Union[Dict[str, Any], TemplateCardImageTextArea]] = Field(
        None, description="Template card image text area (news_notice only)"
    )
    template_card_vertical_content_list: Optional[List[Union[Dict[str, Any], TemplateCardVerticalContentItem]]] = Field(
        None, description="Template card vertical content list (news_notice only), max 4 items"
    )

    @field_validator("content")
    @classmethod
    def validate_content(cls, v: Optional[str], info: ValidationInfo) -> Optional[str]:
        """Validate content field.

        Content is required for text, markdown and markdown_v2 messages, optional for others.
        """
        msg_type = info.data.get("msg_type")
        if msg_type in (MessageType.TEXT, MessageType.MARKDOWN, MessageType.MARKDOWN_V2) and not v:
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
        MessageType.UPLOAD_MEDIA,  # Not officially supported by WeCom webhook API, exposed for convenience
        MessageType.TEMPLATE_CARD,
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
            "msgtype": "markdown_v2",
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

    def _build_upload_media_payload(self, notification: WeComSchema) -> Dict[str, Any]:
        """Build upload_media payload.

        Note: This is NOT an official WeCom webhook message type.
        This message type is exposed for convenience to allow direct access to the
        upload_media API endpoint. It uploads a media file and returns the media_id.

        Official documentation:
        https://developer.work.weixin.qq.com/document/path/91770#%E6%96%87%E4%BB%B6%E4%B8%8A%E4%BC%A0%E6%8E%A5%E5%8F%A3

        Args:
            notification: Notification data.

        Returns:
            Dict[str, Any]: Upload media response with media_id.

        Raises:
            NotificationError: If media_path is missing or upload fails.
        """
        if not notification.media_path:
            raise NotificationError("media_path is required for upload_media message")

        media_type = notification.upload_media_type or "file"
        if media_type not in ("file", "voice"):
            raise NotificationError(f"Invalid upload_media_type: {media_type}. Must be 'file' or 'voice'")

        media_id = self._upload_media(notification.media_path, media_type)
        return {"media_id": media_id, "type": media_type}

    def _convert_to_dict(self, data: Union[Dict[str, Any], BaseModel]) -> Dict[str, Any]:
        """Convert data to dictionary.

        Args:
            data: Data to convert (dict or BaseModel instance).

        Returns:
            Dict[str, Any]: Converted dictionary.
        """
        if isinstance(data, dict):
            return data
        return data.model_dump(exclude_none=True)

    def _convert_list_to_dict(self, items: List[Union[Dict[str, Any], BaseModel]]) -> List[Dict[str, Any]]:
        """Convert list of items to list of dictionaries.

        Args:
            items: List of items to convert.

        Returns:
            List[Dict[str, Any]]: List of dictionaries.
        """
        return [self._convert_to_dict(item) for item in items]

    def _add_template_card_field(self, template_card: Dict[str, Any], field_name: str, field_value: Any) -> None:
        """Add a field to template card if provided.

        Args:
            template_card: Template card dictionary.
            field_name: Field name.
            field_value: Field value.
        """
        if field_value is None:
            return

        if isinstance(field_value, (str, int, float)):
            template_card[field_name] = field_value
        elif isinstance(field_value, list):
            converted_list = self._convert_list_to_dict(field_value)
            if converted_list:
                template_card[field_name] = converted_list
        else:
            converted_data = self._convert_to_dict(field_value)
            if converted_data:
                template_card[field_name] = converted_data

    def _build_template_card_payload(self, notification: WeComSchema) -> Dict[str, Any]:
        """Build template card message payload.

        Args:
            notification: Notification data.

        Returns:
            Dict[str, Any]: Template card message payload.

        Raises:
            NotificationError: If required fields are missing.
        """
        template_card: Dict[str, Any] = {
            "card_type": notification.template_card_type or "text_notice",
        }

        # Add all template card fields
        self._add_template_card_field(template_card, "source", notification.template_card_source)
        self._add_template_card_field(template_card, "main_title", notification.template_card_main_title)
        self._add_template_card_field(template_card, "emphasis_content", notification.template_card_emphasis_content)
        self._add_template_card_field(template_card, "quote_area", notification.template_card_quote_area)
        self._add_template_card_field(template_card, "sub_title_text", notification.template_card_sub_title_text)
        self._add_template_card_field(
            template_card, "horizontal_content_list", notification.template_card_horizontal_content_list
        )
        self._add_template_card_field(template_card, "jump_list", notification.template_card_jump_list)
        self._add_template_card_field(template_card, "card_action", notification.template_card_card_action)
        self._add_template_card_field(template_card, "card_image", notification.template_card_image)
        self._add_template_card_field(template_card, "image_text_area", notification.template_card_image_text_area)
        self._add_template_card_field(
            template_card, "vertical_content_list", notification.template_card_vertical_content_list
        )

        return {"msgtype": "template_card", "template_card": template_card}

    def _get_payload_builder(self, msg_type: MessageType) -> Callable[[WeComSchema], Dict[str, Any]]:
        """Get the appropriate payload builder for the message type.

        Args:
            msg_type: Message type.

        Returns:
            Callable: Payload builder function.

        Raises:
            NotificationError: If message type is not supported.
        """
        builders: Dict[MessageType, Callable[[WeComSchema], Dict[str, Any]]] = {
            MessageType.TEXT: self._build_text_payload,
            MessageType.MARKDOWN: self._build_markdown_payload,
            MessageType.MARKDOWN_V2: self._build_markdown_v2_payload,
            MessageType.IMAGE: self._build_image_payload,
            MessageType.NEWS: self._build_news_payload,
            MessageType.FILE: self._build_file_payload,
            MessageType.VOICE: self._build_voice_payload,
            MessageType.TEMPLATE_CARD: self._build_template_card_payload,
        }

        if msg_type not in builders:
            raise NotificationError(f"Unsupported message type: {msg_type}")

        return builders[msg_type]

    def assemble_data(self, data: WeComSchema) -> Dict[str, Any]:
        """Assemble data data.

        Args:
            data: Notification data

        Returns:
            Dict[str, Any]: API payload
        """
        if not isinstance(data, WeComSchema):
            raise NotificationError("data must be a WeComSchema instance")

        # For UPLOAD_MEDIA, this should not be called via normal send flow
        # It's handled separately in send() and send_async()
        if data.msg_type == MessageType.UPLOAD_MEDIA:
            raise NotificationError(
                "UPLOAD_MEDIA should be handled via send() or send_async() methods, not assemble_data()"
            )

        # Use msg_type directly - WeChat Work API supports markdown_v2
        payload = {"msgtype": data.msg_type}

        # Get the appropriate builder and build the payload
        msg_type_enum = MessageType(data.msg_type)
        builder = self._get_payload_builder(msg_type_enum)
        payload.update(builder(data))

        return payload

    def send(self, notification_data: Union[Dict[str, Any], WeComSchema]) -> NotificationResponse:
        """Send notification.

        Args:
            notification_data: Notification data.

        Returns:
            NotificationResponse: Notification response.

        Raises:
            NotificationError: If notification fails.
        """
        try:
            notification = self.validate(notification_data)

            # Special handling for UPLOAD_MEDIA
            if notification.msg_type == MessageType.UPLOAD_MEDIA:
                result = self._build_upload_media_payload(notification)
                return NotificationResponse(
                    success=True,
                    name=self.name,
                    message="Media uploaded successfully",
                    data=result,
                )

            # Normal flow for other message types
            return super().send(notification)
        except Exception as e:
            raise NotificationError(str(e), notifier_name=self.name)

    async def send_async(self, notification_data: Union[Dict[str, Any], WeComSchema]) -> NotificationResponse:
        """Send notification asynchronously.

        Args:
            notification_data: Notification data.

        Returns:
            NotificationResponse: Notification response.

        Raises:
            NotificationError: If notification fails.
        """
        try:
            notification = self.validate(notification_data)

            # Special handling for UPLOAD_MEDIA
            if notification.msg_type == MessageType.UPLOAD_MEDIA:
                result = self._build_upload_media_payload(notification)
                return NotificationResponse(
                    success=True,
                    name=self.name,
                    message="Media uploaded successfully",
                    data=result,
                )

            # Normal flow for other message types
            return await super().send_async(notification)
        except Exception as e:
            raise NotificationError(str(e), notifier_name=self.name)
