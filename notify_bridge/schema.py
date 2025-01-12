"""Type definitions for notify-bridge.

This module contains all the base schemas and type definitions used in notify-bridge.
"""

# Import built-in modules
from enum import Enum
from typing import Any, DefaultDict, Dict, List, Optional, Union

# Import third-party modules
from pydantic import BaseModel, EmailStr, Field, SecretStr, field_validator, model_validator



class MessageType(str, Enum):
    """Message types supported by notifiers."""

    TEXT = "text"
    MARKDOWN = "markdown"
    NEWS = "news"
    POST = "post"
    IMAGE = "image"
    FILE = "file"
    INTERACTIVE = "interactive"

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

    content: str = Field(..., description="Message content")
    headers: Dict[str, Any] = Field(default_factory=dict, description="HTTP headers")

    def to_payload(self) -> Dict[str, Any]:
        """Convert schema to payload.

        This method should be overridden by subclasses to implement
        platform-specific payload transformations.

        Returns:
            Dict[str, Any]: Payload for the notification.
        """
        return self.model_dump(exclude_none=True)

    class Config:
        """Pydantic model configuration."""
        extra = "allow"  # Allow extra fields for platform-specific needs


class NotificationSchema(BaseSchema):
    """Base notification schema.

    This schema provides the most basic fields for sending notifications.
    Platform-specific fields should be added in platform-specific schemas.
    """

    title: Optional[str] = Field(None, description="Message title")
    msg_type: Optional[str] = Field(None, description="Message type")

    @model_validator(mode="before")
    @classmethod
    def convert_webhook_url(cls, data: Dict[str, Any]) -> Dict[str, Any]:
        """Convert webhook_url to url.

        Args:
            data: Data to validate.

        Returns:
            Dict[str, Any]: Validated data.
        """
        if "webhook_url" in data and "url" not in data:
            data["url"] = data["webhook_url"]
        return data


class WebhookSchema(NotificationSchema):
    """Schema for webhook notifications.

    This schema is used for platforms that use webhooks for notifications,
    such as Slack, Discord, and WeChat Work.
    """

    url: str = Field(..., description="Webhook URL")
    method: str = Field("POST", description="HTTP method")
    headers: Dict[str, Any] = Field(default_factory=dict, description="HTTP headers")
    timeout: Optional[float] = Field(None, description="Request timeout in seconds")
    verify_ssl: bool = Field(True, description="Whether to verify SSL certificates")


class APISchema(NotificationSchema):
    """Schema for API-based notifications.

    This schema is used for platforms that use REST APIs for notifications,
    such as GitHub Issues and Telegram.
    """

    base_url: str = Field(..., description="Base API URL")
    token: str = Field(..., description="API token or access key")
    method: str = Field("POST", description="HTTP method")
    headers: Dict[str, Any] = Field(default_factory=dict, description="HTTP headers")
    timeout: Optional[float] = Field(None, description="Request timeout in seconds")
    verify_ssl: bool = Field(True, description="Whether to verify SSL certificates")


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
    timeout: Optional[float] = Field(None, description="Connection timeout in seconds")


class NotificationResponse(BaseModel):
    """Response data for notification."""

    success: bool = Field(description="Success status")
    name: str = Field(description="Notifier name")
    message: str = Field(description="Response message")
    data: Dict[str, Any] = Field(description="Response data")

    def __init__(self, **data: Dict[str, Any]) -> None:
        """Initialize response data.

        Args:
            **data: Response data
        """
        super().__init__(**data)

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


class AuthSchema(BaseModel):
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

        if self.auth_type == AuthType.BASIC:
            if self.username and self.password:
                # Import built-in modules
                import base64

                auth_str = f"{self.username}:{self.password.get_secret_value()}"
                auth_bytes = base64.b64encode(auth_str.encode()).decode()
                headers["Authorization"] = f"Basic {auth_bytes}"

        elif self.auth_type == AuthType.BEARER:
            if self.token:
                headers["Authorization"] = f"Bearer {self.token.get_secret_value()}"

        elif self.auth_type == AuthType.API_KEY:
            if self.api_key and self.api_key_name:
                if self.api_key_location == "header":
                    headers[self.api_key_name] = self.api_key.get_secret_value()

        return headers

    class Config:
        """Pydantic model configuration."""

        arbitrary_types_allowed = True
