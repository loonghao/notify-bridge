"""Factory for creating notifiers."""

# Import built-in modules
import asyncio
import importlib
import logging
from pathlib import Path
from typing import Any, Dict, List, Optional, Type, Union

# Import local modules
from notify_bridge.exceptions import NoSuchNotifierError, PluginError
from notify_bridge.types import BaseNotifier, NotificationResponse, NotificationSchema
from notify_bridge.utils.plugin import get_notifiers_from_entry_points

logger = logging.getLogger(__name__)


class NotifierFactory:
    """Factory to dynamically load notifier instances."""

    NOTIFIERS_DIR = Path(__file__).parent / "notifiers"

    def __init__(self, load_plugins: bool = True) -> None:
        """Initialize the notifier factory.

        Args:
            load_plugins: Whether to load notifier plugins from entry points
        """
        self._notifiers: Dict[str, Type[BaseNotifier]] = {}
        self._instances: Dict[str, BaseNotifier] = {}

        # Load built-in notifiers
        self._load_builtin_notifiers()

        # Load plugins if enabled
        if load_plugins:
            self._load_plugins()

    def _load_builtin_notifiers(self) -> None:
        """Load all built-in notifiers."""
        # Skip if notifiers directory doesn't exist
        if not self.NOTIFIERS_DIR.exists():
            return

        # Import all .py files in the notifiers directory
        for file in self.NOTIFIERS_DIR.glob("*.py"):
            if file.name.startswith("_"):
                continue

            module_name = f"notify_bridge.notifiers.{file.stem}"
            try:
                module = importlib.import_module(module_name)

                # Find all BaseNotifier subclasses in the module
                for attr_name in dir(module):
                    attr = getattr(module, attr_name)
                    if isinstance(attr, type) and issubclass(attr, BaseNotifier) and attr is not BaseNotifier:
                        self._notifiers[attr.name or attr_name.lower()] = attr
                        logger.info(f"Loaded built-in notifier: {attr.name or attr_name.lower()}")

            except Exception as e:
                logger.error(f"Failed to load notifier module {module_name}: {str(e)}")

    def _load_plugins(self) -> None:
        """Load notifier plugins from entry points."""
        try:
            plugins = get_notifiers_from_entry_points()
            for name, notifier_class in plugins.items():
                self._notifiers[name] = notifier_class
                logger.info(f"Loaded plugin notifier: {name}")
        except Exception as e:
            logger.error(f"Failed to load notifier plugins: {str(e)}")

    def get_notifier_class(self, name: str) -> Optional[Type[BaseNotifier]]:
        """Get a notifier class by name.

        Args:
            name: Name of the notifier class to get

        Returns:
            Optional[Type[BaseNotifier]]: The notifier class if found, None otherwise
        """
        return self._notifiers.get(name)

    def get_notifier_names(self) -> List[str]:
        """Get a list of all available notifier names.

        Returns:
            List[str]: List of notifier names
        """
        return sorted(list(self._notifiers.keys()))

    def create_notifier(self, name: str, **config: Any) -> BaseNotifier:
        """Create a notifier instance by name.

        Args:
            name: Name of the notifier to create
            **config: Configuration for the notifier

        Returns:
            BaseNotifier: The created notifier instance

        Raises:
            NoSuchNotifierError: If the notifier is not found
            PluginError: If there is an error creating the notifier
        """
        notifier_class = self.get_notifier_class(name)
        if not notifier_class:
            raise NoSuchNotifierError(name)

        try:
            instance = notifier_class(**config)
            self._instances[name] = instance
            return instance
        except Exception as e:
            raise PluginError(f"Failed to create notifier {name}: {str(e)}", name)

    async def acreate_notifier(self, name: str, **config: Any) -> BaseNotifier:
        """Create a notifier instance by name asynchronously.

        Args:
            name: Name of the notifier to create
            **config: Configuration for the notifier

        Returns:
            BaseNotifier: The created notifier instance

        Raises:
            NoSuchNotifierError: If the notifier is not found
            PluginError: If there is an error creating the notifier
        """
        return await asyncio.to_thread(self.create_notifier, name, **config)

    def get_instance(self, name: str) -> Optional[BaseNotifier]:
        """Get an existing notifier instance by name.

        Args:
            name: Name of the notifier instance to get

        Returns:
            Optional[BaseNotifier]: The notifier instance if found, None otherwise
        """
        return self._instances.get(name)

    def notify(self, name: str, notification: Union[NotificationSchema, dict], **kwargs: Any) -> NotificationResponse:
        """Send a notification using a notifier.

        Args:
            name: Name of the notifier to use
            notification: Notification data or schema instance
            **kwargs: Additional notification configuration

        Returns:
            NotificationResponse: The response from the notification attempt

        Raises:
            NoSuchNotifierError: If the notifier is not found
            PluginError: If there is an error creating the notifier
        """
        notifier = self.create_notifier(name, **kwargs)
        if isinstance(notification, dict):
            notification = notifier.validate(notification)
        return notifier.notify(notification)

    async def anotify(
        self, name: str, notification: Union[NotificationSchema, dict], **kwargs: Any
    ) -> NotificationResponse:
        """Send a notification using a notifier asynchronously.

        Args:
            name: Name of the notifier to use
            notification: Notification data or schema instance
            **kwargs: Additional notification configuration

        Returns:
            NotificationResponse: The response from the notification attempt

        Raises:
            NoSuchNotifierError: If the notifier is not found
            PluginError: If there is an error creating the notifier
        """
        notifier = self.create_notifier(name, **kwargs)
        if isinstance(notification, dict):
            notification = notifier.validate(notification)
        return await notifier.asend(notification)

    def close(self) -> None:
        """Close all notifier instances."""
        for instance in list(self._instances.values()):
            try:
                instance.close()
                del self._instances[instance.name]
            except Exception as e:
                logger.error(f"Error closing notifier {instance.name}: {str(e)}")

    async def aclose(self) -> None:
        """Close all notifier instances asynchronously."""
        for instance in list(self._instances.values()):
            try:
                await instance.aclose()
                del self._instances[instance.name]
            except Exception as e:
                logger.error(f"Error closing notifier {instance.name}: {str(e)}")

    def register_notifier(self, name: str, notifier_class: Type[BaseNotifier]) -> None:
        """Register a notifier class.

        Args:
            name: The name to register the notifier under.
            notifier_class: The notifier class to register.
        """
        self._notifiers[name] = notifier_class

    def unregister_notifier(self, name: str) -> None:
        """Unregister a notifier.

        Args:
            name: The name of the notifier to unregister.
        """
        if name in self._instances:
            del self._instances[name]
        if name in self._notifiers:
            del self._notifiers[name]

    def __del__(self) -> None:
        """Clean up resources when the factory is deleted."""
        self.close()
