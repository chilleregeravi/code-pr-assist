import logging
from opentelemetry import trace

from github import Github
from github_agent.config import GITHUB_TOKEN, REPO_NAME

logger = logging.getLogger(__name__)
tracer = trace.get_tracer(__name__)


def get_repo():
    g = Github(GITHUB_TOKEN)
    return g.get_repo(REPO_NAME)


def post_comment_to_pr(pr_number: int, comment: str):
    """Post a comment to the specified PR on GitHub."""
    with tracer.start_as_current_span("post_comment_to_pr") as span:
        span.set_attribute("pr.number", pr_number)
        try:
            repo = get_repo()
            pr = repo.get_pull(pr_number)
            pr.create_issue_comment(comment)
        except Exception as e:
            logger.error(f"Failed to post comment to PR #{pr_number}: {e}")
            span.record_exception(e)
            raise
