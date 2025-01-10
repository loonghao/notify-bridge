"""Base types for notify-bridge."""

# Import built-in modules
from abc import ABC, abstractmethod
from typing import Any, Dict, Optional, Type

# Import third-party modules
from pydantic import BaseModel, ConfigDict, Field


class NotificationSchema(BaseModel):
    """Base schema for all notifications."""

    model_config = ConfigDict(extra="allow")

    # Common fields that all notifications might have
    title: Optional[str] = Field(None, description="Title of the notification")
    body: Optional[str] = Field(None, description="Body of the notification")


class NotificationResponse:
    """Response from a notification attempt."""

    def __init__(
        self,
        success: bool,
        notifier: str,
        data: Dict[str, Any],
        response: Optional[Dict[str, Any]] = None,
        error: Optional[str] = None,
    ) -> None:
        """Initialize NotificationResponse.

        Args:
            success: Whether the notification was successful
            notifier: Name of the notifier used
            data: The notification data that was sent
            response: Optional response data from the notifier
            error: Optional error message if the notification failed
        """
        self.success = success
        self.notifier = notifier
        self.data = data
        self.response = response
        self.error = error

    def __bool__(self) -> bool:
        return self.success


class BaseNotifier(ABC):
    """Base class for all notifiers."""

    name: str = None
    schema: Type[NotificationSchema] = NotificationSchema
    site_url: str = None

    def __init__(self, **kwargs: Any) -> None:
        """Initialize the notifier.

        Args:
            **kwargs: Configuration for the notifier
        """
        if not self.name:
            self.name = self.__class__.__name__.lower().replace("notifier", "")

        # Store configuration
        self.config = kwargs

    def validate(self, data: Dict[str, Any]) -> NotificationSchema:
        """Validate notification data against the schema.

        Args:
            data: The notification data to validate

        Returns:
            NotificationSchema: The validated notification data

        Raises:
            ValidationError: If validation fails
        """
        try:
            return self.schema(**data)
        except Exception as e:
            # Import local modules
            from notify_bridge.exceptions import ValidationError

            raise ValidationError(str(e), self.name)

    @abstractmethod
    def send(self, notification: NotificationSchema) -> NotificationResponse:
        """Send a notification.

        Args:
            notification: The notification to send

        Returns:
            NotificationResponse: The response from the notification attempt

        Raises:
            NotificationError: If sending the notification fails
        """

    @abstractmethod
    async def asend(self, notification: NotificationSchema) -> NotificationResponse:
        """Send a notification asynchronously.

        Args:
            notification: The notification to send

        Returns:
            NotificationResponse: The response from the notification attempt

        Raises:
            NotificationError: If sending the notification fails
        """

    def close(self) -> None:
        """Close any resources held by the notifier."""

    async def aclose(self) -> None:
        """Close any resources held by the notifier asynchronously."""
