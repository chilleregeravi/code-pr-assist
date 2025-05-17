import os
os.environ['QDRANT_URL'] = 'http://localhost:6333'
os.environ['COLLECTION_NAME'] = 'test_collection'

import pytest
from unittest.mock import patch, MagicMock
import numpy as np

patcher_qdrant = patch("agent.qdrant_utils.QdrantClient")
patcher_model = patch("agent.qdrant_utils.SentenceTransformer")
MockQdrantClient = patcher_qdrant.start()
MockSentenceTransformer = patcher_model.start()
mock_qdrant = MockQdrantClient.return_value
mock_qdrant.collection_exists.return_value = True
mock_model = MockSentenceTransformer.return_value
mock_model.encode.return_value = np.array([[1,2,3]])

from agent.qdrant_utils import embed_text, search_similar_prs, upsert_pr, ensure_collection_exists, get_model, get_qdrant

def teardown_module(module):
    patcher_qdrant.stop()
    patcher_model.stop()

def test_embed_text_success():
    result = embed_text("text")
    assert (result == np.array([1,2,3])).all()

def test_embed_text_error():
    with patch("agent.qdrant_utils.get_model", return_value=mock_model):
        mock_model.encode.side_effect = Exception("fail")
        with pytest.raises(Exception):
            embed_text("text")
        mock_model.encode.side_effect = None  # Reset for other tests

def test_search_similar_prs_success():
    with patch("agent.qdrant_utils.get_qdrant", return_value=mock_qdrant):
        mock_qdrant.search.return_value = [type("obj", (), {"payload": {"text": "foo"}})]
        result = search_similar_prs(np.array([1,2,3]))
        assert result == [{"text": "foo"}]

def test_search_similar_prs_error():
    with patch("agent.qdrant_utils.get_qdrant", return_value=mock_qdrant):
        mock_qdrant.search.side_effect = Exception("fail")
        result = search_similar_prs(np.array([1,2,3]))
        assert result == []
        mock_qdrant.search.side_effect = None  # Reset for other tests

def test_upsert_pr_success():
    with patch("agent.qdrant_utils.get_qdrant", return_value=mock_qdrant):
        upsert_pr(1, np.array([1,2,3]), "text")
        mock_qdrant.upsert.assert_called()

def test_upsert_pr_error():
    with patch("agent.qdrant_utils.get_qdrant", return_value=mock_qdrant):
        mock_qdrant.upsert.side_effect = Exception("fail")
        upsert_pr(1, np.array([1,2,3]), "text")  # Should log error but not raise
        mock_qdrant.upsert.side_effect = None  # Reset for other tests

def test_ensure_collection_exists_recreate():
    mock_qdrant2 = MagicMock()
    mock_qdrant2.collection_exists.return_value = False
    ensure_collection_exists(mock_qdrant2)
    mock_qdrant2.recreate_collection.assert_called()

def test_get_model_error():
    with patch("agent.qdrant_utils.SentenceTransformer", side_effect=Exception("fail")):
        with pytest.raises(Exception):
            get_model()

def test_get_qdrant_error():
    with patch("agent.qdrant_utils.QdrantClient", side_effect=Exception("fail")):
        with pytest.raises(Exception):
            get_qdrant()