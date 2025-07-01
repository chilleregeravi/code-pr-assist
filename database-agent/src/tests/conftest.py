"""Shared test fixtures for database agent tests."""

from unittest.mock import MagicMock, patch

import pytest

from database_agent.database_agent import DatabaseAgent


@pytest.fixture
def mock_qdrant_url():
    return "http://localhost:6333"


@pytest.fixture
def mock_qdrant_api_key():
    return "test-api-key"


@pytest.fixture
def mock_github_token():
    return "test-github-token"


@pytest.fixture
def mock_vector_store():
    with patch("database_agent.vector_store.QdrantStore") as mock:
        store = mock.return_value
        store.generate_embedding.return_value = [0.1, 0.2, 0.3]
        store.store_pr.return_value = True
        store.store_prs_batch.return_value = True
        store.search_similar_prs.return_value = [
            {"id": 1, "score": 0.9},
            {"id": 2, "score": 0.8},
        ]
        store.get_pr.return_value = {
            "id": 1,
            "title": "Test PR",
            "body": "Test body",
            "state": "open",
            "created_at": "2024-01-01T00:00:00Z",
            "updated_at": "2024-01-01T00:00:00Z",
            "labels": ["test"],
            "comments": ["test comment"],
        }
        store.delete_pr.return_value = True
        store.delete_collection.return_value = True
        yield store


@pytest.fixture
def mock_github_client():
    with patch("database_agent.github_client.Github") as mock:
        client = mock.return_value
        repo = MagicMock()
        pr = MagicMock()
        pr.number = 1
        pr.title = "Test PR"
        pr.body = "Test body"
        pr.state = "open"
        pr.created_at = "2024-01-01T00:00:00Z"
        pr.updated_at = "2024-01-01T00:00:00Z"
        pr.labels = [MagicMock(name="test")]
        pr.get_comments.return_value = [MagicMock(body="test comment")]
        repo.get_pulls.return_value = [pr]
        client.get_repo.return_value = repo
        yield client


@pytest.fixture(scope="session")
def test_config():
    """Provide a test configuration dictionary."""
    return {"log_level": "INFO", "database": {"type": "test", "url": "test://database"}}


@pytest.fixture(scope="session")
def database_agent(test_config):
    """Create a DatabaseAgent instance with test configuration."""
    return DatabaseAgent(config=test_config)
