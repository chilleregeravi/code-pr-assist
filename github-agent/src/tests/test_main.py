"""Tests for the FastAPI application."""

import logging
from unittest.mock import Mock, patch

import numpy as np
import pytest
from fastapi.testclient import TestClient

logger = logging.getLogger(__name__)
logger.info("Starting test file")

# Mock OpenAI and Qdrant before importing app
with (
    patch("github_agent.agents.embedding_agent.OpenAI") as mock_openai_class,
    patch("github_agent.agents.llm_agent.OpenAI") as mock_openai_llm_class,
    patch("github_agent.llm_utils.OpenAI") as mock_openai_utils_class,
    patch("github_agent.agents.embedding_agent.QdrantClient") as mock_qdrant,
    patch.dict(
        "os.environ",
        {
            "OPENAI_API_KEY": "test-key",
            "GITHUB_TOKEN": "test-token",
            "REPO_NAME": "test/repo",
        },
    ),
):
    # Setup OpenAI client mock with embeddings and chat completions
    mock_client = Mock()
    mock_chat_response_obj = Mock()
    mock_embed_data_obj = Mock()
    mock_embed_data_obj.data = [Mock(embedding=[0.1] * 1536)]
    mock_chat_response_obj.choices = [Mock(message=Mock(content="Test summary"))]

    # Configure chat completions and embeddings on the same mock
    mock_client.configure_mock(
        **{
            "embeddings.create.return_value": mock_embed_data_obj,
            "chat.completions.create.return_value": mock_chat_response_obj,
        }
    )

    # Configure all OpenAI class mocks to return the same client
    mock_openai_class.return_value = mock_client
    mock_openai_llm_class.return_value = mock_client
    mock_openai_utils_class.return_value = mock_client

    # Setup Qdrant mock
    mock_qdrant.return_value.collection_exists.return_value = True
    from github_agent.main import app


@pytest.fixture
def client():
    """Create a test client."""
    return TestClient(app)


@pytest.fixture
def mock_agents():
    """Mock all agents used in the application."""
    # Create mock responses
    mock_embed_data = Mock()
    mock_embed_data.data = [Mock(embedding=np.array([0.1] * 1536))]

    mock_chat_response = Mock()
    mock_chat_response.choices = [Mock(message=Mock(content="Test summary"))]

    # Setup OpenAI client mock with embeddings and chat completions
    mock_embed_client = Mock()
    mock_embed_client.embeddings.create.return_value = mock_embed_data
    mock_embed_client.chat.completions.create.return_value = mock_chat_response

    # First patch configuration values and clients
    with (
        patch.dict(
            "os.environ",
            {
                "OPENAI_API_KEY": "test_key",
                "GITHUB_TOKEN": "test_token",
                "REPO_NAME": "test/repo",
            },
        ),
        patch("github_agent.main.embedding_agent") as mock_embedding_agent,
        patch("github_agent.main.llm_agent") as mock_llm_agent,
        patch("github_agent.main.github_agent") as mock_github_agent,
        patch("github_agent.github_utils.get_repo") as mock_get_repo,
        patch("github_agent.main.logger"),
    ):
        # Setup embedding agent mock
        mock_embedding_agent.embed.return_value = np.array([0.1] * 1536)
        mock_embedding_agent.search_similar.return_value = [
            {"text": "Similar PR 1"},
            {"text": "Similar PR 2"},
        ]
        mock_embedding_agent.upsert.return_value = None

        # Setup LLM agent mock
        mock_llm_agent.summarize_with_context.return_value = "Test summary"

        # Setup GitHub agent mock
        mock_github_agent.post_comment.return_value = None

        # Setup GitHub mocks
        mock_repo = Mock()
        mock_pr = Mock()
        mock_get_repo.return_value = mock_repo
        mock_repo.get_pull.return_value = mock_pr
        mock_pr.create_issue_comment.return_value = None

        # Return everything needed for tests
        yield {
            "get_repo": mock_get_repo,
            "repo": mock_repo,
            "pr": mock_pr,
            "embed_client": mock_embed_client,
            "embedding_agent": mock_embedding_agent,
            "llm_agent": mock_llm_agent,
            "github_agent": mock_github_agent,
            "openai": mock_embed_client,
        }


def test_root_endpoint(client):
    """Test the root endpoint."""
    response = client.get("/")
    assert response.status_code == 200
    assert "GitHub PR Agent" in response.json()["message"]


def test_health_endpoint(client):
    """Test the health check endpoint."""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}


