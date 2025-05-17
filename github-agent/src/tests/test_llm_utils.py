from unittest.mock import patch

import pytest

from github_agent.llm_utils import gpt_summarize_with_context


@pytest.mark.parametrize(
    "provider,expected", [("openai", "OpenAI summary"), ("ollama", "Ollama summary")]
)
def test_gpt_summarize_with_context(monkeypatch, provider, expected):
    pr_text = "Test PR"
    similar_contexts = ["Context1", "Context2"]
    if provider == "openai":
        with patch("github_agent.llm_utils.LLM_PROVIDER", "openai"), patch(
            "openai.ChatCompletion.create"
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
    with patch("github_agent.llm_utils.LLM_PROVIDER", "openai"), patch(
        "openai.ChatCompletion.create", side_effect=Exception("fail")
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
    with patch("github_agent.llm_utils.LLM_PROVIDER", "unknown"), patch(
        "openai.ChatCompletion.create"
    ) as mock_create:
        result = gpt_summarize_with_context("text", [])
        assert "Unknown LLM provider" in result or "Error" in result
