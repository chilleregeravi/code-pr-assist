"""Tests for the FastAPI application."""
import json
from unittest.mock import Mock, patch
import pytest
from fastapi.testclient import TestClient

# Mock OpenAI before importing app
with patch('github_agent.agents.embedding_agent.OpenAI'):
    from github_agent.main import app

@pytest.fixture
def client():
    """Create a test client."""
    return TestClient(app)

@pytest.fixture
def mock_agents():
    """Mock all agents used in the application."""
    with patch('github_agent.main.GitHubAgent') as mock_github, \
         patch('github_agent.main.LLMAgent') as mock_llm, \
         patch('github_agent.main.EmbeddingAgent') as mock_embedding:
        
        # Set up mock returns
        mock_llm.return_value.summarize_with_context.return_value = "Test summary"
        mock_embedding.return_value.embed.return_value = [0.1] * 1536
        mock_embedding.return_value.search_similar.return_value = [
            {"text": "Similar PR 1"},
            {"text": "Similar PR 2"}
        ]
        
        yield {
            'github': mock_github,
            'llm': mock_llm,
            'embedding': mock_embedding
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
            "user": {"login": "test-user"},
            "base": {"ref": "main"},
            "head": {"ref": "feature"}
        }
    }
    
    response = client.post(
        "/webhook",
        headers={"X-GitHub-Event": "pull_request"},
        json=payload
    )
    
    assert response.status_code == 200
    mock_agents['llm'].return_value.summarize_with_context.assert_called_once()
    mock_agents['embedding'].return_value.embed.assert_called_once()
    mock_agents['github'].return_value.post_comment.assert_called_once()

def test_webhook_invalid_event(client):
    """Test webhook handling for invalid event."""
    response = client.post(
        "/webhook",
        headers={"X-GitHub-Event": "invalid"},
        json={}
    )
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
        json={"action": "opened"}  # Missing required fields
    )
    assert response.status_code == 422  # Validation error
