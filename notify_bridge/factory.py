"""Factory for creating notifiers."""

# Import built-in modules
import logging
from typing import Any
from typing import Dict
from typing import Optional
from typing import Type
from typing import Union

# Import local modules
from notify_bridge.components import BaseNotifier
from notify_bridge.exceptions import NoSuchNotifierError
from notify_bridge.exceptions import NotificationError
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

    async def create_async_notifier(
        self, name: str, config: Optional[HTTPClientConfig] = None, **kwargs: Any
    ) -> BaseNotifier:
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

    def get_notifier_names(self) -> Dict[str, Type[BaseNotifier]]:
        """Get registered notifier names.

        Returns:
            Dict[str, Type[BaseNotifier]]: Registered notifier names
        """
        return self._notifiers.copy()

    def send(
        self, name: str, data: Optional[Union[NotificationSchema, Dict[str, Any]]] = None, **kwargs: Any
    ) -> Dict[str, Any]:
        """Send a data.

        Args:
            name: The name of the notifier to use.
            data: The data to send.
            **kwargs: Additional arguments to pass to the notifier.

        Returns:
            The response from the notifier.

        Raises:
            NoSuchNotifierError: If the specified notifier is not found.
            ValidationError: If data validation fails.
            NotificationError: If there is an error sending the data.
        """
        notifier_class = self.get_notifier_class(name)
        if notifier_class is None:
            raise NoSuchNotifierError(f"Notifier {name} not found")
        notifier = notifier_class()
        if data is None and not kwargs:
            raise NotificationError("No data provided")
        if data is None:
            data = kwargs
        return notifier.send(data)

    async def send_async(
        self, name: str, data: Optional[Union[NotificationSchema, Dict[str, Any]]] = None, **kwargs: Any
    ) -> Dict[str, Any]:
        """Send a data asynchronously.

        Args:
            name: The name of the notifier to use.
            data: The data to send.
            **kwargs: Additional arguments to pass to the notifier.

        Returns:
            The response from the notifier.

        Raises:
            NoSuchNotifierError: If the specified notifier is not found.
            ValidationError: If data validation fails.
            NotificationError: If there is an error sending the data.
        """
        notifier_class = self.get_notifier_class(name)
        if notifier_class is None:
            raise NoSuchNotifierError(f"Notifier {name} not found")
        notifier = notifier_class()
        if data is None and not kwargs:
            raise NotificationError("No data provided")
        if data is None:
            data = kwargs
        return await notifier.send_async(data)
