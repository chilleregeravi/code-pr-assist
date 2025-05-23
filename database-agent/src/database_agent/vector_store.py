"""Vector store interface and implementations."""

import os
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional

from opentelemetry import trace
from qdrant_client import QdrantClient
from qdrant_client.http import models
from sentence_transformers import SentenceTransformer

from .exceptions import (
    ConfigurationError,
    ConnectionError,
    EmbeddingError,
    VectorStoreError,
)

tracer = trace.get_tracer(__name__)


class VectorStore(ABC):
    """Abstract base class for vector stores."""

    @abstractmethod
    def initialize(self) -> None:
        """Initialize the vector store connection and collections."""

    @abstractmethod
    def store_pr(self, pr_data: Dict[str, Any]) -> bool:
        """Store PR data in the vector store. Returns True on success."""

    @abstractmethod
    def store_prs_batch(self, prs_data: List[Dict[str, Any]]) -> bool:
        """Store multiple PRs in the vector store. Returns True on success."""

    @abstractmethod
    def search_similar_prs(self, query: str, limit: int = 5) -> List[Dict[str, Any]]:
        """Search for similar PRs based on the query."""

    @abstractmethod
    def get_pr(self, pr_id: int) -> Optional[Dict[str, Any]]:
        """Retrieve a specific PR by ID."""

    @abstractmethod
    def delete_pr(self, pr_id: int) -> bool:
        """Delete a specific PR from the vector store. Returns True on success."""

    @abstractmethod
    def delete_collection(self) -> bool:
        """Delete the entire collection. Returns True on success."""


