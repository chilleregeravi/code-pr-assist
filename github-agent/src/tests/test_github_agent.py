from unittest.mock import patch

import pytest
from github_agent.agents.github_agent import GitHubAgent


def test_post_comment_success():
    """Test successful comment posting to PR."""
    with patch("github_agent.agents.github_agent.post_comment_to_pr") as mock_post:
        agent = GitHubAgent()
        agent.post_comment(123, "Test comment")
        mock_post.assert_called_once_with(123, "Test comment")


def test_post_comment_error():
    """Test error handling in comment posting."""
    with patch(
        "github_agent.agents.github_agent.post_comment_to_pr",
        side_effect=Exception("Failed to post"),
    ):
        agent = GitHubAgent()
        with pytest.raises(Exception):
            agent.post_comment(123, "Test comment")
