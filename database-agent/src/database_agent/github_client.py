"""GitHub API client for fetching PR data."""

import logging
import os
import time
from collections.abc import Generator
from datetime import datetime
from functools import wraps
from typing import Any

from github import Github, GithubException
from github.PullRequest import PullRequest
from github.Repository import Repository

try:
    from opentelemetry import trace

    tracer = trace.get_tracer(__name__)
    TRACING_AVAILABLE = True
except ImportError:
    # Create a no-op tracer for when OpenTelemetry is not available
    class NoOpSpan:
        def set_attribute(self, key: str, value: Any) -> None:
            pass

        def __enter__(self) -> "NoOpSpan":
            return self

        def __exit__(self, *args: Any) -> None:
            pass

    class NoOpTracer:
        def start_as_current_span(self, name: str) -> NoOpSpan:
            return NoOpSpan()

    tracer = NoOpTracer()  # type: ignore
    TRACING_AVAILABLE = False

from .exceptions import PRProcessingError

logger = logging.getLogger(__name__)


def rate_limit(func):
    """Decorator to handle GitHub API rate limiting."""

    @wraps(func)
    def wrapper(self, *args, **kwargs):
        try:
            return func(self, *args, **kwargs)
        except GithubException as e:
            if e.status == 403 and "rate limit" in str(e).lower():
                reset_time = int(e.headers.get("X-RateLimit-Reset", 0))
                wait_time = max(reset_time - time.time(), 0)
                if wait_time > 0:
                    time.sleep(wait_time)
                    return func(self, *args, **kwargs)
            raise

    return wrapper


def retry(max_retries: int = 3, delay: float = 1.0):
    """Decorator to retry failed API calls."""

    def decorator(func):
        @wraps(func)
        def wrapper(self, *args, **kwargs):
            last_exception = None
            for attempt in range(max_retries):
                try:
                    return func(self, *args, **kwargs)
                except Exception as e:
                    last_exception = e
                    if attempt < max_retries - 1:
                        time.sleep(delay * (2**attempt))  # Exponential backoff
            raise last_exception

        return wrapper

    return decorator


