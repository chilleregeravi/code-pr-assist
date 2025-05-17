from unittest.mock import MagicMock, patch

import pytest
from database_agent.github_client import GitHubClient, PRProcessingError


@pytest.fixture
def github_client():
    with patch("database_agent.github_client.Github") as mock:
        client = GitHubClient(token="test-token")
        mock_instance = mock.return_value
        repo = MagicMock()
        pr = MagicMock()
        pr.number = 1
        pr.title = "Test PR"
        pr.body = "Test body"
        pr.state = "open"
        pr.created_at = MagicMock(isoformat=lambda: "2024-01-01T00:00:00Z")
        pr.updated_at = MagicMock(isoformat=lambda: "2024-01-01T00:00:00Z")
        pr.user.login = "testuser"
        pr.labels = [MagicMock(name="test", name_attr="test")]
        pr.get_issue_comments.return_value = [MagicMock(body="test comment")]
        pr.get_reviews.return_value = []
        pr.get_files.return_value = []
        pr.additions = 1
        pr.deletions = 1
        pr.changed_files = 1
        pr.base.ref = "main"
        pr.head.ref = "feature"
        pr.mergeable = True
        pr.mergeable_state = "clean"
        pr.review_comments = 0
        pr.commits = 1
        repo.get_pull.return_value = pr
        repo.get_pulls.return_value = [pr]
        mock_instance.get_repo.return_value = repo
        yield client


def test_get_pr_data_success(github_client):
    data = github_client.get_pr_data("owner/repo", 1)
    assert data["id"] == 1
    assert data["title"] == "Test PR"
    assert data["author"] == "testuser"
    assert data["comments"] == ["test comment"]
    assert data["labels"] == [
        label.name for label in github_client.client.get_repo().get_pull().labels
    ]


def test_get_pr_data_error():
    with patch("database_agent.github_client.Github") as mock:
        client = GitHubClient(token="test-token")
        mock_instance = mock.return_value
        mock_instance.get_repo.side_effect = Exception("fail")
        with pytest.raises(Exception):
            client.get_pr_data("owner/repo", 1)


def test_get_repo_prs_limit(github_client):
    prs = list(github_client.get_repo_prs("owner/repo", limit=1))
    assert len(prs) == 1
    assert prs[0]["id"] == 1


def test_process_and_store_prs_batches():
    with patch("database_agent.github_client.Github") as mock:
        client = GitHubClient(token="test-token")
        client.batch_size = 2
        mock_instance = mock.return_value
        repo = MagicMock()
        pr = MagicMock()
        pr.number = 1
        repo.get_pulls.return_value = [pr, pr, pr]
        mock_instance.get_repo.return_value = repo
        client.get_pr_data = MagicMock(return_value={"id": 1})
        pr_processor = MagicMock()
        client.process_and_store_prs(pr_processor, "owner/repo", limit=3)
        # Should call process_and_store_pr 3 times (once per PR)
        assert pr_processor.process_and_store_pr.call_count == 3


def test_search_prs_with_and_without_repo_name():
    with patch("database_agent.github_client.Github"):
        client = GitHubClient(token="test-token")
        pr_processor = MagicMock()
        pr_processor.search_similar_prs.return_value = [
            {"payload": {"repo_name": "owner/repo"}},
            {"payload": {"repo_name": "other/repo"}},
        ]
        # Without repo_name filter
        results = client.search_prs(pr_processor, "query")
        assert len(results) == 2
        # With repo_name filter
        results = client.search_prs(pr_processor, "query", repo_name="owner/repo")
        assert len(results) == 1
        assert results[0]["payload"]["repo_name"] == "owner/repo"


def test_process_repository_prs_calls_processor():
    with patch("database_agent.github_client.Github"):
        client = GitHubClient(token="test-token")
        pr = MagicMock()
        pr.number = 1
        pr.title = "Test PR"
        pr.body = "Test body"
        pr.labels = [MagicMock(name="test", name_attr="test")]
        client.get_pull_requests = MagicMock(return_value=[pr])
        client._extract_pr_data = MagicMock(return_value={"id": 1})
        processor = MagicMock()
        client.process_repository_prs("owner/repo", processor)
        processor.process_pr.assert_called_once_with({"id": 1})


def test_process_repository_prs_error():
    with patch("database_agent.github_client.Github"):
        client = GitHubClient(token="test-token")
        client.get_pull_requests = MagicMock(side_effect=Exception("fail"))
        processor = MagicMock()
        with pytest.raises(PRProcessingError):
            client.process_repository_prs("owner/repo", processor)
