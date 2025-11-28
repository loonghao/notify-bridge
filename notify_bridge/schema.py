"""Type definitions for notify-bridge.

This module contains all the base schemas and type definitions used in notify-bridge.
"""

# Import built-in modules
from enum import Enum
from typing import Any, Dict, List, Optional, Union

# Import third-party modules
from pydantic import AliasChoices, BaseModel, Field, SecretStr


class MessageType(str, Enum):
    """Message types supported by notifiers."""

    TEXT = "text"
    MARKDOWN = "markdown"
    MARKDOWN_V2 = "markdown_v2"
    NEWS = "news"
    POST = "post"
    IMAGE = "image"
    FILE = "file"
    VOICE = "voice"
    INTERACTIVE = "interactive"
    UPLOAD_MEDIA = "upload_media"
    TEMPLATE_CARD = "template_card"


class NotifyLevel(str, Enum):
    """Notification level enum."""

    DEBUG = "debug"
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


class BaseSchema(BaseModel):
    """Base schema for all data schemas.

    This class provides the most basic fields that all notifiers might need.
    Platform-specific fields should be added in platform-specific schemas.
    """

    model_config = {"extra": "allow", "populate_by_name": True}

    def to_payload(self) -> Dict[str, Any]:
        """Convert schema to payload.

        Returns:
            Dict[str, Any]: Payload data.
        """
        return dict(self.model_dump(exclude_none=True))


class HTTPSchema(BaseSchema):
    """Schema for HTTP-based operations.

    This schema provides common fields for HTTP operations like webhooks and APIs.
    """

    url: str = Field(
        ...,
        description="HTTP URL",
        validation_alias=AliasChoices("url", "webhook_url", "base_url"),
    )
    method: str = Field("POST", description="HTTP method")
    headers: Dict[str, Any] = Field(default_factory=dict, description="HTTP headers")
    timeout: Optional[float] = Field(None, description="Request timeout in seconds")
    verify_ssl: bool = Field(True, description="Whether to verify SSL certificates")


class NotificationSchema(HTTPSchema):
    """Schema for notifications.

    This schema provides common fields for all notification types.
    Platform-specific fields should be added in platform-specific schemas.
    """

    title: Optional[str] = Field(None, description="Message title")
    content: Optional[str] = Field(None, description="Message content", alias="message")
    msg_type: str = Field("text", description="Message type")


class WebhookSchema(NotificationSchema):
    """Schema for webhook notifications.

    This schema is used for platforms that use webhooks for notifications,
    such as Slack, Discord, and WeChat Work.
    """

    webhook_url: Optional[str] = Field(None, description="Webhook URL")
    title: Optional[str] = Field(None, description="Message title")
    content: Optional[str] = Field(None, description="Message content", alias="message")

    @property
    def url(self) -> str:
        """Get URL.

        Returns:
            str: URL.
        """
        return self.webhook_url or ""

    @url.setter
    def url(self, value: str) -> None:
        """Set URL.

        Args:
            value: URL.
        """
        self.webhook_url = value


class APISchema(NotificationSchema):
    """Schema for API-based notifications.

    This schema is used for platforms that use REST APIs for notifications,
    such as GitHub Issues and Telegram.
    """

    token: str = Field(..., description="API token or access key")


class EmailSchema(NotificationSchema):
    """Schema for email notifications.

    This schema is used for sending notifications via email,
    supporting both SMTP and API-based email services.
    """

    host: str = Field(..., description="SMTP server host or API endpoint")
    port: int = Field(..., description="SMTP server port or API port")
    username: str = Field(..., description="SMTP username or API key")
    password: str = Field(..., description="SMTP password or API secret")
    from_email: str = Field(..., description="Sender email address")
    to_email: Union[str, List[str]] = Field(..., description="Recipient email address(es)")
    subject: str = Field(..., description="Email subject")
    is_ssl: bool = Field(True, description="Whether to use SSL/TLS")


class NotificationResponse(BaseModel):
    """Response data for notification."""

    success: bool = Field(description="Success status")
    name: str = Field(description="Notifier name")
    message: str = Field(description="Response message")
    data: Dict[str, Any] = Field(description="Response data")

    def __eq__(self, other: object) -> bool:
        """Compare response data.

        Args:
            other: Other response data

        Returns:
            bool: True if equal
        """
        if not isinstance(other, NotificationResponse):
            return False
        return (
            self.success == other.success
            and self.name == other.name
            and self.message == other.message
            and self.data == other.data
        )

    def __hash__(self) -> int:
        """Hash response data.

        Returns:
            int: Hash value
        """
        return hash((self.success, self.name, self.message, str(self.data)))


class AuthType(str, Enum):
    """Authentication type enum."""

    NONE = "none"
    BASIC = "basic"
    BEARER = "bearer"
    OAUTH = "oauth"
    API_KEY = "api_key"
    CUSTOM = "custom"


class AuthSchema(BaseSchema):
    """Base schema for authentication.

    This schema is used to define authentication parameters.
    """

    auth_type: AuthType = Field(default=AuthType.NONE, description="Authentication type")
    username: Optional[str] = Field(None, description="Username for basic auth")
    password: Optional[SecretStr] = Field(None, description="Password for basic auth")
    token: Optional[SecretStr] = Field(None, description="Token for bearer auth")
    api_key: Optional[SecretStr] = Field(None, description="API key")
    api_key_name: Optional[str] = Field(None, description="API key parameter name")
    api_key_location: Optional[str] = Field(None, description="API key location (header, query, cookie)")
    oauth_config: Optional[Dict[str, Any]] = Field(None, description="OAuth configuration")
    custom_auth: Optional[Dict[str, Any]] = Field(None, description="Custom authentication parameters")

    def to_headers(self) -> Dict[str, str]:
        """Convert auth schema to headers.

        Returns:
            Dict containing authentication headers
        """
        headers = {}
        if self.auth_type == AuthType.BASIC and self.username and self.password:
            # Import built-in modules
            import base64

            auth_str = f"{self.username}:{self.password.get_secret_value()}"
            auth_bytes = auth_str.encode("utf-8")
            headers["Authorization"] = f"Basic {base64.b64encode(auth_bytes).decode()}"
        elif self.auth_type == AuthType.BEARER and self.token:
            headers["Authorization"] = f"Bearer {self.token.get_secret_value()}"
        elif self.auth_type == AuthType.API_KEY and self.api_key:
            if self.api_key_location == "header":
                headers[self.api_key_name or "X-API-Key"] = self.api_key.get_secret_value()
        elif self.auth_type == AuthType.CUSTOM and self.custom_auth:
            headers.update(self.custom_auth)
        return headers
