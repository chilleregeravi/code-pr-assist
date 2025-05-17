import logging

import numpy as np
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, PointStruct, VectorParams
from sentence_transformers import SentenceTransformer

from .config import COLLECTION_NAME, QDRANT_URL

logger = logging.getLogger(__name__)


def get_model():
    return SentenceTransformer("all-MiniLM-L6-v2")


def get_qdrant():
    return QdrantClient(url=QDRANT_URL)


def ensure_collection_exists(qdrant):
    if not qdrant.collection_exists(collection_name=COLLECTION_NAME):
        qdrant.recreate_collection(
            collection_name=COLLECTION_NAME,
            vectors_config=VectorParams(size=384, distance=Distance.COSINE),
        )


def embed_text(text: str) -> np.ndarray:
    """Embed text using the sentence transformer model."""
    try:
        model = get_model()
        return model.encode([text])[0]
    except Exception as e:
        logger.error(f"Embedding failed: {e}")
        raise


def search_similar_prs(embedding: np.ndarray, k=3):
    """Search for similar PRs in Qdrant using the embedding."""
    try:
        qdrant = get_qdrant()
        ensure_collection_exists(qdrant)
        search_result = qdrant.search(
            collection_name=COLLECTION_NAME, query_vector=embedding.tolist(), limit=k
        )
        return [hit.payload for hit in search_result]
    except Exception as e:
        logger.error(f"Qdrant search failed: {e}")
        return []


def upsert_pr(pr_number: int, embedding: np.ndarray, full_text: str):
    try:
        qdrant = get_qdrant()
        ensure_collection_exists(qdrant)
        qdrant.upsert(
            collection_name=COLLECTION_NAME,
            points=[
                PointStruct(
                    id=pr_number, vector=embedding.tolist(), payload={"text": full_text}
                )
            ],
        )
    except Exception as e:
        logger.error(f"Failed to upsert PR to Qdrant: {e}")
