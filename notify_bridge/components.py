"""Core components for notify-bridge.

This module contains the base notifier classes and core functionality.
"""

# Import built-in modules
from abc import ABC, abstractmethod
from typing import Any, ClassVar, Dict, Optional, Type, Union

# Import third-party modules
from pydantic import ValidationError

# Import local modules
from notify_bridge.exceptions import NotificationError
from notify_bridge.schema import MessageType, NotificationResponse, NotificationSchema
from notify_bridge.utils import AsyncHTTPClient, HTTPClient, HTTPClientConfig


class AbstractNotifier(ABC):
    """Abstract base class for all notifiers."""

    name: str = ""
    schema_class: Type[NotificationSchema] = NotificationSchema
    supported_types: ClassVar[set[MessageType]] = {MessageType.TEXT}
    http_method: str = "POST"

    def get_http_method(self) -> str:
        """Get HTTP method for the request.

        Returns:
            str: HTTP method (e.g., "POST", "GET", "PUT", etc.)
        """
        return self.http_method

    def prepare_request_params(self, notification: NotificationSchema, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Prepare request parameters based on HTTP method.

        Args:
            notification: Notification data.
            payload: Prepared payload data.

        Returns:
            Dict[str, Any]: Request parameters.
        """
        params = {
            "method": self.get_http_method(),
            "url": notification.webhook_url,
            "headers": notification.headers,
        }

        # 根据不同的 HTTP 方法设置不同的参数
        method = self.get_http_method().upper()
        if method in ["POST", "PUT", "PATCH"]:
            params["json"] = payload
        elif method == "GET":
            params["params"] = payload
        else:
            # 对于其他方法，如 DELETE，可能不需要 payload
            if payload:
                params["json"] = payload

        return params

    @abstractmethod
    def __init__(self, config: Optional[HTTPClientConfig] = None) -> None:
        """Initialize notifier.

        Args:
            config: HTTP client configuration.
        """

    @abstractmethod
    def assemble_data(self, data: NotificationSchema) -> Dict[str, Any]:
        """Assemble data data.

        Args:
            data: Notification data.

        Returns:
            Dict[str, Any]: API payload.

        Raises:
            NotificationError: If data is not valid.
        """

    @abstractmethod
    def _prepare_data(self, notification: NotificationSchema) -> Dict[str, Any]:
        """Prepare data data.

        Args:
            notification: Notification data.

        Returns:
            Dict[str, Any]: API payload.

        Raises:
            NotificationError: If data preparation fails.
        """

    @abstractmethod
    async def send_async(self, notification: NotificationSchema) -> NotificationResponse:
        """Send data asynchronously.

        Args:
            notification: Notification data.

        Returns:
            NotificationResponse: API response.

        Raises:
            NotificationError: If data fails.
        """

    @abstractmethod
    def send(self, notification: NotificationSchema) -> NotificationResponse:
        """Send data synchronously.

        Args:
            notification: Notification data.

        Returns:
            NotificationResponse: API response.

        Raises:
            NotificationError: If data fails.
        """

    @abstractmethod
    def validate(self, data: Union[Dict[str, Any], NotificationSchema]) -> NotificationSchema:
        """Validate data data.

        Args:
            data: Notification data.

        Returns:
            NotificationSchema: Validated data schema.

        Raises:
            NotificationError: If validation fails.
        """


class BaseNotifier(AbstractNotifier):
    """Base implementation of notifier with common functionality."""

    def __init__(self, config: Optional[HTTPClientConfig] = None) -> None:
        """Initialize notifier.

        Args:
            config: HTTP client configuration.
        """
        self._config = config or HTTPClientConfig()
        self._sync_client: Optional[HTTPClient] = None
        self._async_client: Optional[AsyncHTTPClient] = None

    def _ensure_sync_client(self) -> HTTPClient:
        """Ensure sync client is initialized.

        Returns:
            HTTPClient: HTTP client instance.
        """
        if self._sync_client is None:
            self._sync_client = HTTPClient(self._config)
        return self._sync_client

    async def _ensure_async_client(self) -> AsyncHTTPClient:
        """Ensure async client is initialized.

        Returns:
            AsyncHTTPClient: Async HTTP client instance.
        """
        if self._async_client is None:
            self._async_client = AsyncHTTPClient(self._config)
        return self._async_client

    def close(self) -> None:
        """Close sync client."""
        if self._sync_client is not None:
            self._sync_client.close()
            self._sync_client = None
        if self._async_client is not None:
            # In sync context, we can't await the close() method
            # Just set the client to None to allow garbage collection
            self._async_client = None

    async def close_async(self) -> None:
        """Close async client."""
        if self._sync_client is not None:
            self._sync_client.close()
            self._sync_client = None
        if self._async_client is not None:
            await self._async_client.close()
            self._async_client = None

    def validate(self, data: Union[Dict[str, Any], NotificationSchema]) -> NotificationSchema:
        """Validate data data.

        Args:
            data: Notification data.

        Returns:
            NotificationSchema: Validated data schema.

        Raises:
            NotificationError: If validation fails.
        """
        try:
            if isinstance(data, dict):
                notification = self.schema_class(**data)
            elif isinstance(data, self.schema_class):
                notification = data
            else:
                raise NotificationError(f"Invalid data type: {type(data)}", notifier_name=self.name)

            if notification.msg_type not in self.supported_types:
                raise NotificationError(f"Unsupported message type: {notification.msg_type}", notifier_name=self.name)

            return notification
        except ValidationError as e:
            raise NotificationError(f"Invalid data data: {str(e)}", notifier_name=self.name)

    def assemble_data(self, data: NotificationSchema) -> Dict[str, Any]:
        """Assemble data data.

        Args:
            data: Notification data.

        Returns:
            Dict[str, Any]: API payload.

        Raises:
            NotificationError: If data is not valid.
        """
        return data.to_payload()

    def _prepare_data(self, notification: NotificationSchema) -> Dict[str, Any]:
        """Prepare data data.

        Args:
            notification: Notification data.

        Returns:
            Dict[str, Any]: API payload.

        Raises:
            NotificationError: If data preparation fails.
        """
        try:
            return self.assemble_data(notification)
        except ValidationError as e:
            raise NotificationError(f"Invalid data data: {str(e)}", notifier_name=self.name)
        except Exception as e:
            raise NotificationError(str(e), notifier_name=self.name)

    def send(self, notification_data: Union[Dict[str, Any], NotificationSchema]) -> NotificationResponse:
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
            request_params = self.prepare_request_params(notification, self._prepare_data(notification))
            client = self._ensure_sync_client()
            response = client.request(request_params.pop("method"), **request_params)
            data = response.json()
            return NotificationResponse(
                success=True,
                name=self.name,
                message="Notification sent successfully",
                data=data,
            )
        except Exception as e:
            raise NotificationError(str(e), notifier_name=self.name)

    async def send_async(self, notification_data: Union[Dict[str, Any], NotificationSchema]) -> NotificationResponse:
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
            request_params = self.prepare_request_params(notification, self._prepare_data(notification))
            client = await self._ensure_async_client()
            response = await client.request(request_params.pop("method"), **request_params)
            data = response.json()
            return NotificationResponse(
                success=True,
                name=self.name,
                message="Notification sent successfully",
                data=data,
            )
        except Exception as e:
            raise NotificationError(str(e), notifier_name=self.name)
