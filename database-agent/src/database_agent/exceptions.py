"""Custom exceptions for the database agent."""


class VectorStoreError(Exception):
    """Base exception for vector store related errors."""


class PRProcessingError(Exception):
    """Base exception for PR processing related errors."""


class ConfigurationError(VectorStoreError):
    """Raised when there is an error in the configuration."""


class ConnectionError(VectorStoreError):
    """Raised when there is an error connecting to the vector store."""


class EmbeddingError(PRProcessingError):
    """Raised when there is an error generating embeddings."""


class DataValidationError(PRProcessingError):
    """Raised when PR data validation fails."""
