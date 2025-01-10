"""Feishu notifier implementation."""

# Import built-in modules
from typing import Optional

# Import third-party modules
from pydantic import Field

# Import local modules
from notify_bridge.exceptions import NotificationError
from notify_bridge.types import BaseNotifier, NotificationResponse, NotificationSchema
from notify_bridge.utils.requests import RequestsHelper


class FeishuSchema(NotificationSchema):
    """Schema for Feishu notifications."""

    webhook_url: str = Field(description="Webhook URL for sending notifications")
    msg_type: str = Field(description="Message type (text or interactive)")
    at_all: bool = Field(default=False, description="Whether to @all users")
    at_users: Optional[list[str]] = Field(default=None, description="List of user IDs to @")


class FeishuNotifier(BaseNotifier):
    """Feishu notifier implementation."""

    name = "feishu"
    schema = FeishuSchema

    def __init__(self, webhook_url: Optional[str] = None) -> None:
        """Initialize the notifier.

        Args:
            webhook_url: Optional default webhook URL.
        """
        super().__init__()
        self._webhook_url = webhook_url
        self._requests = RequestsHelper()

    def _prepare_message(self, notification: FeishuSchema) -> dict:
        """Prepare the message payload.

        Args:
            notification: The notification data.

        Returns:
            The message payload.

        Raises:
            NotificationError: If the message type is not supported.
        """
        if notification.msg_type == "text":
            return {"msg_type": "text", "content": {"text": f"{notification.title}\n{notification.body}"}}
        elif notification.msg_type == "interactive":
            return {
                "msg_type": "interactive",
                "card": {
                    "header": {"title": {"tag": "plain_text", "content": notification.title}},
                    "elements": [{"tag": "div", "text": {"tag": "plain_text", "content": notification.body}}],
                },
            }
        else:
            raise NotificationError("Invalid message type")

    def send(self, notification: NotificationSchema) -> NotificationResponse:
        """Send a notification.

        Args:
            notification: The notification data.

        Returns:
            NotificationResponse: The response from the notification attempt.

        Raises:
            NotificationError: If sending the notification fails.
        """
        try:
            data = notification.model_dump()
            webhook_url = data.get("webhook_url") or self._webhook_url
            if not webhook_url:
                raise NotificationError("No webhook URL provided")

            payload = self._prepare_message(notification)

            # Add @mentions if specified
            if data.get("at_all"):
                payload.setdefault("at", {})["isAtAll"] = True
            if data.get("at_users"):
                payload.setdefault("at", {})["atUserIds"] = data["at_users"]

            response = self._requests.post(webhook_url, json=payload)
            response.raise_for_status()

            return NotificationResponse(True, self.name, data)
        except Exception as e:
            raise NotificationError(f"Failed to send Feishu notification: {str(e)}")

    async def asend(self, notification: NotificationSchema) -> NotificationResponse:
        """Send a notification asynchronously.

        Args:
            notification: The notification data.

        Returns:
            NotificationResponse: The response from the notification attempt.

        Raises:
            NotificationError: If sending the notification fails.
        """
        try:
            data = notification.model_dump()
            webhook_url = data.get("webhook_url") or self._webhook_url
            if not webhook_url:
                raise NotificationError("No webhook URL provided")

            payload = self._prepare_message(notification)

            # Add @mentions if specified
            if data.get("at_all"):
                payload.setdefault("at", {})["isAtAll"] = True
            if data.get("at_users"):
                payload.setdefault("at", {})["atUserIds"] = data["at_users"]

            response = await self._requests.apost(webhook_url, json=payload)
            response.raise_for_status()

            return NotificationResponse(True, self.name, data)
        except Exception as e:
            raise NotificationError(f"Failed to send Feishu notification: {str(e)}")

    def close(self) -> None:
        """Close any resources held by the notifier."""
        self._requests.close()

    async def aclose(self) -> None:
        """Close any resources held by the notifier asynchronously."""
        await self._requests.aclose()
