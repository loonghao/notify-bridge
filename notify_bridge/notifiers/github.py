"""GitHub notifier implementation.

This module provides the GitHub Issues data implementation.
"""

# Import built-in modules
import logging
from typing import Any, ClassVar, Dict, List, Optional

# Import third-party modules
from pydantic import Field, model_validator

# Import local modules
from notify_bridge.components import BaseNotifier, MessageType, NotificationError
from notify_bridge.schema import WebhookSchema

logger = logging.getLogger(__name__)


class GitHubSchema(WebhookSchema):
    """Schema for GitHub notifications."""

    owner: str = Field(..., description="Repository owner")
    repo: str = Field(..., description="Repository name")
    title: str = Field(..., description="Issue title")
    body: Optional[str] = Field(None, description="Issue body")
    message: Optional[str] = Field(None, description="Issue message")
    content: Optional[str] = Field(None, description="Issue content")
    labels: Optional[List[str]] = Field(None, description="Issue labels")
    assignees: Optional[List[str]] = Field(None, description="Issue assignees")
    webhook_url: Optional[str] = Field(None, description="GitHub API URL")
    token: str = Field(..., description="GitHub personal access token")

    @model_validator(mode="before")
    @classmethod
    def set_webhook_url(cls, values: Dict[str, Any]) -> Dict[str, Any]:
        """Set webhook URL if not provided.

        Args:
            values: Field values

        Returns:
            Dict[str, Any]: Updated field values
        """
        if not values.get("webhook_url"):
            owner = values.get("owner")
            repo = values.get("repo")
            if owner and repo:
                values["webhook_url"] = f"https://api.github.com/repos/{owner}/{repo}/issues"
        return values

    @model_validator(mode="before")
    @classmethod
    def set_content_and_body(cls, values: Dict[str, Any]) -> Dict[str, Any]:
        """Set content and body from message if not provided.

        Args:
            values: Field values

        Returns:
            Dict[str, Any]: Updated field values
        """
        message = values.get("message")
        if message:
            if not values.get("content"):
                values["content"] = message
            if not values.get("body"):
                values["body"] = message
        return values

    class Config:
        """Pydantic model configuration."""

        populate_by_name = True


class GitHubNotifier(BaseNotifier):
    """GitHub notifier implementation."""

    name = "github"
    schema_class = GitHubSchema
    supported_types: ClassVar[set[MessageType]] = {MessageType.TEXT, MessageType.MARKDOWN}
    http_method = "POST"

    def assemble_data(self, data: GitHubSchema) -> Dict[str, Any]:
        """Assemble data data.

        Args:
            data: Notification data

        Returns:
            Dict[str, Any]: API payload
        """
        # Set headers with token
        data.headers.update({
            "Authorization": f"token {data.token}",
            "Accept": "application/vnd.github.v3+json"
        })

        # Get body content
        body = data.body or data.content or data.message
        if not body:
            raise NotificationError("body, content or message is required", notifier_name=self.name)

        # Convert markdown if needed
        if data.msg_type == MessageType.MARKDOWN:
            body = f"```markdown\n{body}\n```"

        payload = {
            "title": data.title,
            "body": body,
        }

        if data.labels:
            payload["labels"] = data.labels
        if data.assignees:
            payload["assignees"] = data.assignees

        return payload
