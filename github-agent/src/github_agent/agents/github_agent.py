import logging

from opentelemetry import trace

from github_agent.github_utils import post_comment_to_pr

logger = logging.getLogger(__name__)
tracer = trace.get_tracer(__name__)


class GitHubAgent:
    def post_comment(self, pr_number, comment):
        with tracer.start_as_current_span("GitHubAgent.post_comment") as span:
            span.set_attribute("pr.number", pr_number)
            return post_comment_to_pr(pr_number, comment)
