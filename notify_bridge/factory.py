"""Factory for creating notifiers."""

# Import built-in modules
import logging
from typing import Any, Dict, List, Optional, Type, Union

from notify_bridge.components import BaseNotifier

# Import local modules
from notify_bridge.exceptions import NoSuchNotifierError
from notify_bridge.plugin import get_all_notifiers
from notify_bridge.schema import NotificationSchema
from notify_bridge.utils import HTTPClientConfig

logger = logging.getLogger(__name__)


class NotifierFactory:
    """Factory for creating notifiers."""

    def __init__(self) -> None:
        """Initialize factory."""
        self._notifiers: Dict[str, Type[BaseNotifier]] = {}
        self._config: Dict[str, Any] = {}
        self._load_plugins()

    def _load_plugins(self) -> None:
        """Load notifier plugins from entry points and built-in notifiers."""
        plugins = get_all_notifiers()
        for name, notifier_class in plugins.items():
            self.register_notifier(name, notifier_class)

    def register_notifier(self, name: str, notifier_class: Type[BaseNotifier]) -> None:
        """Register a notifier class.

        Args:
            name: Name of the notifier.
            notifier_class: Notifier class to register.
        """
        self._notifiers[name] = notifier_class

    def unregister_notifier(self, name: str) -> None:
        """Unregister a notifier class.

        Args:
            name: Name of the notifier to unregister.
        """
        if name in self._notifiers:
            del self._notifiers[name]

    def get_notifier_class(self, name: str) -> Optional[Type[BaseNotifier]]:
        """Get a notifier class by name.

        Args:
            name: Name of the notifier.

        Returns:
            Optional[Type[BaseNotifier]]: Notifier class if found, None otherwise.
        """
        return self._notifiers.get(name)

    def create_notifier(self, name: str, config: Optional[HTTPClientConfig] = None, **kwargs: Any) -> BaseNotifier:
        """Create a notifier instance.

        Args:
            name: Name of the notifier.
            config: HTTP client configuration.
            **kwargs: Additional arguments to pass to the notifier.

        Returns:
            BaseNotifier: Notifier instance.

        Raises:
            NoSuchNotifierError: If the notifier is not found.
        """
        notifier_class = self.get_notifier_class(name)
        if notifier_class is None:
            raise NoSuchNotifierError(f"Notifier {name} not found")
        return notifier_class(config=config, **kwargs)

    async def create_async_notifier(self, name: str, config: Optional[HTTPClientConfig] = None, **kwargs: Any) -> BaseNotifier:
        """Create a notifier instance.

        Args:
            name: Notifier name.
            config: HTTP client configuration.
            **kwargs: Additional arguments.

        Returns:
            Notifier instance.

        Raises:
            NoSuchNotifierError: If notifier not found.
        """
        notifier_class = self.get_notifier_class(name)
        if not notifier_class:
            raise NoSuchNotifierError(f"Notifier {name} not found")
        return notifier_class(config=config, **kwargs)

    def get_notifier_names(self) -> List[str]:
        """Get a list of registered notifier names.

        Returns:
            List[str]: List of notifier names.
        """
        return list(self._notifiers.keys())

    def notify(
        self,
        name: str,
        notification: Optional[Union[NotificationSchema, Dict[str, Any]]] = None,
        **kwargs: Any,
    ) -> Dict[str, Any]:
        """Send a notification.

        Args:
            name: The name of the notifier to use.
            notification: The notification to send.
            **kwargs: Additional arguments to pass to the notifier.

        Returns:
            The response from the notifier.

        Raises:
            NoSuchNotifierError: If the specified notifier is not found.
            ValidationError: If notification validation fails.
            NotificationError: If there is an error sending the notification.
        """
        notifier_class = self.get_notifier_class(name)
        if notifier_class is None:
            raise NoSuchNotifierError(f"Notifier {name} not found")
        notifier = notifier_class()
        if notification is None:
            notification = kwargs
        return notifier.notify(notification)

    async def notify_async(
        self,
        name: str,
        notification: Optional[Union[NotificationSchema, Dict[str, Any]]] = None,
        **kwargs: Any,
    ) -> Dict[str, Any]:
        """Send a notification asynchronously.

        Args:
            name: The name of the notifier to use.
            notification: The notification to send.
            **kwargs: Additional arguments to pass to the notifier.

        Returns:
            The response from the notifier.

        Raises:
            NoSuchNotifierError: If the specified notifier is not found.
            ValidationError: If notification validation fails.
            NotificationError: If there is an error sending the notification.
        """
        notifier_class = self.get_notifier_class(name)
        if notifier_class is None:
            raise NoSuchNotifierError(f"Notifier {name} not found")
        notifier = notifier_class()
        if notification is None:
            notification = kwargs
        return await notifier.notify_async(notification)
