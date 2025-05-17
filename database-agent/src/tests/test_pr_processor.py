"""Tests for the PR processor."""

import pytest
from unittest.mock import MagicMock, patch
from datetime import datetime
from database_agent.pr_processor import PRProcessor
from database_agent.exceptions import PRProcessingError

@pytest.fixture
def mock_github_client():
    """Create a mock GitHub client."""
    client = MagicMock()
    client.get_repository.return_value = MagicMock()
    client.get_pull_requests.return_value = [
        MagicMock(
            number=1,
            title="Test PR",
            body="Test body",
            state="open",
            created_at=datetime.now(),
            updated_at=datetime.now(),
            labels=[MagicMock(name="test")],
            get_comments=MagicMock(return_value=[MagicMock(body="test comment")])
        )
    ]
    return client

@pytest.fixture
def mock_vector_store():
    """Create a mock vector store."""
    store = MagicMock()
    store.store_pr.return_value = True
    store.store_prs_batch.return_value = True
    store.search_similar_prs.return_value = [
        {"id": 1, "score": 0.9, "payload": {"title": "Test PR"}},
        {"id": 2, "score": 0.8, "payload": {"title": "Another PR"}}
    ]
    return store

@pytest.fixture
def pr_processor(mock_github_client, mock_vector_store):
    """Create a PRProcessor instance with mocked dependencies."""
    return PRProcessor(
        github_client=mock_github_client,
        vector_store=mock_vector_store
    )

def test_pr_processor_initialization(pr_processor):
    """Test PR processor initialization."""
    assert pr_processor is not None
    assert pr_processor.github_client is not None
    assert pr_processor.vector_store is not None

def test_process_pr(pr_processor, mock_github_client, mock_vector_store):
    """Test processing a single PR."""
    pr_data = {
        "id": 1,
        "title": "Test PR",
        "body": "Test body",
        "labels": ["test"],
        "state": "open",
        "created_at": datetime.now().isoformat(),
        "updated_at": datetime.now().isoformat(),
        "author": "test-author",
        "repo_name": "owner/repo"
    }
    result = pr_processor.process_pr(pr_data)
    assert result is True
    mock_vector_store.store_pr.assert_called_once()

def test_process_prs_batch(pr_processor, mock_github_client, mock_vector_store):
    """Test processing multiple PRs in batch."""
    prs_data = [
        {"id": 1, "title": "PR 1", "body": "Body 1"},
        {"id": 2, "title": "PR 2", "body": "Body 2"}
    ]
    result = pr_processor.process_prs_batch(prs_data)
    assert result is True
    mock_vector_store.store_prs_batch.assert_called_once()

def test_process_repository_prs(pr_processor, mock_github_client, mock_vector_store):
    """Test processing PRs from a repository."""
    result = pr_processor.process_repository_prs("owner/repo")
    assert result is True
    mock_github_client.get_pull_requests.assert_called_once_with("owner/repo")
    mock_vector_store.store_prs_batch.assert_called_once()

def test_search_similar_prs(pr_processor, mock_vector_store):
    """Test searching for similar PRs."""
    results = pr_processor.search_similar_prs("test query", limit=2)
    assert len(results) == 2
    assert results[0]["id"] == 1
    assert results[0]["score"] == 0.9
    assert results[1]["id"] == 2
    assert results[1]["score"] == 0.8

def test_process_pr_handles_error(pr_processor, mock_vector_store):
    """Test processing PR handles error."""
    mock_vector_store.store_pr.side_effect = Exception("Storage Error")
    with pytest.raises(PRProcessingError):
        pr_processor.process_pr({"id": 1, "title": "Test PR"})

def test_process_prs_batch_handles_error(pr_processor, mock_vector_store):
    """Test processing PRs batch handles error."""
    mock_vector_store.store_prs_batch.side_effect = Exception("Storage Error")
    with pytest.raises(PRProcessingError):
        pr_processor.process_prs_batch([{"id": 1, "title": "Test PR"}])

def test_process_repository_prs_handles_error(pr_processor, mock_github_client):
    """Test processing repository PRs handles error."""
    mock_github_client.get_pull_requests.side_effect = Exception("API Error")
    with pytest.raises(PRProcessingError):
        pr_processor.process_repository_prs("owner/repo") 