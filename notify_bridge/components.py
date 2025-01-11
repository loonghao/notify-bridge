"""Core components for notify-bridge.

This module contains the base notifier classes and core functionality.
"""

# Import built-in modules
from abc import ABC
from abc import abstractmethod
from enum import Enum
from typing import Any
from typing import ClassVar
from typing import Dict
from typing import Optional
from typing import Type
from typing import Union

# Import third-party modules
from pydantic import BaseModel
from pydantic import Field
from pydantic import ValidationError

# Import local modules
from notify_bridge.exceptions import NotificationError
from notify_bridge.utils import AsyncHTTPClient
from notify_bridge.utils import HTTPClient
from notify_bridge.utils import HTTPClientConfig


class MessageType(str, Enum):
    """Message types supported by notifiers."""

    TEXT = "text"
    MARKDOWN = "markdown"
    NEWS = "news"
    POST = "post"
    IMAGE = "image"
    FILE = "file"
    INTERACTIVE = "interactive"


class NotificationSchema(BaseModel):
    """Base schema for all notifications."""

    content: str = Field(..., description="Message content", alias="message")
    title: Optional[str] = Field(None, description="Message title")
    msg_type: MessageType = Field(MessageType.TEXT, description="Message type")
    webhook_url: Optional[str] = Field(None, description="Webhook URL", alias="base_url")
    headers: Dict[str, str] = Field(
        default_factory=lambda: {"Content-Type": "application/json"}, description="HTTP headers"
    )
    labels: Optional[list[str]] = Field(None, description="Labels or tags", alias="tags")
    token: Optional[str] = Field(None, description="Authentication token")
    owner: Optional[str] = Field(None, description="Repository owner")
    repo: Optional[str] = Field(None, description="Repository name")

    def to_payload(self) -> Dict[str, Any]:
        """Convert to API payload.

        Returns:
            Dict[str, Any]: API payload.
        """
        return self.model_dump(exclude_none=True)

    class Config:
        """Pydantic model configuration."""

        extra = "allow"
        populate_by_name = True


class NotificationResponse(BaseModel):
    """Response schema for notifications."""

    success: bool = Field(..., description="Whether the notification was successful")
    name: str = Field(..., description="Name of the notifier")
    message: str = Field(..., description="Response message")
    data: Optional[Dict[str, Any]] = Field(None, description="Additional response data")


