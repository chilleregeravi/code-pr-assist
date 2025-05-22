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

def test_summarize_with_different_model():
    """Test PR summarization with different model."""
    mock_content = "Summary of PR"
    mock_response = Mock()
    mock_response.choices = [Mock(message=Mock(content=mock_content))]
    
    with patch('openai.ChatCompletion.create', return_value=mock_response) as mock_create, \
         patch('github_agent.agents.llm_agent.OPENAI_MODEL', 'gpt-3.5-turbo'):
        agent = LLMAgent()
        result = agent.summarize_with_context("test PR", ["context"])
        
        assert result == mock_content
        mock_create.assert_called_once()
        call_args = mock_create.call_args[1]
        assert call_args["model"] == "gpt-3.5-turbo"

def test_summarize_empty_response():
    """Test handling of empty response from OpenAI."""
    mock_response = Mock()
    mock_response.choices = [Mock(message=Mock(content=""))]
    
    with patch('openai.ChatCompletion.create', return_value=mock_response):
        agent = LLMAgent()
        result = agent.summarize_with_context("test PR", [])
        assert result == ""

def test_summarize_with_empty_context():
    """Test summarization with no context."""
    mock_content = "Summary with no context"
    mock_response = Mock()
    mock_response.choices = [Mock(message=Mock(content=mock_content))]
    
    with patch('openai.ChatCompletion.create', return_value=mock_response) as mock_create:
        agent = LLMAgent()
        result = agent.summarize_with_context("test PR", [])
        
        assert result == mock_content
        mock_create.assert_called_once()
        call_args = mock_create.call_args[1]
        messages = call_args["messages"][1]["content"]
        assert "Context from similar past PRs:" in messages
        assert "New PR:" in messages
