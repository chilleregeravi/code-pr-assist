from unittest.mock import MagicMock, patch

import pytest

from database_agent.vector_store import (
    ConfigurationError,
    ConnectionError,
    EmbeddingError,
    QdrantStore,
    VectorStoreError,
)


@pytest.fixture
def store():
    return QdrantStore(
        url="http://localhost:6333",
        api_key="test-key",
        collection_name="test-collection",
    )


def test_initialize_success():
    with (
        patch("database_agent.vector_store.QdrantClient") as mock_client,
        patch("database_agent.vector_store.SentenceTransformer") as mock_model,
    ):
        mock_instance = mock_client.return_value
        mock_model_instance = mock_model.return_value
        mock_model_instance.get_sentence_embedding_dimension.return_value = 3
        mock_instance.get_collections.return_value.collections = []
        store = QdrantStore(
            url="http://localhost:6333",
            api_key="test-key",
            collection_name="test-collection",
        )
        store.initialize()
        assert store.client is not None
        assert store.model is not None


def test_initialize_missing_url():
    with patch.dict("os.environ", {}, clear=True):
        with pytest.raises(ConfigurationError):
            QdrantStore(url=None)


def test_initialize_error():
    with patch(
        "database_agent.vector_store.QdrantClient", side_effect=Exception("fail")
    ):
        store = QdrantStore(
            url="http://localhost:6333",
            api_key="test-key",
            collection_name="test-collection",
        )
        with pytest.raises(ConnectionError):
            store.initialize()


def test_generate_embedding_uninitialized(store):
    store.model = None
    with pytest.raises(ConnectionError):
        store.generate_embedding("test")


def test_generate_embedding_error(store):
    store.model = MagicMock()
    store.model.encode.side_effect = Exception("fail")
    with pytest.raises(EmbeddingError):
        store.generate_embedding("test")


def test_store_pr_uninitialized(store):
    store.client = None
    store.model = None
    with pytest.raises(ConnectionError):
        store.store_pr({"id": 1, "title": "t", "body": "b"})


def test_store_pr_error(store):
    store.client = MagicMock()
    store.model = MagicMock()
    store.model.encode.side_effect = Exception("fail")
    with pytest.raises(VectorStoreError):
        store.store_pr({"id": 1, "title": "t", "body": "b"})


def test_store_prs_batch_uninitialized(store):
    store.client = None
    store.model = None
    with pytest.raises(ConnectionError):
        store.store_prs_batch([{"id": 1, "title": "t", "body": "b"}])


def test_store_prs_batch_error(store):
    store.client = MagicMock()
    store.model = MagicMock()
    store.model.encode.side_effect = Exception("fail")
    with pytest.raises(VectorStoreError):
        store.store_prs_batch([{"id": 1, "title": "t", "body": "b"}])


def test_search_similar_prs_uninitialized(store):
    store.client = None
    store.model = None
    with pytest.raises(ConnectionError):
        store.search_similar_prs("query")


def test_search_similar_prs_error(store):
    store.client = MagicMock()
    store.model = MagicMock()
    store.model.encode.return_value = [0.1, 0.2, 0.3]
    store.client.search.side_effect = Exception("fail")
    with pytest.raises(VectorStoreError):
        store.search_similar_prs("query")


def test_get_pr_uninitialized(store):
    store.client = None
    with pytest.raises(ConnectionError):
        store.get_pr(1)


def test_get_pr_error(store):
    store.client = MagicMock()
    store.client.retrieve.side_effect = Exception("fail")
    with pytest.raises(VectorStoreError):
        store.get_pr(1)


def test_delete_pr_uninitialized(store):
    store.client = None
    with pytest.raises(ConnectionError):
        store.delete_pr(1)


def test_delete_pr_error(store):
    store.client = MagicMock()
    store.client.delete.side_effect = Exception("fail")
    with pytest.raises(VectorStoreError):
        store.delete_pr(1)


def test_delete_collection_uninitialized(store):
    store.client = None
    with pytest.raises(ConnectionError):
        store.delete_collection()


def test_delete_collection_error(store):
    store.client = MagicMock()
    store.client.delete_collection.side_effect = Exception("fail")
    with pytest.raises(VectorStoreError):
        store.delete_collection()
