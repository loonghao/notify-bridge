"""Plugin utilities for notify-bridge."""

# Import built-in modules
import importlib
import inspect
import logging
import os
import sys

# Import third-party modules
from importlib import metadata
from typing import Dict, Optional, Type

from notify_bridge.components import BaseNotifier

# Import local modules
from notify_bridge.exceptions import PluginError

logger = logging.getLogger(__name__)

def load_notifier(entry_point: str) -> Type[BaseNotifier]:
    """Load a BaseNotifier class from a given entry point string.

    Args:
        entry_point: The entry point string.

    Returns:
        The notifier class.

    Raises:
        PluginError: If there is an error loading the plugin.
    """
    try:
        module_name, class_name = entry_point.split(":")
        module = importlib.import_module(module_name)
        notifier_class = getattr(module, class_name)
        if not (inspect.isclass(notifier_class) and issubclass(notifier_class, BaseNotifier)):
            raise PluginError(f"Plugin {entry_point} is not a valid BaseNotifier subclass")
        return notifier_class
    except (ImportError, AttributeError, ValueError) as e:
        raise PluginError(f"Failed to load plugin {entry_point}: {e}")

def get_notifiers_from_entry_points() -> Dict[str, Type[BaseNotifier]]:
    """Load notifier plugins from entry points.

    Returns:
        Dict[str, Type[BaseNotifier]]: A dictionary mapping notifier names to their classes.
    """
    notifiers = {}
    try:
        entry_points = metadata.entry_points()
        if hasattr(entry_points, 'select'):  # Python 3.10+
            notifier_eps = entry_points.select(group='notify_bridge.notifiers')
        else:  # Python 3.9 and below
            notifier_eps = entry_points.get('notify_bridge.notifiers', [])
            
        for ep in notifier_eps:
            try:
                notifier_class = load_notifier(f"{ep.module}:{ep.attr}")
                notifiers[notifier_class.name.lower()] = notifier_class
            except PluginError as e:
                logger.warning(f"Failed to load plugin {ep.name}: {e}")
    except Exception as e:
        logger.warning(f"Error occurred while loading entry points: {e}")
    return notifiers

def load_notifiers(package_name: str) -> Dict[str, Type[BaseNotifier]]:
    """Load notifiers from a specified package.

    Args:
        package_name: The name of the package to load notifiers from.

    Returns:
        Dict[str, Type[BaseNotifier]]: A dictionary mapping notifier names to their classes.
    """
    notifiers = {}
    try:
        package = importlib.import_module(package_name)
        for name, obj in inspect.getmembers(package):
            if inspect.isclass(obj) and issubclass(obj, BaseNotifier) and obj != BaseNotifier:
                notifiers[obj.name.lower()] = obj
    except ImportError as e:
        logger.error(f"Failed to import package {package_name}: {e}")
    return notifiers

def load_plugins(plugin_dir: str) -> Dict[str, Type[BaseNotifier]]:
    """Load plugins from the specified directory.

    Args:
        plugin_dir: The directory to load plugins from.

    Returns:
        Dict[str, Type[BaseNotifier]]: A dictionary mapping plugin names to plugin classes.
    """
    plugins: Dict[str, Type[BaseNotifier]] = {}
    if not os.path.exists(plugin_dir):
        logger.warning(f"Plugin directory does not exist: {plugin_dir}")
        return plugins

    sys.path.insert(0, os.path.dirname(plugin_dir))
    for file in os.listdir(plugin_dir):
        if file.endswith(".py") and not file.startswith("_"):
            module_name = file[:-3]
            try:
                module = importlib.import_module(module_name)
                for name, obj in inspect.getmembers(module):
                    if inspect.isclass(obj) and issubclass(obj, BaseNotifier) and obj != BaseNotifier:
                        plugins[obj.name.lower()] = obj
            except ImportError as e:
                logger.error(f"Failed to import plugin {module_name}: {e}")
    sys.path.pop(0)
    return plugins

def get_all_notifiers(plugin_dir: Optional[str] = None) -> Dict[str, Type[BaseNotifier]]:
    """Get all available notifiers from various sources.

    Args:
        plugin_dir: Optional directory to load additional plugins from.

    Returns:
        Dict[str, Type[BaseNotifier]]: A dictionary mapping notifier names to their classes.
    """
    notifiers = load_notifiers('notify_bridge.notifiers')  # Built-in notifiers
    notifiers.update(get_notifiers_from_entry_points())  # Entry point notifiers
    if plugin_dir:
        notifiers.update(load_plugins(plugin_dir))  # Custom plugin directory
    return notifiers

def get_notifier_class(name: str, plugin_dir: Optional[str] = None) -> Type[BaseNotifier]:
    """Get a notifier class by name.

    Args:
        name: The name of the notifier class.
        plugin_dir: Optional directory to load additional plugins from.

    Returns:
        The notifier class.

    Raises:
        PluginError: If the notifier class is not found.
    """
    notifiers = get_all_notifiers(plugin_dir)
    name_lower = name.lower()
    if name_lower not in notifiers:
        raise PluginError(f"No such notifier: {name}")
    return notifiers[name_lower]