class AbstractNotifier(ABC):
    """Abstract base class for all notifiers."""

    name: str = ""
    schema_class: Type[NotificationSchema] = NotificationSchema
    supported_types: ClassVar[set[MessageType]] = {MessageType.TEXT}

    def __init__(self, config: Optional[HTTPClientConfig] = None) -> None:
        """Initialize notifier.

        Args:
            config: HTTP client configuration.
        """
        self._config = config or HTTPClientConfig()
        self._http_client = HTTPClient(self._config)
        self._async_http_client = AsyncHTTPClient(self._config)

    def _validate_message_type(self, msg_type: Union[MessageType, str]) -> None:
        """Validate message type.

        Args:
            msg_type: Message type to validate.

        Raises:
            NotificationError: If message type is not supported.
        """
        if isinstance(msg_type, str):
            try:
                msg_type = MessageType(msg_type)
            except ValueError:
                raise NotificationError(f"Invalid message type: {msg_type}")

        if msg_type not in self.supported_types:
            raise NotificationError(
                f"Unsupported message type: {msg_type}. "
                f"Supported types: {', '.join(t.value for t in self.supported_types)}"
            )

    def validate(self, notification: Union[Dict[str, Any], NotificationSchema]) -> NotificationSchema:
        """Validate notification data.

        Args:
            notification: Notification data.

        Returns:
            NotificationSchema: Validated notification schema.

        Raises:
            NotificationError: If validation fails.
        """
        if isinstance(notification, dict):
            try:
                notification = self.schema_class(**notification)
            except ValidationError as e:
                raise NotificationError(f"Invalid notification data: {str(e)}")
        elif not isinstance(notification, self.schema_class):
            try:
                notification = self.schema_class(**notification.model_dump())
            except ValidationError as e:
                raise NotificationError(f"Invalid notification data: {str(e)}")
        return notification

    @abstractmethod
    def build_payload(self, notification: NotificationSchema) -> Dict[str, Any]:
        """Build notification payload.

        Args:
            notification: Notification data.

        Returns:
            Dict[str, Any]: API payload.

        Raises:
            NotificationError: If notification is not valid.
        """
        pass

    def send(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Send notification.

        Args:
            data: Notification data.

        Returns:
            Dict[str, Any]: Response data.

        Raises:
            NotificationError: If notification fails.
        """
        try:
            notification = self.validate(data)
            payload = self.build_payload(notification)

            if not notification.webhook_url:
                raise NotificationError("webhook_url is required")

            with self._http_client as client:
                response = client.request(
                    method="POST", url=notification.webhook_url, headers=notification.headers, json=payload
                )
                status_code = response.status_code
                try:
                    response.raise_for_status()
                    response_data = response.json()
                    return NotificationResponse(
                        success=True, name=self.name, message="Notification sent successfully", data=response_data
                    ).model_dump()
                except Exception as e:
                    return NotificationResponse(
                        success=False,
                        name=self.name,
                        message=f"Request failed with status {status_code}: {str(e)}",
                        data=None,
                    ).model_dump()
        except Exception as e:
            return NotificationResponse(
                success=False, name=self.name, message=f"Failed to send notification: {str(e)}", data=None
            ).model_dump()

    async def send_async(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Send notification asynchronously.

        Args:
            data: Notification data.

        Returns:
            Dict[str, Any]: Response data.

        Raises:
            NotificationError: If notification fails.
        """
        try:
            notification = self.validate(data)
            payload = self.build_payload(notification)

            if not notification.webhook_url:
                raise NotificationError("webhook_url is required")

            async with self._async_http_client as client:
                response = await client.request(
                    method="POST", url=notification.webhook_url, headers=notification.headers, json=payload
                )
                status_code = response.status_code
                try:
                    response.raise_for_status()
                    response_data = await response.json()
                    return NotificationResponse(
                        success=True, name=self.name, message="Notification sent successfully", data=response_data
                    ).model_dump()
                except Exception as e:
                    return NotificationResponse(
                        success=False,
                        name=self.name,
                        message=f"Request failed with status {status_code}: {str(e)}",
                        data=None,
                    ).model_dump()
        except Exception as e:
            return NotificationResponse(
                success=False, name=self.name, message=f"Failed to send notification: {str(e)}", data=None
            ).model_dump()


class BaseNotifier(AbstractNotifier):
    """Base implementation of notifier with common functionality."""

    def build_payload(self, notification: NotificationSchema) -> Dict[str, Any]:
        """Build notification payload.

        Args:
            notification: Notification data.

        Returns:
            Dict[str, Any]: API payload.

        Raises:
            NotificationError: If notification is not valid.
        """
        if not isinstance(notification, NotificationSchema):
            raise NotificationError(f"Invalid notification type: {type(notification)}")
        if notification.msg_type not in self.supported_types:
            raise NotificationError(f"Unsupported message type: {notification.msg_type}")
        notification = self.validate(notification)
        return self._build_payload(notification)

    def _build_payload(self, notification: NotificationSchema) -> Dict[str, Any]:
        """Build notification payload.

        Args:
            notification: Notification data.

        Returns:
            Dict[str, Any]: API payload.
        """
        if notification.msg_type == MessageType.TEXT:
            return {"msg_type": "text", "content": {"text": notification.content}}
        raise NotificationError(f"Unsupported message type: {notification.msg_type}")


class WebhookNotifier(BaseNotifier):
    """Webhook notifier implementation."""

    name = "webhook"

    def build_payload(self, notification: NotificationSchema) -> Dict[str, Any]:
        """Build webhook notification payload.

        Args:
            notification: Notification data.

        Returns:
            Dict[str, Any]: API payload.
        """
        notification = self.validate(notification)
        return notification.to_payload()
