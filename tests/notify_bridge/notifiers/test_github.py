"""Tests for GitHub notifier."""

# Import third-party modules
from pydantic import ValidationError
import pytest

# Import local modules
from notify_bridge.components import MessageType
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


@pytest.fixture
def github_notifier():
    return GitHubNotifier()


@pytest.fixture
def github_data():
    return {
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


def test_github_assemble_data(github_notifier, github_data):
    """Test GitHub notifier assemble_data method."""
    data = github_notifier.validate(github_data)
    payload = github_notifier.assemble_data(data)
    assert payload["title"] == github_data["title"]
    assert payload["body"] == github_data["message"]
    assert payload["labels"] == github_data.get("labels", [])
    assert payload["assignees"] == github_data.get("assignees", [])


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
    notifier.assemble_data(notification)

    expected_url = "https://api.github.com/repos/test-owner/test-repo/issues"
    assert notification.webhook_url == expected_url
