import logging
from typing import Any

import numpy as np
from openai import APIError, APITimeoutError, OpenAI, OpenAIError, RateLimitError
from opentelemetry import trace
from qdrant_client import QdrantClient
from qdrant_client.http.exceptions import ResponseHandlingException
from qdrant_client.models import Distance, PointStruct, VectorParams

from github_agent.config import COLLECTION_NAME, OPENAI_API_KEY, QDRANT_URL
from github_agent.exceptions import (
    ConnectionError,
    EmbeddingError,
)
from github_agent.exceptions import RateLimitError as AgentRateLimitError
from github_agent.exceptions import (
    TimeoutError,
    VectorStoreError,
)

logger = logging.getLogger(__name__)
tracer = trace.get_tracer(__name__)


class EmbeddingAgent:
    def __init__(self) -> None:
        """Initialize the embedding agent with OpenAI and Qdrant clients."""
        try:
            self.qdrant = QdrantClient(url=QDRANT_URL)
            self.openai = OpenAI(
                api_key=OPENAI_API_KEY,
                timeout=60.0,  # 60 second timeout
            )
            self._ensure_collection_exists()
        except Exception as e:
            logger.error(f"Failed to initialize EmbeddingAgent: {e}")
            raise ConnectionError(f"Failed to initialize EmbeddingAgent: {e}") from e

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
            raise VectorStoreError(
                f"Failed to ensure Qdrant collection exists: {e}"
            ) from e

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
                raise AgentRateLimitError(
                    f"OpenAI embedding rate limit exceeded: {e}"
                ) from e

            except APITimeoutError as e:
                logger.error(f"OpenAI embedding timeout: {e}")
                raise TimeoutError(f"OpenAI embedding timeout: {e}") from e

            except APIError as e:
                logger.error(f"OpenAI embedding API error: {e}")
                raise EmbeddingError(f"OpenAI embedding API error: {e}") from e

            except OpenAIError as e:
                logger.error(f"OpenAI embedding SDK error: {e}")
                raise EmbeddingError(f"OpenAI embedding SDK error: {e}") from e

            except Exception as e:
                logger.error(f"Unexpected error in OpenAI embedding: {e}")
                raise EmbeddingError(
                    f"Unexpected error in OpenAI embedding: {e}"
                ) from e

    def search_similar(
        self, embedding: np.ndarray, k: int = 3
    ) -> list[dict[str, Any] | None]:
        """Search for similar PRs in Qdrant using the embedding."""
        with tracer.start_as_current_span("EmbeddingAgent.search_similar") as span:
            span.set_attribute("limit", k)
            try:
                search_result = self.qdrant.search(
                    collection_name=COLLECTION_NAME,
                    query_vector=embedding.tolist(),
                    limit=k,
                )
                return [hit.payload for hit in search_result]

            except ResponseHandlingException as e:
                logger.error(f"Qdrant search response error: {e}")
                raise VectorStoreError(f"Qdrant search response error: {e}") from e

            except Exception as e:
                logger.error(f"Qdrant search failed: {e}")
                raise VectorStoreError(f"Qdrant search failed: {e}") from e

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
                raise VectorStoreError(
                    f"Qdrant upsert response error for PR #{pr_number}: {e}"
                ) from e

            except Exception as e:
                logger.error(f"Failed to upsert PR #{pr_number} to Qdrant: {e}")
                raise VectorStoreError(
                    f"Failed to upsert PR #{pr_number} to Qdrant: {e}"
                ) from e
