from collections.abc import Generator
from unittest.mock import Mock, patch

import pytest

from github_agent.agents.llm_agent import LLMAgent


@pytest.fixture(autouse=True)
def mock_openai_client() -> Generator[Mock, None, None]:
    """Mock OpenAI client for all tests."""
    with patch("github_agent.agents.llm_agent.OpenAI") as mock_openai:
        mock_client = Mock()
        mock_openai.return_value = mock_client

        # Setup default mock chat completion behavior
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = (
            "Test summary with labels: bug, enhancement"
        )
        mock_client.chat.completions.create.return_value = mock_response

        yield mock_client


def test_llm_agent_init(mock_openai_client: Mock) -> None:
    """Test LLMAgent initialization."""
    agent = LLMAgent()
    assert agent.client is mock_openai_client


def test_summarize_with_context_success(mock_openai_client: Mock) -> None:
    """Test successful PR summarization with context."""
    # Setup mock response
    mock_response = Mock()
    mock_response.choices = [Mock()]
    mock_response.choices[0].message.content = (
        "Test summary with labels: bug, enhancement"
    )
    mock_openai_client.chat.completions.create.return_value = mock_response

    agent = LLMAgent()
    result = agent.summarize_with_context(
        "Fix memory leak in data processor",
        ["Previous PR: Fixed similar issue", "Another PR: Memory optimization"],
    )

    assert result == "Test summary with labels: bug, enhancement"
    mock_openai_client.chat.completions.create.assert_called_once()

    # Verify the call arguments
    call_args = mock_openai_client.chat.completions.create.call_args
    assert call_args[1]["model"] == "gpt-4"  # From config - corrected expectation
    assert len(call_args[1]["messages"]) == 2
    assert call_args[1]["timeout"] == 60.0


def test_summarize_with_context_empty_response(mock_openai_client: Mock) -> None:
    """Test handling of empty response from OpenAI."""
    mock_response = Mock()
    mock_response.choices = [Mock()]
    mock_response.choices[0].message.content = None
    mock_openai_client.chat.completions.create.return_value = mock_response

    agent = LLMAgent()
    result = agent.summarize_with_context("Test PR", [])

    assert result == "[Error: Empty response from LLM.]"


def test_summarize_rate_limit_error(mock_openai_client: Mock) -> None:
    """Test handling of rate limit errors."""
    from openai import RateLimitError

    mock_openai_client.chat.completions.create.side_effect = RateLimitError(
        message="Rate limit exceeded", response=Mock(), body={}
    )

    agent = LLMAgent()
    result = agent.summarize_with_context("Test PR", [])

    assert result == "[Error: Rate limit exceeded. Please try again later.]"


def test_summarize_timeout_error(mock_openai_client: Mock) -> None:
    """Test handling of timeout errors."""
    from openai import APITimeoutError

    mock_openai_client.chat.completions.create.side_effect = APITimeoutError(
        request=Mock()
    )

    agent = LLMAgent()
    result = agent.summarize_with_context("Test PR", [])

    assert result == "[Error: Request timed out. Please try again.]"


def test_summarize_api_error(mock_openai_client: Mock) -> None:
    """Test handling of API errors."""
    from openai import APIError

    mock_openai_client.chat.completions.create.side_effect = APIError(
        message="API Error", request=Mock(), body={}
    )

    agent = LLMAgent()
    result = agent.summarize_with_context("Test PR", [])

    assert result == "[Error: API error occurred.]"


def test_summarize_generic_error(mock_openai_client: Mock) -> None:
    """Test handling of generic errors."""
    mock_openai_client.chat.completions.create.side_effect = Exception("Network error")

    agent = LLMAgent()
    result = agent.summarize_with_context("Test PR", [])

    assert result == "[Error: Could not generate summary.]"
