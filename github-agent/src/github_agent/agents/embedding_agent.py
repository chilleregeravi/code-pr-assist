import logging
import numpy as np
from openai import OpenAI
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, PointStruct, VectorParams
from github_agent.config import COLLECTION_NAME, QDRANT_URL, OPENAI_API_KEY

logger = logging.getLogger(__name__)

class EmbeddingAgent:
    def __init__(self):
        self.qdrant = QdrantClient(url=QDRANT_URL)
        self.openai = OpenAI(api_key=OPENAI_API_KEY)
        self._ensure_collection_exists()
    
    def _ensure_collection_exists(self):
        """Ensure Qdrant collection exists with correct settings."""
        if not self.qdrant.collection_exists(collection_name=COLLECTION_NAME):
            # OpenAI text-embedding-ada-002 produces 1536-dimensional vectors
            self.qdrant.recreate_collection(
                collection_name=COLLECTION_NAME,
                vectors_config=VectorParams(size=1536, distance=Distance.COSINE),
            )

    def embed(self, text: str) -> np.ndarray:
        """Create embeddings using OpenAI's text-embedding-ada-002 model."""
        try:
            response = self.openai.embeddings.create(
                model="text-embedding-ada-002",
                input=text
            )
            return np.array(response.data[0].embedding)
        except Exception as e:
            logger.error(f"OpenAI embedding failed: {e}")
            raise

    def search_similar(self, embedding: np.ndarray, k: int = 3):
        """Search for similar PRs in Qdrant using the embedding."""
        try:
            search_result = self.qdrant.search(
                collection_name=COLLECTION_NAME,
                query_vector=embedding.tolist(),
                limit=k
            )
            return [hit.payload for hit in search_result]
        except Exception as e:
            logger.error(f"Qdrant search failed: {e}")
            return []

    def upsert(self, pr_number: int, embedding: np.ndarray, full_text: str):
        """Store PR data and its embedding in Qdrant."""
        try:
            self.qdrant.upsert(
                collection_name=COLLECTION_NAME,
                points=[
                    PointStruct(
                        id=pr_number,
                        vector=embedding.tolist(),
                        payload={"text": full_text}
                    )
                ],
            )
        except Exception as e:
            logger.error(f"Failed to upsert PR to Qdrant: {e}")
            raise
