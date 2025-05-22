# This file has been moved to agents/github_agent.py. Please update imports accordingly.

import logging
from github_agent.github_utils import post_comment_to_pr

logger = logging.getLogger(__name__)

class GitHubAgent:
    def post_comment(self, pr_number, comment):
        post_comment_to_pr(pr_number, comment)
