import pytest
from unittest.mock import Mock, patch
from github_agent.agents.llm_agent import LLMAgent

def test_summarize_with_context_success():
    """Test successful PR summarization."""
    mock_content = "Summary of PR"
    mock_response = Mock()
    mock_response.choices = [Mock(message=Mock(content=mock_content))]
    
    with patch('openai.ChatCompletion.create', return_value=mock_response) as mock_create:
        agent = LLMAgent()
        result = agent.summarize_with_context("test PR", ["context1", "context2"])
        
        assert result == mock_content
        mock_create.assert_called_once()
        call_args = mock_create.call_args[1]
        assert call_args["model"] == "gpt-4"  # default model
        assert len(call_args["messages"]) == 2
        assert call_args["messages"][0]["role"] == "system"
        assert call_args["messages"][1]["role"] == "user"
        assert "test PR" in call_args["messages"][1]["content"]
        assert "context1" in call_args["messages"][1]["content"]
        assert "context2" in call_args["messages"][1]["content"]

def test_summarize_with_context_error():
    """Test error handling in PR summarization."""
    with patch('openai.ChatCompletion.create', side_effect=Exception("API Error")):
        agent = LLMAgent()
        result = agent.summarize_with_context("test PR", [])
        assert "Error" in result
        assert "Could not generate summary" in result
