"""Custom exceptions for the GitHub agent."""


class GitHubAgentError(Exception):
    """Base exception for GitHub agent related errors."""


class EmbeddingError(GitHubAgentError):
    """Raised when there is an error generating or processing embeddings."""


class VectorStoreError(GitHubAgentError):
    """Raised when there is an error with the vector store operations."""


class ConfigurationError(GitHubAgentError):
    """Raised when there is an error in the configuration."""


class ConnectionError(GitHubAgentError):
    """Raised when there is an error connecting to external services."""


class RateLimitError(GitHubAgentError):
    """Raised when API rate limits are exceeded."""


class TimeoutError(GitHubAgentError):
    """Raised when an operation times out."""


class DataValidationError(GitHubAgentError):
    """Raised when data validation fails."""
