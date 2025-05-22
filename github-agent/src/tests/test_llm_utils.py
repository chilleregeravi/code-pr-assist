from unittest.mock import patch

import pytest
from github_agent.llm_utils import gpt_summarize_with_context
from typing import Any, Generator
from unittest.mock import Mock, MagicMock


@pytest.fixture
def mock_openai_client() -> Generator[Mock, None, None]:
    """Mock OpenAI client for tests that need it."""
    with patch('github_agent.llm_utils.OpenAI') as mock_openai:
        mock_client = Mock()
        mock_openai.return_value = mock_client
        yield mock_client


@patch.dict('os.environ', {'OPENAI_API_KEY': 'test-key'})
@patch('github_agent.llm_utils.LLM_PROVIDER', 'openai')
def test_gpt_summarize_with_context_openai_success(mock_openai_client: Mock) -> None:
    """Test successful OpenAI summarization with context."""
    # Setup mock response
    mock_response = Mock()
    mock_response.choices = [Mock()]
    mock_response.choices[0].message.content = "Test summary with labels: bug, enhancement"
    mock_openai_client.chat.completions.create.return_value = mock_response
    
    result = gpt_summarize_with_context(
        "Fix memory leak in data processor",
        ["Previous PR: Fixed similar issue", "Another PR: Memory optimization"]
    )
    
    assert result == "Test summary with labels: bug, enhancement"
    mock_openai_client.chat.completions.create.assert_called_once()
    
    # Verify the call arguments
    call_args = mock_openai_client.chat.completions.create.call_args
    assert call_args[1]["model"] == "gpt-4"  # From config - corrected expectation
    assert len(call_args[1]["messages"]) == 2
    assert call_args[1]["timeout"] == 60.0


@patch.dict('os.environ', {'OPENAI_API_KEY': 'test-key'})
@patch('github_agent.llm_utils.LLM_PROVIDER', 'openai')
def test_gpt_summarize_with_context_openai_empty_response(mock_openai_client: Mock) -> None:
    """Test handling of empty response from OpenAI."""
    mock_response = Mock()
    mock_response.choices = [Mock()]
    mock_response.choices[0].message.content = ""
    mock_openai_client.chat.completions.create.return_value = mock_response
    
    result = gpt_summarize_with_context("Test PR", [])
    
    assert result == "[Error: Empty response from LLM.]"


@patch.dict('os.environ', {'OPENAI_API_KEY': 'test-key'})
@patch('github_agent.llm_utils.LLM_PROVIDER', 'openai')
def test_gpt_summarize_with_context_openai_rate_limit_error(mock_openai_client: Mock) -> None:
    """Test handling of rate limit errors."""
    from openai import RateLimitError
    mock_openai_client.chat.completions.create.side_effect = RateLimitError(
        message="Rate limit exceeded",
        response=Mock(),
        body={}
    )
    
    result = gpt_summarize_with_context("Test PR", [])
    
    assert result == "[Error: Rate limit exceeded. Please try again later.]"


@patch.dict('os.environ', {'OPENAI_API_KEY': 'test-key'})
@patch('github_agent.llm_utils.LLM_PROVIDER', 'openai')
def test_gpt_summarize_with_context_openai_timeout_error(mock_openai_client: Mock) -> None:
    """Test handling of timeout errors."""
    from openai import APITimeoutError
    mock_openai_client.chat.completions.create.side_effect = APITimeoutError(request=Mock())
    
    result = gpt_summarize_with_context("Test PR", [])
    
    assert result == "[Error: Request timed out. Please try again.]"


@patch.dict('os.environ', {'OPENAI_API_KEY': 'test-key'})
@patch('github_agent.llm_utils.LLM_PROVIDER', 'openai')
def test_gpt_summarize_with_context_openai_error(mock_openai_client: Mock) -> None:
    """Test handling of generic OpenAI errors."""
    mock_openai_client.chat.completions.create.side_effect = Exception("Network error")
    
    result = gpt_summarize_with_context("Test PR", [])
    
    assert result == "[Error: Could not generate summary.]"


@patch('github_agent.llm_utils.LLM_PROVIDER', 'ollama')
@patch('github_agent.llm_utils.requests.post')
def test_gpt_summarize_with_context_ollama_success(mock_post: Mock) -> None:
    """Test successful Ollama summarization."""
    # Setup mock response
    mock_response = Mock()
    mock_response.json.return_value = {
        "choices": [{"message": {"content": "Ollama summary"}}]
    }
    mock_response.raise_for_status.return_value = None
    mock_post.return_value = mock_response
    
    result = gpt_summarize_with_context("Test PR", ["context"])
    
    assert result == "Ollama summary"
    mock_post.assert_called_once()


@patch('github_agent.llm_utils.LLM_PROVIDER', 'ollama')
@patch('github_agent.llm_utils.requests.post')
def test_gpt_summarize_with_context_ollama_timeout(mock_post: Mock) -> None:
    """Test handling of Ollama timeout errors."""
    import requests
    mock_post.side_effect = requests.exceptions.Timeout("Request timeout")
    
    result = gpt_summarize_with_context("Test PR", [])
    
    assert result == "[Error: Request timed out. Please try again.]"


@patch('github_agent.llm_utils.LLM_PROVIDER', 'unknown')
def test_gpt_summarize_with_context_unknown_provider() -> None:
    """Test handling of unknown LLM provider."""
    result = gpt_summarize_with_context("Test PR", [])
    
    assert result == "[Error: Unknown LLM provider configured.]"


@patch.dict('os.environ', {'OPENAI_API_KEY': 'test-key'})
@patch('github_agent.llm_utils.LLM_PROVIDER', 'openai')
def test_gpt_summarize_with_context_long_text_truncation(mock_openai_client: Mock) -> None:
    """Test that long PR text gets truncated."""
    # Setup mock response
    mock_response = Mock()
    mock_response.choices = [Mock()]
    mock_response.choices[0].message.content = "Truncated summary"
    mock_openai_client.chat.completions.create.return_value = mock_response
    
    # Create a very long PR text
    long_text = "x" * 8000  # Longer than 7000 chars
    
    result = gpt_summarize_with_context(long_text, [])
    
    assert result == "Truncated summary"
    
    # Verify the call was made with truncated text
    call_args = mock_openai_client.chat.completions.create.call_args
    sent_content = call_args[1]["messages"][1]["content"]
    assert "... (truncated)" in sent_content
