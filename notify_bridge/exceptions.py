"""Exception classes for notify-bridge.

This module contains all custom exceptions used in notify-bridge.
"""

import os
import traceback
from typing import Any, Dict, Optional


class NotifyBridgeError(Exception):
    """Base exception class for notify-bridge.
    
    All exceptions in notify-bridge should inherit from this class.
    """
    def __init__(self, message: str):
        self.message = message
        super().__init__(self.message)


class ValidationError(NotifyBridgeError):
    """Raised when data validation fails.
    
    Args:
        message: Error message
        errors: Validation errors
        data: Invalid data that caused the error
    """
    def __init__(
        self,
        message: str,
        errors: Optional[Dict[str, Any]] = None,
        data: Optional[Dict[str, Any]] = None
    ):
        self.errors = errors or {}
        self.data = data or {}
        super().__init__(message)


class NotificationError(NotifyBridgeError):
    """Raised when sending a notification fails.
    
    Args:
        message: Error message
        notifier_name: Name of the notifier that failed
        response: Response from the notification service
        exception: Original exception that caused this error
    """

    @staticmethod
    def _format_file_url(file_path: str) -> str:
        """Format a file path for error messages.
        
        Args:
            file_path: Path to the file
            
        Returns:
            Formatted file path
        """
        abs_path = os.path.abspath(file_path)
        return abs_path

    @classmethod
    def from_exception(
        cls,
        exception: Exception,
        notifier_name: Optional[str] = None,
        response: Optional[Dict[str, Any]] = None
    ) -> "NotificationError":
        """Create NotificationError from another exception.
        
        Args:
            exception: Original exception
            notifier_name: Name of the notifier
            response: Response from the notification service
            
        Returns:
            NotificationError instance
        """
        # Get the traceback information
        tb = traceback.extract_tb(exception.__traceback__)[-1]
        file_path = cls._format_file_url(tb.filename)

        # Format the error message
        message = f'File "{file_path}", line {tb.lineno}, in {tb.name}\n'
        message += f"  {str(exception)}"

        return cls(
            message=message,
            notifier_name=notifier_name,
            response=response,
            exception=exception
        )

    def __init__(
        self,
        message: str,
        notifier_name: Optional[str] = None,
        response: Optional[Dict[str, Any]] = None,
        exception: Optional[Exception] = None
    ):
        self.notifier_name = notifier_name
        self.response = response or {}
        self.original_exception = exception
        super().__init__(message)


class ConfigurationError(NotifyBridgeError):
    """Raised when there is a configuration error.
    
    Args:
        message: Error message
        config_key: The configuration key that caused the error
        config_value: The invalid configuration value
    """
    def __init__(
        self,
        message: str,
        config_key: Optional[str] = None,
        config_value: Optional[Any] = None
    ):
        self.config_key = config_key
        self.config_value = config_value
        super().__init__(message)


class AuthenticationError(NotifyBridgeError):
    """Raised when authentication fails.
    
    Args:
        message: Error message
        provider: The authentication provider that failed
        details: Additional error details
    """
    def __init__(
        self,
        message: str,
        provider: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None
    ):
        self.provider = provider
        self.details = details or {}
        super().__init__(message)


class RateLimitError(NotifyBridgeError):
    """Raised when rate limit is exceeded.
    
    Args:
        message: Error message
        reset_time: When the rate limit will reset
        limit: The rate limit that was exceeded
        remaining: Number of remaining requests
    """
    def __init__(
        self,
        message: str,
        reset_time: Optional[int] = None,
        limit: Optional[int] = None,
        remaining: Optional[int] = None
    ):
        self.reset_time = reset_time
        self.limit = limit
        self.remaining = remaining
        super().__init__(message)


class NoSuchNotifierError(NotifyBridgeError):
    """Raised when a requested notifier is not found.
    
    Args:
        message: Error message
        notifier_name: Name of the notifier that was not found
        available_notifiers: List of available notifier names
    """
    def __init__(
        self,
        message: str,
        notifier_name: Optional[str] = None,
        available_notifiers: Optional[list[str]] = None
    ):
        self.notifier_name = notifier_name
        self.available_notifiers = available_notifiers or []
        super().__init__(message)


class PluginError(NotifyBridgeError):
    """Raised when there is an error with a plugin.
    
    Args:
        message: Error message
        plugin_name: Name of the plugin that caused the error
        plugin_path: Path to the plugin file
        details: Additional error details
    """
    def __init__(
        self,
        message: str,
        plugin_name: Optional[str] = None,
        plugin_path: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None
    ):
        self.plugin_name = plugin_name
        self.plugin_path = plugin_path
        self.details = details or {}
        super().__init__(message)
