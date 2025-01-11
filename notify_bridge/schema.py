"""Type definitions for notify-bridge.

This module contains all the base schemas and type definitions used in notify-bridge.
"""

# Import built-in modules
from enum import Enum
from typing import Any
from typing import DefaultDict
from typing import Dict
from typing import List
from typing import Optional

# Import third-party modules
from pydantic import BaseModel
from pydantic import EmailStr
from pydantic import Field
from pydantic import SecretStr
from pydantic import field_validator
from pydantic import model_validator


class NotifyLevel(str, Enum):
    """Notification level enum."""

    DEBUG = "debug"
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


class BaseSchema(BaseModel):
    """Base schema for all notification schemas."""

    url: Optional[str] = None
    title: Optional[str] = None
    content: Optional[str] = None
    msg_type: Optional[str] = None
    webhook_url: Optional[str] = None
    method: str = "POST"
    headers: Dict[str, Any] = {}
    payload: Dict[str, Any] = {}
    timeout: Optional[float] = None
    verify_ssl: bool = True

    def to_payload(self) -> Dict[str, Any]:
        """Convert schema to payload."""
        return {
            "url": str(self.url) if self.url else None,
            "title": self.title,
            "content": self.content,
            "msg_type": self.msg_type,
            **self.payload,
        }


class NotificationSchema(BaseSchema):
    """Base notification schema.

    This is the most basic schema that all notifiers must implement.
    Platform-specific fields should be added in platform-specific schemas.
    """

    url: str = Field(..., description="Notification endpoint URL")
    title: Optional[str] = Field(None, description="Message title")
    content: Optional[str] = Field(None, description="Message content")
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

    @model_validator(mode="before")
    @classmethod
    def transform_fields(cls, data: Dict[str, Any]) -> Dict[str, Any]:
        """Transform input fields.

        This method should be overridden by subclasses to implement
        platform-specific field transformations.

        Args:
            data: Raw input data.

        Returns:
            Dict[str, Any]: Transformed data.
        """
        return data


class WebhookSchema(NotificationSchema):
    """Schema for webhook notifications."""

    webhook_url: str = Field(..., description="Webhook URL")
    method: str = Field("POST", description="HTTP method")
    headers: DefaultDict[str, str] = Field(default_factory=dict, description="HTTP headers")
    payload: dict[str, Any] = Field(default_factory=dict, description="Webhook payload")
    timeout: Optional[float] = Field(None, description="Request timeout")
    verify_ssl: bool = Field(True, description="Verify SSL certificate")

    @field_validator("method")
    @classmethod
    def validate_method(cls, v: str) -> str:
        """Validate HTTP method.

        Args:
            v: HTTP method

        Returns:
            Validated HTTP method

        Raises:
            ValueError: If method is invalid

        """
        methods = {"GET", "POST", "PUT", "PATCH", "DELETE"}
        if v.upper() not in methods:
            raise ValueError(f"Invalid HTTP method: {v}")
        return v.upper()

    def to_payload(self) -> Dict[str, Any]:
        """Convert schema to payload.

        Returns:
            Dict[str, Any]: Webhook payload

        """
        payload = self.payload.copy()
        if self.content:
            payload["content"] = self.content
        return payload


class EmailSchema(NotificationSchema):
    """Schema for email notifications."""

    subject: str = Field(description="Subject of the email")
    from_email: EmailStr = Field(description="Sender email address")
    to_emails: List[EmailStr] = Field(description="List of recipient email addresses")
    cc_emails: List[EmailStr] = Field(default_factory=list, description="List of CC email addresses")
    bcc_emails: List[EmailStr] = Field(default_factory=list, description="List of BCC email addresses")
    html_content: Optional[str] = Field(None, description="HTML content of the email")
    attachments: List[str] = Field(default_factory=list, description="List of attachment paths")

    @model_validator(mode="before")
    @classmethod
    def validate_email_lists(cls, values: Dict[str, Any]) -> Dict[str, Any]:
        """Validate email lists."""
        for field in ["to_emails", "cc_emails", "bcc_emails"]:
            if field in values and not values[field]:
                values[field] = []
        return values

    def to_payload(self) -> Dict[str, Any]:
        """Convert schema to email payload.

        Returns:
            Dict[str, Any]: Email payload

        """
        payload = super().to_payload()
        if self.html_content:
            payload["html_content"] = self.html_content
        return payload


class NotificationResponse(BaseModel):
    """Response from a notification attempt."""

    success: bool = Field(description="Whether the notification was successful")
    name: str = Field(description="Name of the notifier")
    message: Optional[str] = Field(default=None, description="Optional message")
    data: Optional[Dict[str, Any]] = Field(default=None, description="Optional data")


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
