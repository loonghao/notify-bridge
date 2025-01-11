"""Factory for creating notifiers."""

# Import built-in modules
import logging
from typing import Any, Dict, Optional, Type, Union

# Import third-party modules
import httpx

# Import local modules
from notify_bridge.exceptions import NoSuchNotifierError
from notify_bridge.types import BaseNotifier, NotificationResponse, NotificationSchema
from notify_bridge.utils.plugin import get_all_notifiers

logger = logging.getLogger(__name__)


class NotifierFactory:
    """Factory for creating notifiers."""

    def __init__(self) -> None:
        """Initialize the factory."""
        self._notifier_classes: Dict[str, Type[BaseNotifier]] = {}
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
        self._notifier_classes[name] = notifier_class

    def unregister_notifier(self, name: str) -> None:
        """Unregister a notifier class.

        Args:
            name: Name of the notifier to unregister.
        """
        if name in self._notifier_classes:
            del self._notifier_classes[name]

    def get_notifier_class(self, name: str) -> Optional[Type[BaseNotifier]]:
        """Get a notifier class by name.

        Args:
            name: Name of the notifier.

        Returns:
            Optional[Type[BaseNotifier]]: Notifier class if found, None otherwise.
        """
        return self._notifier_classes.get(name)

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
        notifier_class = self.get_notifier_class(name)
        if notifier_class is None:
            raise NoSuchNotifierError(f"Notifier {name} not found")
        return notifier_class(**kwargs)

    def get_notifier_names(self) -> Dict[str, Type[BaseNotifier]]:
        """Get a dictionary of registered notifier names and classes.

        Returns:
            Dict[str, Type[BaseNotifier]]: Dictionary of notifier names and classes.
        """
        return self._notifier_classes.copy()

    def notify(
        self,
        name: str,
        notification: Optional[Union[NotificationSchema, Dict[str, Any]]] = None,
        client: Optional[httpx.Client] = None,
        **kwargs: Any,
    ) -> NotificationResponse:
        """Send a notification synchronously.

        Args:
            name: Name of the notifier to use.
            notification: Notification data.
            client: HTTP client to use.
            **kwargs: Additional arguments to pass to the notifier.

        Returns:
            NotificationResponse: The response from the notification attempt.

        Raises:
            NoSuchNotifierError: If the specified notifier is not found.
        """
        notifier = self.create_notifier(name, client=client)
        return notifier.notify(notification, **kwargs)

    async def anotify(
        self,
        name: str,
        notification: Optional[Union[NotificationSchema, Dict[str, Any]]] = None,
        client: Optional[httpx.AsyncClient] = None,
        **kwargs: Any,
    ) -> NotificationResponse:
        """Send a notification asynchronously.

        Args:
            name: Name of the notifier to use.
            notification: Notification data.
            client: HTTP client to use.
            **kwargs: Additional arguments to pass to the notifier.

        Returns:
            NotificationResponse: The response from the notification attempt.

        Raises:
            NoSuchNotifierError: If the specified notifier is not found.
        """
        notifier = self.create_notifier(name, client=client)
        return await notifier.anotify(notification, **kwargs)
