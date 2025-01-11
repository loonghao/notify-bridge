"""Core module for notify-bridge.

This module provides the main functionality for sending notifications.
"""

# Import built-in modules
import logging
from typing import Any
from typing import Dict
from typing import List
from typing import Optional
from typing import Type

# Import third-party modules
import httpx

# Import local modules
from notify_bridge.components import BaseNotifier
from notify_bridge.exceptions import ConfigurationError
from notify_bridge.exceptions import NoSuchNotifierError
from notify_bridge.factory import NotifierFactory
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

    def register_notifier(self, name: str, notifier_cls: Type[BaseNotifier]) -> None:
        """Register a notifier.

        Args:
            name: Name of the notifier
            notifier_cls: Notifier class to register

        Raises:
            TypeError: If notifier_cls is not a subclass of BaseNotifier
        """
        if not isinstance(notifier_cls, type) or not issubclass(notifier_cls, BaseNotifier):
            raise TypeError(f"Invalid notifier class: {notifier_cls}. " "Expected a subclass of BaseNotifier.")
        self._factory.register_notifier(name, notifier_cls)
        logger.debug(f"Registered notifier: {name}")

    def get_registered_notifiers(self) -> List[str]:
        """Get list of registered notifier names.

        Returns:
            List of notifier names
        """
        return list(self._factory.get_notifier_names())

    @property
    def notifiers(self) -> List[str]:
        return self.get_registered_notifiers()

    def get_notifier(self, name: str) -> BaseNotifier:
        """Get a registered notifier by name.

        Args:
            name: Name of the notifier

        Returns:
            Registered notifier instance

        Raises:
            NoSuchNotifierError: If notifier is not found
        """
        return self.create_notifier(name)

    def send(self, notifier_name: str, data: Optional[Dict[str, Any]] = None, **kwargs) -> Dict[str, Any]:
        """Send notification.

        Args:
            notifier_name: Name of the notifier
            data: Notification data as dictionary
            **kwargs: Additional notification data as keyword arguments

        Returns:
            Dict[str, Any]: Response data

        Raises:
            NoSuchNotifierError: If notifier is not found
        """
        notifier = self.get_notifier(notifier_name)
        if data is None:
            data = {}
        notification_data = {**data, **kwargs}
        notification = notifier.schema_class(**notification_data)
        response = notifier.send(notification)
        response["name"] = notifier_name
        return response

    async def send_async(self, notifier_name: str, data: Optional[Dict[str, Any]] = None, **kwargs) -> Dict[str, Any]:
        """Send notification asynchronously.

        Args:
            notifier_name: Name of the notifier
            data: Notification data as dictionary
            **kwargs: Additional notification data as keyword arguments

        Returns:
            Dict[str, Any]: Response data

        Raises:
            NoSuchNotifierError: If notifier is not found
        """
        notifier = self.get_notifier(notifier_name)
        if data is None:
            data = {}
        notification_data = {**data, **kwargs}
        notification = notifier.schema_class(**notification_data)
        response = await notifier.send_async(notification)
        response["name"] = notifier_name
        return response
