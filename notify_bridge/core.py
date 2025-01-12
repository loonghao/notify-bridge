"""Core module for notify-bridge.

This module provides the main functionality for sending notifications.
"""

# Import built-in modules
import logging
from typing import Any, Dict, List, Optional, Type

# Import third-party modules
import httpx
from pydantic import ValidationError

# Import local modules
from notify_bridge.components import BaseNotifier
from notify_bridge.exceptions import ConfigurationError, NoSuchNotifierError, NotificationError
from notify_bridge.factory import NotifierFactory
from notify_bridge.schema import NotificationResponse
from notify_bridge.utils import HTTPClientConfig

logger = logging.getLogger(__name__)


class NotifyBridge:
    """Main class for sending notifications.

    This class provides a unified interface for sending notifications
    through different notifiers.
    """

    def __init__(self, config: Optional[Any] = None):
        """Initialize NotifyBridge.

        Args:
            config: HTTP client configuration

        Raises:
            ConfigurationError: If config is invalid
        """
        if config is None:
            self._config = HTTPClientConfig()
        elif isinstance(config, HTTPClientConfig):
            self._config = config
        else:
            raise ConfigurationError("Invalid configuration. Expected HTTPClientConfig or None.", config_value=config)
        self._factory = NotifierFactory()
        self._sync_client = None
        self._async_client = None
        self._notifiers = {}

    def __enter__(self):
        """Enter context manager."""
        self._sync_client = httpx.Client(
            timeout=self._config.timeout, verify=self._config.verify_ssl, headers=self._config.headers
        )
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Exit context manager."""
        if self._sync_client:
            self._sync_client.close()
        self._sync_client = None
        for notifier in self._notifiers.values():
            if hasattr(notifier, "close"):
                notifier.close()
        self._notifiers.clear()

    async def __aenter__(self):
        """Enter async context manager."""
        self._async_client = httpx.AsyncClient(
            timeout=self._config.timeout, verify=self._config.verify_ssl, headers=self._config.headers
        )
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Exit async context manager."""
        if self._async_client:
            await self._async_client.aclose()
        self._async_client = None
        for notifier in self._notifiers.values():
            if hasattr(notifier, "close"):
                await notifier.close()
        self._notifiers.clear()

    def get_notifier_class(self, name: str) -> Type[BaseNotifier]:
        """Get notifier class by name.

        Args:
            name: Name of the notifier

        Returns:
            Notifier class

        Raises:
            NoSuchNotifierError: If notifier is not found
        """
        notifier_class = self._factory.get_notifier_class(name)
        if not notifier_class:
            raise NoSuchNotifierError(f"Notifier {name} not found")
        return notifier_class

    def create_notifier(self, name: str) -> BaseNotifier:
        """Create a notifier instance.

        Args:
            name: Name of the notifier

        Returns:
            Notifier instance

        Raises:
            NoSuchNotifierError: If notifier is not found
        """
        return self._factory.create_notifier(name, config=self._config)

    async def create_async_notifier(self, name: str) -> BaseNotifier:
        """Create an async notifier instance.

        Args:
            name: Name of the notifier

        Returns:
            Notifier instance

        Raises:
            NoSuchNotifierError: If notifier is not found
        """
        return self._factory.create_notifier(name, config=self._config)

    def register_notifier(self, name: str, notifier_class: Type[BaseNotifier]) -> None:
        """Register a notifier.

        Args:
            name: Notifier name
            notifier_class: Notifier class
        """
        self._notifiers[name] = notifier_class(name=name)

    def get_registered_notifiers(self) -> Dict[str, Type[BaseNotifier]]:
        """Get registered notifiers.

        Returns:
            Dict[str, Type[BaseNotifier]]: Dictionary of registered notifiers.
        """
        return self._notifiers

    @property
    def notifiers(self) -> List[str]:
        return list(self.get_registered_notifiers())

    def get_notifier(self, name: str) -> BaseNotifier:
        """Get or create a notifier instance.

        Args:
            name: Name of the notifier

        Returns:
            Notifier instance

        Raises:
            NoSuchNotifierError: If notifier is not found
        """
        if name not in self._notifiers:
            self._notifiers[name] = self.create_notifier(name)
        return self._notifiers[name]

    def send(self, notifier_name: str, data: Optional[Dict[str, Any]] = None, **kwargs) -> NotificationResponse:
        """Send data synchronously.

        Args:
            notifier_name: Name of the notifier
            data: Notification data as dictionary
            **kwargs: Additional data data as keyword arguments

        Returns:
            NotificationResponse: Response data

        Raises:
            NoSuchNotifierError: If notifier is not found
        """
        notifier = self.get_notifier(notifier_name)
        if data is None:
            data = {}
        notification_data = {**data, **kwargs}
        try:
            response = notifier.send(notification_data)
            return response if isinstance(response, NotificationResponse) else response
        except ValidationError as e:
            raise NotificationError(str(e), notifier_name=notifier_name)

    async def send_async(self, notifier_name: str, data: Optional[Dict[str, Any]] = None, **kwargs) -> NotificationResponse:
        """Send data asynchronously.

        Args:
            notifier_name: Name of the notifier
            data: Notification data as dictionary
            **kwargs: Additional data data as keyword arguments

        Returns:
            NotificationResponse: Response data

        Raises:
            NoSuchNotifierError: If notifier is not found
        """
        notifier = self.get_notifier(notifier_name)
        if data is None:
            data = {}
        notification_data = {**data, **kwargs}
        try:
            response = await notifier.send_async(notification_data)
            return response if isinstance(response, NotificationResponse) else response
        except ValidationError as e:
            raise NotificationError(str(e), notifier_name=notifier_name)
