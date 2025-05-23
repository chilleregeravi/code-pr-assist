import logging
import os
import sys

from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)


def get_required_env_var(name: str) -> str:
    """Get a required environment variable or exit with error."""
    value = os.getenv(name)
    if not value:
        # Don't exit during tests or when importing for inspection
        if "pytest" in sys.modules or os.getenv("TESTING"):
            return f"test-{name.lower().replace('_', '-')}"
        logger.error(f"Required environment variable '{name}' is not set")
        sys.exit(1)
    return value


def get_env_var_with_validation(
    name: str, default: str | None = None, validate_https: bool = False
) -> str:
    """Get environment variable with optional validation."""
    value = os.getenv(name, default)
    if not value:
        if default is None:
            logger.error(f"Required environment variable '{name}' is not set")
            sys.exit(1)
        return default

    # Validate HTTPS for production URLs
    if validate_https and value.startswith("http://") and "localhost" not in value:
        logger.warning(
            f"Using insecure HTTP for {name}: {value}. "
            "Consider using HTTPS in production."
        )

    return value


# Required environment variables
OPENAI_API_KEY = get_required_env_var("OPENAI_API_KEY")
GITHUB_TOKEN = get_required_env_var("GITHUB_TOKEN")

# Optional environment variables with defaults
REPO_NAME = os.getenv("REPO_NAME")
QDRANT_URL = get_env_var_with_validation(
    "QDRANT_URL", "http://localhost:6333", validate_https=True
)
COLLECTION_NAME = os.getenv("COLLECTION_NAME", "pr_cache")
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4")
LLM_PROVIDER = os.getenv("LLM_PROVIDER", "openai")  # 'openai' or 'ollama'
OLLAMA_URL = get_env_var_with_validation(
    "OLLAMA_URL", "http://localhost:11434", validate_https=True
)
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "llama2")

# Validate LLM provider
if LLM_PROVIDER not in ["openai", "ollama"]:
    if not ("pytest" in sys.modules or os.getenv("TESTING")):
        logger.error(
            f"Invalid LLM_PROVIDER '{LLM_PROVIDER}'. Must be 'openai' or 'ollama'"
        )
        sys.exit(1)

# Security-related configuration
REQUEST_TIMEOUT = int(os.getenv("REQUEST_TIMEOUT", "60"))  # seconds
MAX_RETRIES = int(os.getenv("MAX_RETRIES", "3"))
RATE_LIMIT_DELAY = float(os.getenv("RATE_LIMIT_DELAY", "1.0"))  # seconds

# Server configuration
# Default to localhost for security
SERVER_HOST = get_env_var_with_validation("SERVER_HOST", "127.0.0.1")
SERVER_PORT = int(os.getenv("SERVER_PORT", "8000"))