def test_webhook_pr_opened(client, mock_agents):
    """Test webhook handling for PR opened event."""
    payload = {
        "action": "opened",
        "pull_request": {
            "number": 123,
            "title": "Test PR",
            "body": "Test description",
            "diff_url": "https://github.com/test/diff",
            "user": {"login": "test-user"},
            "base": {"ref": "main"},
            "head": {"ref": "feature"},
        },
    }

    response = client.post(
        "/webhook", headers={"X-GitHub-Event": "pull_request"}, json=payload
    )

    assert response.status_code == 200
    response_json = response.json()
    assert response_json["status"] == "processed"
    assert response_json["comment_posted"]
    assert response_json["embedding_stored"]

    # Verify all operations were attempted
    mock_agents["embedding_agent"].embed.assert_called()
    mock_agents["embedding_agent"].search_similar.assert_called()
    mock_agents["embedding_agent"].upsert.assert_called()
    mock_agents["llm_agent"].summarize_with_context.assert_called()
    mock_agents["github_agent"].post_comment.assert_called()


def test_webhook_invalid_event(client):
    """Test webhook handling for invalid event."""
    response = client.post("/webhook", headers={"X-GitHub-Event": "invalid"}, json={})
    assert response.status_code == 400
    assert "Unsupported event" in response.json()["detail"]


def test_webhook_missing_header(client):
    """Test webhook handling with missing event header."""
    response = client.post("/webhook", json={})
    assert response.status_code == 400
    assert "Missing X-GitHub-Event header" in response.json()["detail"]


def test_webhook_invalid_payload(client):
    """Test webhook handling with invalid payload."""
    response = client.post(
        "/webhook",
        headers={"X-GitHub-Event": "pull_request"},
        json={"action": "opened"},  # Missing required fields
    )
    assert response.status_code == 422  # Validation error


def test_webhook_missing_pr_fields(client):
    """Test webhook handling with missing PR fields."""
    payload = {
        "action": "opened",
        "pull_request": {
            "number": 123,
            # Missing title, body, and diff_url
        },
    }
    response = client.post(
        "/webhook", headers={"X-GitHub-Event": "pull_request"}, json=payload
    )
    assert response.status_code == 400
    assert "Missing PR fields" in response.json()["message"]


def test_webhook_github_comment_error(client, mock_agents):
    """Test handling of GitHub comment posting error."""
    # Configure the mock to raise an exception
    mock_agents["github_agent"].post_comment.side_effect = Exception("API error")

    payload = {
        "action": "opened",
        "pull_request": {
            "number": 123,
            "title": "Test PR",
            "body": "Test description",
            "diff_url": "https://github.com/test/diff",
            "user": {"login": "test-user"},
            "base": {"ref": "main"},
            "head": {"ref": "feature"},
        },
    }

    response = client.post(
        "/webhook", headers={"X-GitHub-Event": "pull_request"}, json=payload
    )

    assert response.status_code == 200  # Should still succeed
    response_json = response.json()
    assert response_json["status"] == "partially_processed"
    assert not response_json["comment_posted"]
    assert response_json["embedding_stored"]

    # Verify that the operations were attempted
    mock_agents["embedding_agent"].embed.assert_called()
    mock_agents["embedding_agent"].search_similar.assert_called()
    mock_agents["embedding_agent"].upsert.assert_called()
    mock_agents["llm_agent"].summarize_with_context.assert_called()
    mock_agents["github_agent"].post_comment.assert_called()


def test_webhook_embedding_error(client, mock_agents):
    """Test handling of embedding insertion error."""
    # Configure the mock to raise an exception
    mock_agents["embedding_agent"].upsert.side_effect = Exception("Qdrant error")

    payload = {
        "action": "opened",
        "pull_request": {
            "number": 123,
            "title": "Test PR",
            "body": "Test description",
            "diff_url": "https://github.com/test/diff",
            "user": {"login": "test-user"},
            "base": {"ref": "main"},
            "head": {"ref": "feature"},
        },
    }

    response = client.post(
        "/webhook", headers={"X-GitHub-Event": "pull_request"}, json=payload
    )

    assert response.status_code == 200  # Should still succeed
    response_json = response.json()
    assert response_json["status"] == "partially_processed"
    assert response_json["comment_posted"]
    assert not response_json["embedding_stored"]

    # Verify that the operations were attempted
    mock_agents["embedding_agent"].embed.assert_called()
    mock_agents["embedding_agent"].search_similar.assert_called()
    mock_agents["embedding_agent"].upsert.assert_called()
    mock_agents["llm_agent"].summarize_with_context.assert_called()
    mock_agents["github_agent"].post_comment.assert_called()


def test_webhook_json_decode_error(client):
    """Test handling of invalid JSON in request."""
    response = client.post(
        "/webhook", headers={"X-GitHub-Event": "pull_request"}, content="invalid json"
    )
    assert response.status_code == 500
    assert "error" in response.json()["status"]
