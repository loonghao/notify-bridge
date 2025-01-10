"""Core components of the notify-bridge framework."""

# Import built-in modules
import logging
from typing import Any, Dict, List, Optional, Union

# Import local modules
from notify_bridge.exceptions import NoSuchNotifierError
from notify_bridge.factory import NotifierFactory
from notify_bridge.types import BaseNotifier, NotificationResponse, NotificationSchema
from notify_bridge.utils.plugin import get_all_notifiers

logger = logging.getLogger(__name__)


class NotifyBridge:
    """Main class for managing notifiers and sending notifications."""

    def __init__(self, config: Dict[str, Any] = None, load_plugins: bool = True) -> None:
        """Initialize the notification bridge.

        Args:
            config: Configuration dictionary for notifiers
            load_plugins: Whether to load notifier plugins from entry points
        """
        self._config = config or {}
        self._factory = NotifierFactory()

        # Load plugins if enabled
        if load_plugins:
            self._load_plugins()

    def _load_plugins(self) -> None:
        """Load notifier plugins from entry points and built-in notifiers."""
        plugins = get_all_notifiers()
        for name, notifier_class in plugins.items():
            try:
                config = self._config.get(name, {})
                self._factory.create_notifier(name, **config)
            except Exception as e:
                logger.error(f"Failed to initialize plugin {name}: {str(e)}")

    def get_notifier(self, name: str) -> Optional[BaseNotifier]:
        """Get a registered notifier by name.

        Args:
            name: The name of the notifier to get.

        Returns:
            Optional[BaseNotifier]: The notifier if found, None otherwise.
        """
        return self._factory.get_instance(name)

    def get_registered_notifiers(self) -> List[str]:
        """Get a list of registered notifier names.

        Returns:
            List[str]: List of registered notifier names.
        """
        return self._factory.get_notifier_names()

    def notify(
        self, notifier_name: str, notification: Optional[Union[NotificationSchema, Dict[str, Any]]] = None, **kwargs
    ) -> NotificationResponse:
        """Send a notification.

        Args:
            notifier_name: Name of the notifier to use
            notification: The notification data, can be a NotificationSchema or dict
            **kwargs: Additional notification parameters if notification is not provided

        Returns:
            NotificationResponse: The response from the notification attempt.

        Raises:
            NoSuchNotifierError: If the notifier is not found.
            NotificationError: If sending the notification fails.
        """
        notifier = self.get_notifier(notifier_name)
        if not notifier:
            raise NoSuchNotifierError(f"Notifier {notifier_name} not found")

        # If notification is not provided, create one from kwargs
        if notification is None and kwargs:
            schema_class = notifier.schema
            notification = schema_class(**kwargs)
        elif isinstance(notification, dict):
            schema_class = notifier.schema
            notification = schema_class(**notification)

        try:
            return notifier.send(notification)
        finally:
            # Run the async close in a new event loop
            # Import built-in modules
            import asyncio

            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            try:
                loop.run_until_complete(notifier.aclose())
            finally:
                loop.run_until_complete(loop.shutdown_asyncgens())
                loop.close()

    async def anotify(
        self, notifier_name: str, notification: Optional[Union[NotificationSchema, Dict[str, Any]]] = None, **kwargs
    ) -> NotificationResponse:
        """Send a notification asynchronously.

        Args:
            notifier_name: Name of the notifier to use
            notification: The notification data, can be a NotificationSchema or dict
            **kwargs: Additional notification parameters if notification is not provided

        Returns:
            NotificationResponse: The response from the notification attempt.

        Raises:
            NoSuchNotifierError: If the notifier is not found.
            NotificationError: If sending the notification fails.
        """
        notifier = self.get_notifier(notifier_name)
        if not notifier:
            raise NoSuchNotifierError(f"Notifier {notifier_name} not found")

        # If notification is not provided, create one from kwargs
        if notification is None and kwargs:
            schema_class = notifier.schema
            notification = schema_class(**kwargs)
        elif isinstance(notification, dict):
            schema_class = notifier.schema
            notification = schema_class(**notification)

        try:
            return await notifier.asend(notification)
        finally:
            await notifier.aclose()

    def add_notifier(self, notifier: BaseNotifier) -> None:
        """Add a notifier.

        Args:
            notifier: The notifier to add.
        """
        self._factory.register_notifier(notifier.name, type(notifier))
        self._factory._instances[notifier.name] = notifier

    def remove_notifier(self, name: str) -> None:
        """Remove a notifier.

        Args:
            name: The name of the notifier to remove.
        """
        self._factory.unregister_notifier(name)

    def close(self) -> None:
        """Close all notifiers and clean up resources."""
        self._factory.close()

    async def aclose(self) -> None:
        """Close all notifiers and clean up resources asynchronously."""
        await self._factory.aclose()

    def __del__(self) -> None:
        """Clean up resources when the bridge is deleted."""
        self.close()
