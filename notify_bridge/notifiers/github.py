"""GitHub notifier implementation.

This module provides the GitHub Issues notification implementation.
"""

# Import built-in modules
import logging
from typing import Any, Dict, List, Optional

# Import third-party modules
from pydantic import Field

# Import local modules
from notify_bridge.components import BaseNotifier, MessageType, NotificationError, NotificationSchema

logger = logging.getLogger(__name__)


class GitHubSchema(NotificationSchema):
    """Schema for GitHub notifications."""
    owner: str = Field(..., description="Repository owner")
    repo: str = Field(..., description="Repository name")
    token: str = Field(..., description="GitHub personal access token")
    labels: Optional[List[str]] = Field(None, description="Issue labels")
    assignees: Optional[List[str]] = Field(None, description="Issue assignees")
    milestone: Optional[int] = Field(None, description="Issue milestone number")


class GitHubNotifier(BaseNotifier):
    """GitHub notifier implementation."""

    name = "github"
    schema_class = GitHubSchema
    supported_types = {MessageType.TEXT, MessageType.MARKDOWN}

    def _get_headers(self, token: str) -> Dict[str, str]:
        """Get request headers.

        Args:
            token: GitHub personal access token

        Returns:
            Dict[str, str]: Request headers
        """
        return {
            "Accept": "application/vnd.github+json",
            "Authorization": f"Bearer {token}",
            "X-GitHub-Api-Version": "2022-11-28"
        }

    def build_payload(self, notification: NotificationSchema) -> Dict[str, Any]:
        """Build notification payload.

        Args:
            notification: Notification data.

        Returns:
            Dict[str, Any]: API payload.

        Raises:
            NotificationError: If payload building fails.
        """
        if not isinstance(notification, GitHubSchema):
            raise NotificationError("Invalid notification schema")

        # Set webhook URL if not set
        if not notification.webhook_url:
            notification.webhook_url = f"https://api.github.com/repos/{notification.owner}/{notification.repo}/issues"

        # Set headers with token
        notification.headers.update(self._get_headers(notification.token))

        # Build basic payload
        payload = {
            "title": notification.title or "New Issue",
            "body": notification.content
        }

        # Add optional fields
        if notification.labels:
            payload["labels"] = notification.labels
        if notification.assignees:
            payload["assignees"] = notification.assignees
        if notification.milestone:
            payload["milestone"] = notification.milestone

        return payload