class GitHubClient:
    """GitHub API client for fetching and processing PR data."""

    def __init__(
        self,
        token: str | None = None,
        base_url: str | None = None,
        pr_processor: Any = None,
    ):
        """Initialize GitHub client.

        Args:
            token: GitHub API token. If not provided, will try to get from
            GITHUB_TOKEN env var.
            base_url: GitHub API base URL. If not provided, will use
            default GitHub API URL.
            pr_processor: Optional PRProcessor instance for processing PRs.
        """
        self.token = token or os.getenv("GITHUB_TOKEN")
        if not self.token:
            raise ValueError("GitHub token is required")

        if base_url is not None:
            self.client = Github(self.token, base_url=base_url)
        else:
            self.client = Github(self.token)
        self.pr_processor = pr_processor
        self.batch_size = 100  # Default batch size, can be overridden

    @rate_limit
    @retry()
    def get_pr_data(self, repo_name: str, pr_number: int) -> dict[str, Any]:
        with tracer.start_as_current_span("GitHubClient.get_pr_data") as span:
            span.set_attribute("repo_name", repo_name)
            span.set_attribute("pr_number", pr_number)

            try:
                repo: Repository = self.client.get_repo(repo_name)
                pr: PullRequest = repo.get_pull(pr_number)

                # Fetch comments
                comments = [comment.body for comment in pr.get_issue_comments()]

                # Fetch reviews
                reviews = []
                for review in pr.get_reviews():
                    reviews.append(
                        {
                            "user": review.user.login,
                            "state": review.state,
                            "body": review.body,
                            "submitted_at": review.submitted_at.isoformat(),
                        }
                    )

                # Fetch files changed
                files_changed = []
                for file in pr.get_files():
                    files_changed.append(
                        {
                            "filename": file.filename,
                            "status": file.status,
                            "additions": file.additions,
                            "deletions": file.deletions,
                            "changes": file.changes,
                        }
                    )

                # Compile PR data
                pr_data = {
                    "id": pr.number,
                    "repo_name": repo_name,  # Add repository name
                    "title": pr.title,
                    "body": pr.body,
                    "state": pr.state,
                    "created_at": pr.created_at.isoformat() if pr.created_at else "",
                    "updated_at": pr.updated_at.isoformat() if pr.updated_at else "",
                    "author": pr.user.login,
                    "labels": [label.name for label in pr.labels],
                    "comments": comments,
                    "reviews": reviews,
                    "files_changed": files_changed,
                    "additions": pr.additions,
                    "deletions": pr.deletions,
                    "changed_files": pr.changed_files,
                    "base_branch": pr.base.ref,
                    "head_branch": pr.head.ref,
                    "mergeable": pr.mergeable,
                    "mergeable_state": pr.mergeable_state,
                    "review_comments": pr.review_comments,
                    "commits": pr.commits,
                }

                return pr_data

            except GithubException as e:
                raise PRProcessingError(f"Failed to fetch PR data: {e!s}") from e

    def get_repo_prs(
        self,
        repo_name: str,
        state: str = "all",
        sort: str = "updated",
        direction: str = "desc",
        limit: int | None = None,
    ) -> Generator[dict[str, Any], None, None]:
        with tracer.start_as_current_span("GitHubClient.get_repo_prs") as span:
            span.set_attribute("repo_name", repo_name)
            span.set_attribute("state", state)

            try:
                repo: Repository = self.client.get_repo(repo_name)
                prs = repo.get_pulls(state=state, sort=sort, direction=direction)

                count = 0
                for pr in prs:
                    if limit and count >= limit:
                        break

                    pr_data = self.get_pr_data(repo_name, pr.number)
                    yield pr_data
                    count += 1

            except GithubException as e:
                raise PRProcessingError(f"Failed to fetch repository PRs: {e!s}") from e

    def process_and_store_prs(
        self,
        pr_processor,
        repo_name: str,
        state: str = "all",
        limit: int | None = None,
    ) -> None:
        with tracer.start_as_current_span("GitHubClient.process_and_store_prs") as span:
            span.set_attribute("repo_name", repo_name)
            span.set_attribute("state", state)

            try:
                prs_generator = self.get_repo_prs(repo_name, state=state, limit=limit)
                batch = []

                for pr_data in prs_generator:
                    batch.append(pr_data)

                    if len(batch) >= self.batch_size:
                        self._process_batch(pr_processor, batch)
                        batch = []

                # Process remaining PRs
                if batch:
                    self._process_batch(pr_processor, batch)

            except Exception as e:
                raise PRProcessingError(
                    f"Failed to process repository PRs: {e!s}"
                ) from e

    def _process_batch(self, pr_processor, batch: list[dict[str, Any]]) -> None:
        """Process a batch of PRs.

        Args:
            pr_processor: PRProcessor instance for storing PR data.
            batch: List of PR data dictionaries.
        """
        for pr_data in batch:
            try:
                pr_processor.process_and_store_pr(pr_data)
            except Exception as e:
                logger.error(f"Failed to process PR #{pr_data['id']}: {e!s}")
                continue

    def search_prs(
        self, pr_processor, query: str, repo_name: str | None = None, limit: int = 5
    ) -> list[dict[str, Any]]:
        """Search for similar PRs in the vector database.

        Args:
            pr_processor: PRProcessor instance for searching PRs.
            query: Search query text.
            repo_name: Optional repository name to filter results.
            limit: Maximum number of results to return.

        Returns:
            List of similar PRs with their scores.
        """
        similar_prs = pr_processor.search_similar_prs(query, limit=limit)

        if repo_name:
            # Filter results by repository
            similar_prs = [
                pr for pr in similar_prs if pr["payload"].get("repo_name") == repo_name
            ]

        return similar_prs

    def get_repository(self, repo_name: str) -> Repository:
        """Get a repository by name.

        Args:
            repo_name: Repository name in format 'owner/repo'.

        Returns:
            Repository object.

        Raises:
            PRProcessingError: If fetching repository fails.
        """
        try:
            return self.client.get_repo(repo_name)
        except GithubException as e:
            raise PRProcessingError(f"Failed to fetch repository: {e!s}") from e

    def get_pull_requests(self, repo_name: str) -> list[PullRequest]:
        """Get all pull requests for a repository.

        Args:
            repo_name: Repository name in format 'owner/repo'.

        Returns:
            List of pull request objects.

        Raises:
            PRProcessingError: If fetching pull requests fails.
        """
        try:
            repo = self.get_repository(repo_name)
            return list(repo.get_pulls())
        except GithubException as e:
            raise PRProcessingError(f"Failed to fetch pull requests: {e!s}") from e

    def get_pull_request_comments(self, repo_name: str, pr_number: int) -> list[str]:
        """Get comments for a pull request.

        Args:
            repo_name: Repository name in format 'owner/repo'.
            pr_number: Pull request number.

        Returns:
            List of comment bodies.

        Raises:
            PRProcessingError: If fetching comments fails.
        """
        try:
            repo = self.get_repository(repo_name)
            pr = repo.get_pull(pr_number)
            return [comment.body for comment in pr.get_issue_comments()]
        except GithubException as e:
            raise PRProcessingError(f"Failed to fetch comments: {e!s}") from e

    def get_pull_request_labels(self, repo_name: str, pr_number: int) -> list[str]:
        """Get labels for a pull request.

        Args:
            repo_name: Repository name in format 'owner/repo'.
            pr_number: Pull request number.

        Returns:
            List of label names.

        Raises:
            PRProcessingError: If fetching labels fails.
        """
        try:
            repo = self.get_repository(repo_name)
            pr = repo.get_pull(pr_number)
            return [label.name for label in pr.labels]
        except GithubException as e:
            raise PRProcessingError(f"Failed to fetch labels: {e!s}") from e

    def get_pull_request_state(self, repo_name: str, pr_number: int) -> str:
        """Get state of a pull request.

        Args:
            repo_name: Repository name in format 'owner/repo'.
            pr_number: Pull request number.

        Returns:
            Pull request state.

        Raises:
            PRProcessingError: If fetching state fails.
        """
        try:
            repo = self.get_repository(repo_name)
            pr = repo.get_pull(pr_number)
            return pr.state
        except GithubException as e:
            raise PRProcessingError(f"Failed to fetch state: {e!s}") from e

    def get_pull_request_dates(
        self, repo_name: str, pr_number: int
    ) -> tuple[datetime, datetime]:
        """Get creation and update dates of a pull request.

        Args:
            repo_name: Repository name in format 'owner/repo'.
            pr_number: Pull request number.

        Returns:
            Tuple of (created_at, updated_at) dates.

        Raises:
            PRProcessingError: If fetching dates fails.
        """
        try:
            repo = self.get_repository(repo_name)
            pr = repo.get_pull(pr_number)
            if pr.created_at is None or pr.updated_at is None:
                raise PRProcessingError("PR missing created_at or updated_at")
            return pr.created_at, pr.updated_at
        except GithubException as e:
            raise PRProcessingError(f"Failed to fetch dates: {e!s}") from e

    def process_repository_prs(self, repo_name: str, processor: Any) -> None:
        """Process all PRs in a repository.

        Args:
            repo_name: Repository name in format 'owner/repo'.
            processor: PRProcessor instance for processing PRs.

        Raises:
            PRProcessingError: If processing fails.
        """
        try:
            for pr in self.get_pull_requests(repo_name):
                pr_data = self._extract_pr_data(pr)
                processor.process_pr(pr_data)
        except Exception as e:
            raise PRProcessingError(f"Failed to process repository PRs: {e!s}") from e

    def _extract_pr_data(self, pr: Any) -> dict:
        # Stub implementation to satisfy mypy; replace with real logic as needed
        return {}
