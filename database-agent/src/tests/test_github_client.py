"""Tests for the GitHub client."""

from datetime import datetime
from unittest.mock import MagicMock, patch

import pytest

from database_agent.github_client import GitHubClient


@pytest.fixture
def mock_github():
    """Create a mock GitHub instance."""
    with patch("database_agent.github_client.Github") as mock:
        client = mock.return_value
        repo = MagicMock()
        pr = MagicMock()
        pr.number = 1
        pr.title = "Test PR"
        pr.body = "Test body"
        pr.state = "open"
        pr.created_at = datetime.now()
        pr.updated_at = datetime.now()
        label = MagicMock()
        label.name = "test"
        pr.labels = [label]
        comment = MagicMock()
        comment.body = "test comment"
        pr.get_issue_comments.return_value = [comment]
        repo.get_pulls.return_value = [pr]
        repo.get_pull.return_value = pr
        client.get_repo.return_value = repo
        yield client


@pytest.fixture
def github_client(mock_github):
    """Create a GitHubClient instance with mocked GitHub."""
    return GitHubClient(token="test-token")


def test_github_client_initialization(github_client):
    """Test GitHub client initialization."""
    assert github_client is not None
    assert github_client.token == "test-token"


def test_get_repository(github_client, mock_github):
    """Test getting a repository."""
    repo = github_client.get_repository("owner/repo")
    assert repo is not None
    mock_github.get_repo.assert_called_once_with("owner/repo")


def test_get_pull_requests(github_client, mock_github):
    """Test getting pull requests."""
    prs = github_client.get_pull_requests("owner/repo")
    assert len(prs) == 1
    assert prs[0].number == 1
    assert prs[0].title == "Test PR"


def test_get_pull_request_comments(github_client, mock_github):
    """Test getting pull request comments."""
    comments = github_client.get_pull_request_comments("owner/repo", 1)
    assert len(comments) == 1
    assert comments[0] == "test comment"


def test_get_pull_request_labels(github_client, mock_github):
    """Test getting pull request labels."""
    labels = github_client.get_pull_request_labels("owner/repo", 1)
    assert len(labels) == 1
    assert labels[0] == "test"


def test_get_pull_request_state(github_client, mock_github):
    """Test getting pull request state."""
    state = github_client.get_pull_request_state("owner/repo", 1)
    assert state == "open"


def test_get_pull_request_dates(github_client, mock_github):
    """Test getting pull request dates."""
    created_at, updated_at = github_client.get_pull_request_dates("owner/repo", 1)
    assert isinstance(created_at, datetime)
    assert isinstance(updated_at, datetime)
