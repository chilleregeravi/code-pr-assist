import pytest
import numpy as np
import openai
from unittest.mock import Mock, patch
from github_agent.agents.embedding_agent import EmbeddingAgent
from qdrant_client.models import ScoredPoint

def test_embedding_agent_init():
    """Test EmbeddingAgent initialization."""
    with patch('github_agent.agents.embedding_agent.QdrantClient') as mock_qdrant:
        agent = EmbeddingAgent()
        assert agent.qdrant is mock_qdrant.return_value
        mock_qdrant.return_value.collection_exists.assert_called_once()

def test_ensure_collection_exists():
    """Test collection creation if it doesn't exist."""
    with patch('github_agent.agents.embedding_agent.QdrantClient') as mock_qdrant:
        mock_qdrant.return_value.collection_exists.return_value = False
        agent = EmbeddingAgent()
        mock_qdrant.return_value.recreate_collection.assert_called_once()

def test_embed_text_success():
    """Test successful text embedding."""
    mock_embedding = [0.1] * 1536
    mock_response = {
        'data': [{
            'embedding': mock_embedding
        }]
    }
    
    with patch('openai.Embedding.create', return_value=mock_response) as mock_create:
        agent = EmbeddingAgent()
        result = agent.embed("test text")
        
        assert isinstance(result, np.ndarray)
        assert result.shape == (1536,)
        assert np.allclose(result, mock_embedding)
        mock_create.assert_called_once_with(
            model="text-embedding-ada-002",
            input="test text"
        )

def test_embed_text_error():
    """Test embedding error handling."""
    with patch('openai.Embedding.create', side_effect=Exception("API Error")):
        agent = EmbeddingAgent()
        with pytest.raises(Exception):
            agent.embed("test text")

def test_search_similar_success():
    """Test successful similar PR search."""
    mock_hits = [
        Mock(payload={"text": "PR1"}),
        Mock(payload={"text": "PR2"})
    ]
    
    with patch('github_agent.agents.embedding_agent.QdrantClient') as mock_qdrant:
        mock_qdrant.return_value.search.return_value = mock_hits
        agent = EmbeddingAgent()
        result = agent.search_similar(np.array([0.1] * 1536))
        
        assert len(result) == 2
        assert result[0]["text"] == "PR1"
        assert result[1]["text"] == "PR2"

def test_search_similar_error():
    """Test search error handling."""
    with patch('github_agent.agents.embedding_agent.QdrantClient') as mock_qdrant:
        mock_qdrant.return_value.search.side_effect = Exception("Search failed")
        agent = EmbeddingAgent()
        result = agent.search_similar(np.array([0.1] * 1536))
        assert result == []

def test_upsert_success():
    """Test successful PR upsert."""
    with patch('github_agent.agents.embedding_agent.QdrantClient') as mock_qdrant:
        agent = EmbeddingAgent()
        embedding = np.array([0.1] * 1536)
        agent.upsert(123, embedding, "Test PR")
        
        mock_qdrant.return_value.upsert.assert_called_once()
        args = mock_qdrant.return_value.upsert.call_args[1]
        assert args["points"][0].id == 123
        assert args["points"][0].payload["text"] == "Test PR"

def test_upsert_error():
    """Test upsert error handling."""
    with patch('github_agent.agents.embedding_agent.QdrantClient') as mock_qdrant:
        mock_qdrant.return_value.upsert.side_effect = Exception("Upsert failed")
        agent = EmbeddingAgent()
        with pytest.raises(Exception):
            agent.upsert(123, np.array([0.1] * 1536), "Test PR")