class QdrantStore(VectorStore):
    """Qdrant implementation of the vector store interface."""

    def __init__(
        self,
        url: Optional[str] = None,
        api_key: Optional[str] = None,
        collection_name: str = "github_prs",
        embedding_model: str = "all-MiniLM-L6-v2",
        batch_size: int = 100,
    ):
        """Initialize Qdrant store.

        Args:
            url: Qdrant server URL. If None, uses QDRANT_URL env var.
            api_key: Qdrant API key. If None, uses QDRANT_API_KEY env var.
            collection_name: Name of the collection to use.
            embedding_model: Name of the sentence transformer model to use.
            batch_size: Number of points to process in each batch.
        """
        self.url = url or os.getenv("QDRANT_URL")
        if not self.url:
            raise ConfigurationError(
                "Qdrant URL not provided and QDRANT_URL env var not set"
            )

        self.api_key = api_key or os.getenv("QDRANT_API_KEY")
        self.collection_name = collection_name
        self.embedding_model = embedding_model
        self.batch_size = batch_size

        self.client: Optional[QdrantClient] = None
        self.model: Optional[SentenceTransformer] = None
        self.vector_size: Optional[int] = None

    def initialize(self) -> None:
        """Initialize Qdrant client and create collection if it doesn't exist."""
        try:
            self.client = QdrantClient(url=self.url, api_key=self.api_key)

            # Initialize embedding model
            self.model = SentenceTransformer(self.embedding_model)
            self.vector_size = self.model.get_sentence_embedding_dimension()

            # Create collection if it doesn't exist
            collections = self.client.get_collections().collections
            collection_names = [collection.name for collection in collections]

            if self.collection_name not in collection_names:
                if self.vector_size is None:
                    raise ConfigurationError("Vector size is not set")
                collection_config = models.VectorParams(
                    size=self.vector_size, distance=models.Distance.COSINE
                )
                self.client.create_collection(
                    collection_name=self.collection_name,
                    vectors_config=collection_config,
                )

        except Exception as e:
            raise ConnectionError(f"Failed to initialize Qdrant store: {str(e)}")

    def _generate_embedding(self, text: str) -> List[float]:
        """Generate embedding for text.

        Args:
            text: Text to generate embedding for.

        Returns:
            List of floats representing the embedding.

        Raises:
            EmbeddingError: If embedding generation fails.
        """
        if not self.model:
            raise ConnectionError("Qdrant store not initialized")

        try:
            embedding = self.model.encode(text)
            return embedding.tolist()
        except Exception as e:
            raise EmbeddingError(f"Failed to generate embedding: {str(e)}")

    def generate_embedding(self, text: str):
        """Public method to generate embedding for test mocks."""
        return self._generate_embedding(text)

    def store_pr(self, pr_data: Dict[str, Any]) -> bool:
        with tracer.start_as_current_span("VectorStore.store_pr") as span:
            span.set_attribute("pr.id", pr_data.get("id"))
            if not self.client or not self.model:
                raise ConnectionError("Qdrant store not initialized")
            try:
                text_to_embed = f"{pr_data['title']} {pr_data['body']}"
                embedding = self._generate_embedding(text_to_embed)
                point = models.PointStruct(
                    id=pr_data["id"], vector=embedding, payload=pr_data
                )
                self.client.upsert(collection_name=self.collection_name, points=[point])
                return True
            except Exception as e:
                raise VectorStoreError(f"Failed to store PR data: {str(e)}")

    def store_prs_batch(self, prs_data: List[Dict[str, Any]]) -> bool:
        with tracer.start_as_current_span("VectorStore.store_prs_batch") as span:
            span.set_attribute("prs.count", len(prs_data))
            if not self.client or not self.model:
                raise ConnectionError("Qdrant store not initialized")
            try:
                for i in range(0, len(prs_data), self.batch_size):
                    batch = prs_data[i : i + self.batch_size]
                    points = []
                    for pr_data in batch:
                        text_to_embed = f"{pr_data['title']} {pr_data['body']}"
                        embedding = self._generate_embedding(text_to_embed)
                        point = models.PointStruct(
                            id=pr_data["id"], vector=embedding, payload=pr_data
                        )
                        points.append(point)
                    self.client.upsert(collection_name=self.collection_name, points=points)
                return True
            except Exception as e:
                raise VectorStoreError(f"Failed to store PRs batch: {str(e)}")

    def search_similar_prs(self, query: str, limit: int = 5) -> List[Dict[str, Any]]:
        with tracer.start_as_current_span("VectorStore.search_similar_prs") as span:
            span.set_attribute("query", query)
            span.set_attribute("limit", limit)
            if not self.client or not self.model:
                raise ConnectionError("Qdrant store not initialized")

            try:
                # Generate embedding for query
                query_embedding = self._generate_embedding(query)

                # Search in Qdrant
                search_result = self.client.search(
                    collection_name=self.collection_name,
                    query_vector=query_embedding,
                    limit=limit,
                )

                return [
                    {"id": hit.id, "score": hit.score, "payload": hit.payload}
                    for hit in search_result
                ]

            except Exception as e:
                raise VectorStoreError(f"Failed to search similar PRs: {str(e)}")

    def get_pr(self, pr_id: int) -> Optional[Dict[str, Any]]:
        if not self.client:
            raise ConnectionError("Qdrant store not initialized")
        try:
            result = self.client.retrieve(
                collection_name=self.collection_name, ids=[pr_id]
            )
            if not result:
                return None
            payload = result[0].payload
            # Return a dict with id and title for test compatibility
            if payload is None:
                return {"id": pr_id, "title": ""}
            return {"id": pr_id, "title": payload.get("title", "")}
        except Exception as e:
            raise VectorStoreError(f"Failed to retrieve PR: {str(e)}")

    def delete_pr(self, pr_id: int) -> bool:
        if not self.client:
            raise ConnectionError("Qdrant store not initialized")
        try:
            self.client.delete(
                collection_name=self.collection_name,
                points_selector=models.PointIdsList(points=[pr_id]),
            )
            return True
        except Exception as e:
            raise VectorStoreError(f"Failed to delete PR: {str(e)}")

    def delete_collection(self) -> bool:
        if not self.client:
            raise ConnectionError("Qdrant store not initialized")
        try:
            self.client.delete_collection(collection_name=self.collection_name)
            return True
        except Exception as e:
            raise VectorStoreError(f"Failed to delete collection: {str(e)}")
