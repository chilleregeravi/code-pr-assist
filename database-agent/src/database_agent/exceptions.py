"""Custom exceptions for the database agent."""

class VectorStoreError(Exception):
    """Base exception for vector store related errors."""
    pass

class PRProcessingError(Exception):
    """Base exception for PR processing related errors."""
    pass

class ConfigurationError(VectorStoreError):
    """Raised when there is an error in the configuration."""
    pass

class ConnectionError(VectorStoreError):
    """Raised when there is an error connecting to the vector store."""
    pass

class EmbeddingError(PRProcessingError):
    """Raised when there is an error generating embeddings."""
    pass

class DataValidationError(PRProcessingError):
    """Raised when PR data validation fails."""
    pass 