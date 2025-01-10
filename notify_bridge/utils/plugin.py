"""Plugin utilities."""

# Import built-in modules
import importlib
import logging
from typing import Dict, Type

# Import local modules
from notify_bridge.exceptions import PluginError
from notify_bridge.types import BaseNotifier

logger = logging.getLogger(__name__)


def load_notifier_from_entry_point(entry_point) -> Type[BaseNotifier]:
    """Load a BaseNotifier class from a given entry point string.

    Args:
        entry_point: A string in the format 'module_path:class_name'
            (e.g. 'myapp.notifiers:EmailNotifier')

    Returns:
        Type[BaseNotifier]: The loaded notifier class

    Raises:
        PluginError: If the entry point format is invalid, the module cannot be imported,
            the class cannot be found, or the class is not a subclass of BaseNotifier.

    Example:
        >>> entry_point = "myapp.notifiers:EmailNotifier"
        >>> notifier_class = load_notifier_from_entry_point(entry_point)
        >>> notifier = notifier_class()
    """
    try:
        entry_point_value = entry_point.value
    except AttributeError:
        entry_point_value = entry_point

    if not entry_point_value or entry_point_value.count(":") != 1:
        raise PluginError(f"Invalid entry point format: {entry_point_value}. Expected format: 'module_path:class_name'")

    try:
        module_path, class_name = entry_point_value.split(":")
        module = importlib.import_module(module_path)
        notifier_class = getattr(module, class_name)
    except (ImportError, AttributeError) as e:
        raise PluginError(f"Failed to import notifier class: {e}")

    if not issubclass(notifier_class, BaseNotifier):
        raise PluginError(f"Class {class_name} is not a subclass of BaseNotifier")

    return notifier_class


def get_notifiers_from_entry_points() -> Dict[str, Type[BaseNotifier]]:
    """Get all notifier classes from entry points.

    Returns:
        Dict[str, Type[BaseNotifier]]: A dictionary mapping notifier names to their classes.

    Example:
        >>> notifiers = get_notifiers_from_entry_points()
        >>> for name, notifier_class in notifiers.items():
        ...     print(f"{name}: {notifier_class}")
    """
    notifiers = {}
    try:
        # Import built-in modules
        import importlib.metadata as metadata
    except ImportError:
        # Import third-party modules
        import importlib_metadata as metadata  # type: ignore

    entry_points = metadata.entry_points()
    if hasattr(entry_points, "select"):
        selected_entry_points = entry_points.select(group="notify_bridge.notifiers")
    else:
        selected_entry_points = entry_points.get("notify_bridge.notifiers", [])

    for entry_point in selected_entry_points:
        try:
            notifier_class = load_notifier_from_entry_point(entry_point)
            notifiers[entry_point.name] = notifier_class
        except PluginError:
            continue

    return notifiers


def get_builtin_notifiers() -> Dict[str, Type[BaseNotifier]]:
    """Get a dictionary of built-in notifier plugins.

    Returns:
        Dict[str, Type[BaseNotifier]]: A dictionary mapping notifier names to their classes.
    """
    result: Dict[str, Type[BaseNotifier]] = {}

    try:
        # Import the notifiers package
        # Import built-in modules
        import inspect

        # Get all available notifier modules
        import pkgutil

        # Import local modules
        import notify_bridge.notifiers as notifiers_pkg

        # Iterate through all modules in the notifiers package
        for _, name, _ in pkgutil.iter_modules(notifiers_pkg.__path__):
            try:
                # Import the module
                module = importlib.import_module(f"notify_bridge.notifiers.{name}")

                # Find all classes in the module that are subclasses of BaseNotifier
                for _, obj in inspect.getmembers(module, inspect.isclass):
                    if issubclass(obj, BaseNotifier) and obj != BaseNotifier:
                        # Use the notifier's name attribute if available, otherwise use lowercase class name
                        notifier_name = getattr(obj, "name", obj.__name__.lower().replace("notifier", ""))
                        result[notifier_name] = obj

            except Exception as err:
                logger.error(f"Failed to load built-in notifier {name}: {str(err)}")

    except Exception as err:
        logger.error(f"Failed to load built-in notifiers: {str(err)}")

    return result


def get_all_notifiers() -> Dict[str, Type[BaseNotifier]]:
    """Get a dictionary of all available notifier plugins, including built-in and entry points.

    Returns:
        Dict[str, Type[BaseNotifier]]: A dictionary mapping notifier names to their classes.
    """
    # Get built-in notifiers first
    result = get_builtin_notifiers()

    try:
        # Get notifiers from entry points, they can override built-in ones
        entry_point_notifiers = get_notifiers_from_entry_points()
        result.update(entry_point_notifiers)
    except Exception as err:
        logger.error(f"Failed to load entry point notifiers: {str(err)}")

    return result
