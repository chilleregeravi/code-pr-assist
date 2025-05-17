import os

os.environ["REPO_NAME"] = "dummy/repo"
os.environ["GITHUB_TOKEN"] = "dummy"

from unittest.mock import MagicMock, patch

import pytest

patcher_github = patch("github_agent.github_utils.Github")
MockGithub = patcher_github.start()
mock_github = MockGithub.return_value
mock_repo = MagicMock()
mock_github.get_repo.return_value = mock_repo

from github_agent.github_utils import get_repo, post_comment_to_pr


def teardown_module(module):
    patcher_github.stop()


def test_post_comment_to_pr_success():
    with patch("github_agent.github_utils.get_repo", return_value=mock_repo):
        mock_pr = MagicMock()
        mock_repo.get_pull.return_value = mock_pr
        post_comment_to_pr(1, "test comment")
        mock_pr.create_issue_comment.assert_called_once_with("test comment")


def test_post_comment_to_pr_error():
    with patch("github_agent.github_utils.get_repo", return_value=mock_repo):
        mock_repo.get_pull.side_effect = Exception("fail")
        with pytest.raises(Exception):
            post_comment_to_pr(1, "test comment")


def test_get_repo_error():
    with patch("github_agent.github_utils.Github") as MockGithub:
        mock_github = MockGithub.return_value
        mock_github.get_repo.side_effect = Exception("fail")
        with pytest.raises(Exception):
            get_repo()
