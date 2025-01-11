"""Tests for GitHub notifier."""

# Import third-party modules
from pydantic import ValidationError
import pytest

# Import local modules
from notify_bridge.components import MessageType
from notify_bridge.components import NotificationError
from notify_bridge.notifiers.github import GitHubNotifier
from notify_bridge.notifiers.github import GitHubSchema


def test_github_schema_validation():
    """Test GitHub schema validation."""
    # Test valid schema with new usage
    valid_data = {
        "owner": "test-owner",
        "repo": "test-repo",
        "token": "test-token",
        "title": "Test Issue",
        "message": "Test content",  # Using message instead of content
        "labels": ["bug", "help wanted"],
        "assignees": ["user1", "user2"],
        "milestone": 1,
        "msg_type": "text",
    }
    schema = GitHubSchema(**valid_data)
    assert schema.owner == "test-owner"
    assert schema.repo == "test-repo"
    assert schema.token == "test-token"
    assert schema.content == "Test content"  # Verify content is set from message
    assert schema.labels == ["bug", "help wanted"]
    assert schema.assignees == ["user1", "user2"]
    assert schema.milestone == 1
    assert schema.msg_type == MessageType.TEXT

    # Test required fields
    with pytest.raises(ValidationError):
        GitHubSchema(title="Test")  # Missing required fields


def test_github_notifier_initialization():
    """Test GitHub notifier initialization."""
    notifier = GitHubNotifier()
    assert notifier.name == "github"
    assert notifier.schema_class == GitHubSchema
    assert MessageType.TEXT in notifier.supported_types
    assert MessageType.MARKDOWN in notifier.supported_types


def test_github_headers():
    """Test GitHub headers generation."""
    notifier = GitHubNotifier()
    token = "test-token"
    headers = notifier._get_headers(token)

    assert headers["Accept"] == "application/vnd.github+json"
    assert headers["Authorization"] == f"Bearer {token}"
    assert headers["X-GitHub-Api-Version"] == "2022-11-28"


def test_github_build_payload():
    """Test GitHub payload building."""
    notifier = GitHubNotifier()

    # Test with minimal data using new usage
    minimal_data = {
        "owner": "test-owner",
        "repo": "test-repo",
        "token": "test-token",
        "title": "Test Issue",
        "message": "Test content",  # Using message instead of content
        "msg_type": "text",
    }
    notification = GitHubSchema(**minimal_data)
    payload = notifier.build_payload(notification)

    assert payload["title"] == "Test Issue"
    assert payload["body"] == "Test content"
    assert "labels" not in payload
    assert "assignees" not in payload
    assert "milestone" not in payload

    # Test with all optional fields using new usage
    full_data = {
        "owner": "test-owner",
        "repo": "test-repo",
        "token": "test-token",
        "title": "Test Issue",
        "message": "Test content",  # Using message instead of content
        "labels": ["bug"],
        "assignees": ["user1"],
        "milestone": 1,
        "msg_type": "text",
    }
    notification = GitHubSchema(**full_data)
    payload = notifier.build_payload(notification)

    assert payload["title"] == "Test Issue"
    assert payload["body"] == "Test content"
    assert payload["labels"] == ["bug"]
    assert payload["assignees"] == ["user1"]
    assert payload["milestone"] == 1

    # Test with invalid schema
    with pytest.raises(NotificationError):
        notifier.build_payload(object())  # Pass invalid schema object


def test_github_webhook_url():
    """Test GitHub webhook URL generation."""
    notifier = GitHubNotifier()
    data = {
        "owner": "test-owner",
        "repo": "test-repo",
        "token": "test-token",
        "title": "Test Issue",
        "message": "Test content",  # Using message instead of content
        "msg_type": "text",
    }
    notification = GitHubSchema(**data)
    notifier.build_payload(notification)

    expected_url = "https://api.github.com/repos/test-owner/test-repo/issues"
    assert notification.webhook_url == expected_url
