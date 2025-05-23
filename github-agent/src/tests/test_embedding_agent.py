from typing import Generator
from unittest.mock import MagicMock, Mock, patch

import numpy as np
import pytest
from github_agent.agents.embedding_agent import EmbeddingAgent


@pytest.fixture(autouse=True)
def mock_openai() -> Generator[Mock, None, None]:
    """Mock OpenAI client for all tests."""
    with patch("github_agent.agents.embedding_agent.OpenAI") as mock:
        mock_client = mock.return_value
        # Setup default mock embeddings behavior
        mock_embeddings = MagicMock()
        mock_response = Mock()
        mock_response.data = [Mock(embedding=[0.1] * 1536)]
        mock_embeddings.create.return_value = mock_response
        mock_client.embeddings = mock_embeddings
        yield mock_client


@pytest.fixture(autouse=True)
def mock_qdrant() -> Generator[Mock, None, None]:
    """Mock Qdrant client for all tests."""
    with patch("github_agent.agents.embedding_agent.QdrantClient") as mock:
        mock_client = mock.return_value
        # Setup default mock behaviors
        mock_client.collection_exists.return_value = True
        yield mock_client


def test_embedding_agent_init(mock_qdrant: Mock) -> None:
    """Test EmbeddingAgent initialization."""
    agent = EmbeddingAgent()
    assert agent.qdrant is mock_qdrant
    mock_qdrant.collection_exists.assert_called_once()


def test_ensure_collection_exists(mock_qdrant: Mock) -> None:
    """Test collection creation if it doesn't exist."""
    mock_qdrant.collection_exists.return_value = False
    EmbeddingAgent()  # Initialize agent to trigger collection creation
    mock_qdrant.recreate_collection.assert_called_once()


def test_embed_text_success(mock_openai: Mock) -> None:
    """Test successful text embedding."""
    mock_embedding = [0.1] * 1536
    mock_response = Mock()
    mock_response.data = [Mock(embedding=mock_embedding)]
    mock_openai.embeddings.create.return_value = mock_response

    agent = EmbeddingAgent()
    result = agent.embed("test text")

    assert isinstance(result, np.ndarray)
    assert result.shape == (1536,)
    assert np.allclose(result, mock_embedding)
    mock_openai.embeddings.create.assert_called_once_with(
        model="text-embedding-ada-002", input="test text", timeout=60.0
    )


def test_embed_text_error(mock_openai: Mock) -> None:
    """Test embedding error handling."""
    mock_openai.embeddings.create.side_effect = Exception("API Error")

    agent = EmbeddingAgent()
    with pytest.raises(Exception):
        agent.embed("test text")


def test_search_similar_success(mock_qdrant: Mock) -> None:
    """Test successful similar PR search."""
    mock_hits = [Mock(payload={"text": "PR1"}), Mock(payload={"text": "PR2"})]

    mock_qdrant.search.return_value = mock_hits
    agent = EmbeddingAgent()
    result = agent.search_similar(np.array([0.1] * 1536))

    assert len(result) == 2
    assert result[0] is not None and result[0]["text"] == "PR1"
    assert result[1] is not None and result[1]["text"] == "PR2"


def test_search_similar_error(mock_qdrant: Mock) -> None:
    """Test search error handling."""
    mock_qdrant.search.side_effect = Exception("Search failed")
    agent = EmbeddingAgent()
    result = agent.search_similar(np.array([0.1] * 1536))
    assert result == []


def test_upsert_success(mock_qdrant: Mock) -> None:
    """Test successful PR upsert."""
    agent = EmbeddingAgent()
    embedding = np.array([0.1] * 1536)
    agent.upsert(123, embedding, "Test PR")

    mock_qdrant.upsert.assert_called_once()
    args = mock_qdrant.upsert.call_args[1]
    assert args["points"][0].id == 123
    assert args["points"][0].payload["text"] == "Test PR"


def test_upsert_error(mock_qdrant: Mock) -> None:
    """Test upsert error handling."""
    mock_qdrant.upsert.side_effect = Exception("Upsert failed")
    agent = EmbeddingAgent()
    embedding = np.array([0.1] * 1536)
    with pytest.raises(Exception):
        agent.upsert(123, embedding, "Test PR")


def test_init_qdrant_error() -> None:
    """Test Qdrant client initialization error."""
    with patch(
        "github_agent.agents.embedding_agent.QdrantClient",
        side_effect=Exception("Connection failed"),
    ):
        with pytest.raises(Exception):
            EmbeddingAgent()


def test_init_openai_error() -> None:
    """Test OpenAI client initialization error."""
    with patch(
        "github_agent.agents.embedding_agent.OpenAI",
        side_effect=Exception("API key invalid"),
    ):
        with pytest.raises(Exception):
            EmbeddingAgent()
