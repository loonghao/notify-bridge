"""Type definitions for notify-bridge."""

# Import built-in modules
from abc import ABC
from typing import Any, Dict, Optional, Union

# Import third-party modules
import httpx
from pydantic import BaseModel, Field
from pydantic import ValidationError as PydanticValidationError

# Import local modules
from notify_bridge.exceptions import NotificationError, ValidationError


class NotificationSchema(BaseModel):
    """Base schema for notifications."""

    url: str = Field(description="url of the notification")

    @classmethod
    def validate_data(cls, data: Dict[str, Any]) -> "NotificationSchema":
        """Validate notification data.

        Args:
            data: Data to validate.

        Returns:
            NotificationSchema: Validated notification schema.

        Raises:
            ValidationError: If validation fails.
        """
        try:
            return cls(**data)
        except PydanticValidationError as e:
            raise ValidationError(str(e))


class NotificationResponse(BaseModel):
    """Response from a notification attempt."""

    success: bool = Field(description="Whether the notification was successful")
    name: str = Field(description="Name of the notifier")
    message: Optional[str] = Field(default=None, description="Optional message")
    data: Optional[Dict[str, Any]] = Field(default=None, description="Optional data")


class BaseNotifier(ABC):
    """Base class for notifiers."""

    name: str = ""
    schema: type[NotificationSchema] = NotificationSchema

    def __init__(self, client: Optional[httpx.Client] = None, **kwargs: Any) -> None:
        """Initialize the notifier.

        Args:
            client: HTTP client.
            **kwargs: Additional arguments to pass to the notifier.
        """
        self.client = client

    def validate(self, notification: Dict[str, Any]) -> NotificationSchema:
        """Validate notification data.

        Args:
            notification: Notification data.

        Returns:
            NotificationSchema: Validated notification schema.

        Raises:
            ValidationError: If validation fails.
        """
        try:
            return self.schema.validate_data(notification)
        except ValidationError as e:
            raise ValidationError(f"Invalid notification data: {str(e)}")

    def _build_base_payload(self, notification: NotificationSchema) -> Dict[str, Any]:
        """Build the base payload for the API.

        Args:
            notification: Notification data.

        Returns:
            Dict[str, Any]: Base API payload.

        Raises:
            NotificationError: If building the payload fails.
        """
        return {"url": notification.url}

    def _build_content_payload(self, notification: NotificationSchema) -> Dict[str, Any]:
        """Build the content payload for the API.

        Args:
            notification: Notification data.

        Returns:
            Dict[str, Any]: Content API payload.

        Raises:
            NotificationError: If building the payload fails.
        """
        return {}

    async def _build_content_payload_async(self, notification: NotificationSchema) -> Dict[str, Any]:
        """Build the content payload for the API asynchronously.

        Args:
            notification: Notification data.

        Returns:
            Dict[str, Any]: Content API payload.

        Raises:
            NotificationError: If building the payload fails.
        """
        return self._build_content_payload(notification)

    def build_payload(self, notification: NotificationSchema) -> Dict[str, Any]:
        """Build the payload for the API.

        Args:
            notification: Notification data.

        Returns:
            Dict[str, Any]: API payload.

        Raises:
            NotificationError: If building the payload fails.
        """
        base_payload = self._build_base_payload(notification)
        content_payload = self._build_content_payload(notification)
        base_payload.update(content_payload)
        return base_payload

    async def build_payload_async(self, notification: NotificationSchema) -> Dict[str, Any]:
        """Build the payload for the API asynchronously.

        Args:
            notification: Notification data.

        Returns:
            Dict[str, Any]: API payload.

        Raises:
            NotificationError: If building the payload fails.
        """
        base_payload = self._build_base_payload(notification)
        content_payload = await self._build_content_payload_async(notification)
        base_payload.update(content_payload)
        return base_payload

    def notify(self, notification: Optional[Union[NotificationSchema, Dict[str, Any]]] = None, **kwargs: Any) -> NotificationResponse:
        """Send a notification.

        Args:
            notification: Notification data.
            **kwargs: Additional arguments.

        Returns:
            NotificationResponse: Response from the notification attempt.
        """
        if notification is None:
            notification = kwargs
        if isinstance(notification, dict):
            notification = self.validate(notification)
        client = self.client or httpx.Client()
        try:
            payload = self.build_payload(notification)
            response = client.post(**payload)
            response.raise_for_status()
            data = response.json()
            return NotificationResponse(success=True, name=self.name, data=data)
        except Exception as e:
            raise NotificationError(str(e))

    async def anotify(self, notification: Optional[Union[NotificationSchema, Dict[str, Any]]] = None, **kwargs: Any) -> NotificationResponse:
        """Send a notification asynchronously.

        Args:
            notification: Notification data.
            **kwargs: Additional arguments.

        Returns:
            NotificationResponse: Response from the notification attempt.
        """
        if notification is None:
            notification = kwargs
        if isinstance(notification, dict):
            notification = self.validate(notification)
        try:
            payload = await self.build_payload_async(notification)
            async with httpx.AsyncClient() as client:
                response = await client.post(**payload)
                response.raise_for_status()
                try:
                    data = response.json()
                except AttributeError:
                    data = await response.json()
                return NotificationResponse(success=True, name=self.name, data=data)
        except Exception as e:
            raise NotificationError(str(e))
