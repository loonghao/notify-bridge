"""Exceptions used in notify-bridge."""


class NotifyBridgeError(Exception):
    """Base class for all notify-bridge exceptions."""


class ValidationError(NotifyBridgeError):
    """Raised when notification data validation fails."""

    def __init__(self, validation_error: str, notifier_name: str = None) -> None:
        self.validation_error = validation_error
        self.notifier_name = notifier_name
        super().__init__(
            f"Validation failed for notifier {notifier_name}: {validation_error}" if notifier_name else validation_error
        )


class NotificationError(NotifyBridgeError):
    """Raised when sending a notification fails."""

    def __init__(self, message: str, notifier_name: str = None, details: str = None) -> None:
        self.message = message
        self.notifier_name = notifier_name
        self.details = details
        super().__init__(f"{message} (notifier: {notifier_name})" if notifier_name else message)


class NoSuchNotifierError(NotifyBridgeError):
    """Raised when a notifier is not found."""

    def __init__(self, notifier_name: str) -> None:
        self.notifier_name = notifier_name
        super().__init__(f"No such notifier: {notifier_name}")


class PluginError(NotifyBridgeError):
    """Raised when there is an error with a plugin."""

    def __init__(self, message: str, plugin_name: str = None) -> None:
        self.message = message
        self.plugin_name = plugin_name
        super().__init__(f"{message} (plugin: {plugin_name})" if plugin_name else message)


class ConfigurationError(NotifyBridgeError):
    """Raised when there is an error in the configuration."""

    def __init__(self, message: str, notifier_name: str = None) -> None:
        self.message = message
        self.notifier_name = notifier_name
        super().__init__(f"{message} (notifier: {notifier_name})" if notifier_name else message)
