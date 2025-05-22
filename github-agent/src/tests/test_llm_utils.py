from unittest.mock import patch

import pytest
from github_agent.llm_utils import gpt_summarize_with_context


@pytest.mark.parametrize(
    "provider,expected", [("openai", "OpenAI summary"), ("ollama", "Ollama summary")]
)
def test_gpt_summarize_with_context(monkeypatch, provider, expected):
    monkeypatch.setenv("OPENAI_API_KEY", "test_key")
    pr_text = "Test PR"
    similar_contexts = ["Context1", "Context2"]
    if provider == "openai":
        with patch("github_agent.llm_utils.LLM_PROVIDER", "openai"), patch(
            "openai.chat.completions.create"
        ) as mock_create:
            mock_create.return_value.choices = [
                type("obj", (), {"message": type("obj", (), {"content": expected})})
            ]
            result = gpt_summarize_with_context(pr_text, similar_contexts)
            assert result == expected
    else:
        with patch("github_agent.llm_utils.LLM_PROVIDER", "ollama"), patch(
            "requests.post"
        ) as mock_post:
            mock_post.return_value.json.return_value = {
                "choices": [{"message": {"content": expected}}]
            }
            mock_post.return_value.raise_for_status = lambda: None
            result = gpt_summarize_with_context(pr_text, similar_contexts)
            assert result == expected


def test_gpt_summarize_with_context_openai_error():
    with patch.dict("os.environ", {"OPENAI_API_KEY": "test_key"}), \
         patch("github_agent.llm_utils.LLM_PROVIDER", "openai"), patch(
        "openai.chat.completions.create", side_effect=Exception("fail")
    ):
        result = gpt_summarize_with_context("text", [])
        assert "Error" in result


def test_gpt_summarize_with_context_ollama_error():
    with patch("github_agent.llm_utils.LLM_PROVIDER", "ollama"), patch(
        "requests.post", side_effect=Exception("fail")
    ):
        result = gpt_summarize_with_context("text", [])
        assert "Error" in result


def test_gpt_summarize_with_context_unknown_provider():
    with patch("github_agent.llm_utils.LLM_PROVIDER", "unknown"):
        result = gpt_summarize_with_context("test", [])
        assert "Error" in result
        assert "Unknown LLM provider" in result


def test_gpt_summarize_with_context_empty_response():
    """Test handling of empty response from OpenAI."""
    with patch.dict("os.environ", {"OPENAI_API_KEY": "test_key"}), \
         patch("github_agent.llm_utils.LLM_PROVIDER", "openai"), patch(
        "openai.chat.completions.create"
    ) as mock_create:
        mock_create.return_value.choices = [
            type("obj", (), {"message": type("obj", (), {"content": ""})})
        ]
        result = gpt_summarize_with_context("test", [])
        assert result == "[Error: Empty response from LLM.]"


def test_gpt_summarize_with_context_ollama_empty_response():
    """Test handling of empty response from Ollama."""
    with patch("github_agent.llm_utils.LLM_PROVIDER", "ollama"), patch(
        "requests.post"
    ) as mock_post:
        mock_post.return_value.json.return_value = {"choices": [{"message": {"content": ""}}]}
        mock_post.return_value.raise_for_status = lambda: None
        result = gpt_summarize_with_context("test", [])
        assert result == "[Error: Empty response from LLM.]"


def test_gpt_summarize_with_context_long_pr():
    """Test handling of long PR text."""
    long_pr = "A" * 10000  # Very long PR text
    with patch.dict("os.environ", {"OPENAI_API_KEY": "test_key"}), \
         patch("github_agent.llm_utils.LLM_PROVIDER", "openai"), patch(
        "openai.chat.completions.create"
    ) as mock_create:
        mock_create.return_value.choices = [
            type("obj", (), {"message": type("obj", (), {"content": "Summary"})})
        ]
        result = gpt_summarize_with_context(long_pr, [])
        assert result == "Summary"
        # Verify the truncation
        call_args = mock_create.call_args[1]
        messages = call_args["messages"][1]["content"]
        assert len(messages) < 8000  # Max token limit


def test_gpt_summarize_with_context_invalid_ollama_response():
    """Test handling of invalid response from Ollama."""
    with patch("github_agent.llm_utils.LLM_PROVIDER", "ollama"), patch(
        "requests.post"
    ) as mock_post:
        mock_post.return_value.json.return_value = {"invalid": "response"}
        mock_post.return_value.raise_for_status = lambda: None
        result = gpt_summarize_with_context("test", [])
        assert "Error" in result
