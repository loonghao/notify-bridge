"""Core functionality for notify-bridge."""

# Import built-in modules
import logging
from typing import Any, Dict, List, Optional, Type, Union

# Import third-party modules
import httpx

# Import local modules
from notify_bridge.factory import NotifierFactory
from notify_bridge.types import BaseNotifier, NotificationResponse, NotificationSchema

logger = logging.getLogger(__name__)


class NotifyBridge:
    """Core notification bridge class."""

    def __init__(self, config: Dict[str, Any] = None) -> None:
        """Initialize the bridge.

        Args:
            config: Configuration for notifiers.
        """
        self._config = config or {}
        self._factory = NotifierFactory()
        self._sync_client: Optional[httpx.Client] = None
        self._async_client: Optional[httpx.AsyncClient] = None

    def __enter__(self) -> "NotifyBridge":
        """Enter context manager.

        Returns:
            NotifyBridge: Self instance.
        """
        self._sync_client = httpx.Client()
        return self

    def __exit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        """Exit context manager.

        Args:
            exc_type: Exception type.
            exc_val: Exception value.
            exc_tb: Exception traceback.
        """
        if self._sync_client:
            self._sync_client.close()
            self._sync_client = None

    async def __aenter__(self) -> "NotifyBridge":
        """Enter async context manager.

        Returns:
            NotifyBridge: Self instance.
        """
        self._async_client = httpx.AsyncClient()
        return self

    async def __aexit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        """Exit async context manager.

        Args:
            exc_type: Exception type.
            exc_val: Exception value.
            exc_tb: Exception traceback.
        """
        if self._async_client:
            await self._async_client.aclose()
            self._async_client = None

    def get_notifier_class(self, name: str) -> Optional[Type[BaseNotifier]]:
        """Get a notifier class by name.

        Args:
            name: Name of the notifier.

        Returns:
            Optional[Type[BaseNotifier]]: Notifier class if found, None otherwise.
        """
        return self._factory.get_notifier_class(name)

    def create_notifier(self, name: str, **kwargs: Any) -> BaseNotifier:
        """Create a notifier instance.

        Args:
            name: Name of the notifier.
            **kwargs: Additional arguments to pass to the notifier.

        Returns:
            BaseNotifier: Notifier instance.

        Raises:
            NoSuchNotifierError: If the notifier is not found.
        """
        if "client" not in kwargs:
            kwargs["client"] = self._sync_client
        return self._factory.create_notifier(name, **kwargs)

    async def create_async_notifier(self, name: str, **kwargs: Any) -> BaseNotifier:
        """Create an async notifier instance.

        Args:
            name: Name of the notifier.
            **kwargs: Additional arguments to pass to the notifier.

        Returns:
            BaseNotifier: Notifier instance.

        Raises:
            NoSuchNotifierError: If the notifier is not found.
        """
        if "client" not in kwargs:
            kwargs["client"] = self._async_client
        return self._factory.create_notifier(name, **kwargs)

    def notify(
            self,
            name: str,
            notification: Optional[Dict[str, Any]] = None,
            **kwargs: Any,
    ) -> NotificationResponse:
        """Send a notification.

        Args:
            name: The name of the notifier to use.
            notification: The notification to send.
            **kwargs: Additional arguments to pass to the notifier.

        Returns:
            The response from the notifier.
        """
        client = kwargs.pop("client", self._sync_client)
        if notification is None:
            notification = kwargs
            kwargs = {}
        return self._factory.notify(name, notification=notification, client=client, **kwargs)

    async def anotify(
            self,
            name: str,
            notification: Optional[Dict[str, Any]] = None,
            **kwargs: Any,
    ) -> NotificationResponse:
        """Send a notification asynchronously.

        Args:
            name: The name of the notifier to use.
            notification: The notification to send.
            **kwargs: Additional arguments to pass to the notifier.

        Returns:
            The response from the notifier.
        """
        client = kwargs.pop("client", self._async_client)
        if notification is None:
            notification = kwargs
            kwargs = {}
        return await self._factory.anotify(name, notification=notification, client=client, **kwargs)

    def get_registered_notifiers(self) -> List[str]:
        """Get a list of registered notifier names.

        Returns:
            List[str]: List of registered notifier names.
        """
        return list(self._factory.get_notifier_names().keys())
