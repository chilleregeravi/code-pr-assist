"""Tests for the vector store."""

from unittest.mock import MagicMock, patch

import numpy as np
import pytest
from database_agent.vector_store import QdrantStore


@pytest.fixture
def mock_qdrant_client():
    """Create a mock Qdrant client."""
    with patch("database_agent.vector_store.QdrantClient") as mock:
        client = mock.return_value
        client.upsert.return_value = True
        client.search.return_value = [
            MagicMock(id=1, score=0.9, payload={"title": "Test PR"}),
            MagicMock(id=2, score=0.8, payload={"title": "Another PR"}),
        ]
        client.delete.return_value = True
        client.delete_collection.return_value = True
        yield client


@pytest.fixture
def mock_sentence_transformer():
    """Create a mock sentence transformer."""
    with patch("database_agent.vector_store.SentenceTransformer") as mock:
        model = mock.return_value
        model.encode.return_value = np.array([0.1, 0.2, 0.3])
        yield model


@pytest.fixture
def vector_store(mock_qdrant_client, mock_sentence_transformer):
    """Create a VectorStore instance with mocked dependencies."""
    store = QdrantStore(
        url="http://localhost:6333",
        api_key="test-key",
        collection_name="test-collection",
    )
    store.client = mock_qdrant_client
    store.model = mock_sentence_transformer
    return store


def test_vector_store_initialization(vector_store):
    """Test vector store initialization."""
    assert vector_store is not None
    assert vector_store.collection_name == "test-collection"


def test_generate_embedding(vector_store, mock_sentence_transformer):
    """Test generating embeddings."""
    embedding = vector_store.generate_embedding("Test text")
    assert isinstance(embedding, list)
    assert len(embedding) == 3
    mock_sentence_transformer.encode.assert_called_once_with("Test text")


def test_store_pr(vector_store, mock_qdrant_client):
    """Test storing a PR."""
    pr_data = {"id": 1, "title": "Test PR", "body": "Test body", "labels": ["test"]}
    result = vector_store.store_pr(pr_data)
    assert result is True
    mock_qdrant_client.upsert.assert_called_once()


def test_store_prs_batch(vector_store, mock_qdrant_client):
    """Test storing multiple PRs in batch."""
    prs_data = [
        {"id": 1, "title": "PR 1", "body": "Body 1"},
        {"id": 2, "title": "PR 2", "body": "Body 2"},
    ]
    result = vector_store.store_prs_batch(prs_data)
    assert result is True
    mock_qdrant_client.upsert.assert_called_once()


def test_search_similar_prs(vector_store, mock_qdrant_client):
    """Test searching for similar PRs."""
    results = vector_store.search_similar_prs("test query", limit=2)
    assert len(results) == 2
    assert results[0]["id"] == 1
    assert results[0]["score"] == 0.9
    assert results[1]["id"] == 2
    assert results[1]["score"] == 0.8


def test_get_pr(vector_store, mock_qdrant_client):
    """Test getting a PR by ID."""
    mock_qdrant_client.retrieve.return_value = [
        MagicMock(id=1, payload={"title": "Test PR"})
    ]
    pr = vector_store.get_pr(1)
    assert pr is not None
    assert pr["id"] == 1
    assert pr["title"] == "Test PR"


def test_delete_pr(vector_store, mock_qdrant_client):
    """Test deleting a PR."""
    result = vector_store.delete_pr(1)
    assert result is True
    mock_qdrant_client.delete.assert_called_once()


def test_delete_collection(vector_store, mock_qdrant_client):
    """Test deleting a collection."""
    result = vector_store.delete_collection()
    assert result is True
    mock_qdrant_client.delete_collection.assert_called_once_with(
        collection_name="test-collection"
    )
