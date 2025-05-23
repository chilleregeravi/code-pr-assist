import logging
from opentelemetry import trace
from typing import Any, Dict, List, Optional

import numpy as np
from github_agent.config import COLLECTION_NAME, OPENAI_API_KEY, QDRANT_URL
from openai import APIError, APITimeoutError, OpenAI, OpenAIError, RateLimitError
from qdrant_client import QdrantClient
from qdrant_client.http.exceptions import ResponseHandlingException
from qdrant_client.models import Distance, PointStruct, VectorParams

logger = logging.getLogger(__name__)
tracer = trace.get_tracer(__name__)


class EmbeddingAgent:
    def __init__(self) -> None:
        """Initialize the embedding agent with OpenAI and Qdrant clients."""
        self.qdrant = QdrantClient(url=QDRANT_URL)
        self.openai = OpenAI(
            api_key=OPENAI_API_KEY,
            timeout=60.0,  # 60 second timeout
        )
        self._ensure_collection_exists()

    def _ensure_collection_exists(self) -> None:
        """Ensure Qdrant collection exists with correct settings."""
        try:
            if not self.qdrant.collection_exists(collection_name=COLLECTION_NAME):
                # OpenAI text-embedding-ada-002 produces 1536-dimensional vectors
                self.qdrant.recreate_collection(
                    collection_name=COLLECTION_NAME,
                    vectors_config=VectorParams(size=1536, distance=Distance.COSINE),
                )
                logger.info(f"Created Qdrant collection: {COLLECTION_NAME}")
        except Exception as e:
            logger.error(f"Failed to ensure Qdrant collection exists: {e}")
            raise

    def embed(self, text: str) -> np.ndarray:
        """Create embeddings using OpenAI's text-embedding-ada-002 model."""
        with tracer.start_as_current_span("EmbeddingAgent.embed") as span:
            span.set_attribute("text.length", len(text))

            try:
                response = self.openai.embeddings.create(
                    model="text-embedding-ada-002",
                    input=text,
                    timeout=60.0,  # Request-specific timeout
                )
                return np.array(response.data[0].embedding)

            except RateLimitError as e:
                logger.error(f"OpenAI embedding rate limit exceeded: {e}")
                raise

            except APITimeoutError as e:
                logger.error(f"OpenAI embedding timeout: {e}")
                raise

            except APIError as e:
                logger.error(f"OpenAI embedding API error: {e}")
                raise

            except OpenAIError as e:
                logger.error(f"OpenAI embedding SDK error: {e}")
                raise

            except Exception as e:
                logger.error(f"Unexpected error in OpenAI embedding: {e}")
                raise

    def search_similar(
        self, embedding: np.ndarray, k: int = 3
    ) -> List[Optional[Dict[str, Any]]]:
        """Search for similar PRs in Qdrant using the embedding."""
        with tracer.start_as_current_span("EmbeddingAgent.search_similar") as span:
            try:
                search_result = self.qdrant.search(
                    collection_name=COLLECTION_NAME,
                    query_vector=embedding.tolist(),
                    limit=k,
                )
                return [hit.payload for hit in search_result]

            except ResponseHandlingException as e:
                logger.error(f"Qdrant search response error: {e}")
                return []

            except Exception as e:
                logger.error(f"Qdrant search failed: {e}")
                return []

    def upsert(self, pr_number: int, embedding: np.ndarray, full_text: str) -> None:
        """Store PR data and its embedding in Qdrant."""
        with tracer.start_as_current_span("EmbeddingAgent.upsert") as span:
            span.set_attribute("pr.number", pr_number)

            try:
                self.qdrant.upsert(
                    collection_name=COLLECTION_NAME,
                    points=[
                        PointStruct(
                            id=pr_number,
                            vector=embedding.tolist(),
                            payload={"text": full_text},
                        )
                    ],
                )
                logger.debug(f"Successfully upserted PR #{pr_number} to Qdrant")

            except ResponseHandlingException as e:
                logger.error(f"Qdrant upsert response error for PR #{pr_number}: {e}")
                raise

            except Exception as e:
                logger.error(f"Failed to upsert PR #{pr_number} to Qdrant: {e}")
                raise
