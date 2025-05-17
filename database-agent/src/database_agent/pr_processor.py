"""PR data processing and validation."""

import re
from datetime import datetime
from typing import Any, Dict, List, Optional

from .exceptions import DataValidationError, PRProcessingError
from .vector_store import VectorStore


class PRProcessor:
    """Process and validate PR data before storing in vector database."""

    REQUIRED_FIELDS = {
        "id": int,
        "title": str,
        "body": str,
        "state": str,
        "created_at": str,
        "updated_at": str,
        "author": str,
        "repo_name": str,
    }

    VALID_STATES = {"open", "closed", "merged"}

    def __init__(self, vector_store: VectorStore, github_client: Optional[Any] = None):
        """Initialize PR processor.

        Args:
            vector_store: Vector store instance for storing PR data.
            github_client: Optional GitHub client for fetching PR data.
        """
        self.vector_store = vector_store
        self.github_client = github_client

    def validate_pr_data(self, pr_data: Dict[str, Any]) -> None:
        """Validate PR data structure and types.

        Args:
            pr_data: Dictionary containing PR information.

        Raises:
            DataValidationError: If validation fails.
        """
        # Check required fields
        for field, field_type in self.REQUIRED_FIELDS.items():
            if field not in pr_data:
                raise DataValidationError(f"Missing required field: {field}")
            if not isinstance(pr_data[field], field_type):
                raise DataValidationError(
                    f"Invalid type for field {field}: expected {field_type},\n"
                    f"got {type(pr_data[field])}"
                )

        # Validate dates
        try:
            created_at = datetime.fromisoformat(pr_data["created_at"])
            updated_at = datetime.fromisoformat(pr_data["updated_at"])

            if updated_at < created_at:
                raise DataValidationError(
                    "Updated date cannot be earlier than created date"
                )

        except ValueError as e:
            raise DataValidationError(f"Invalid date format: {str(e)}")

        # Validate state
        if pr_data["state"] not in self.VALID_STATES:
            raise DataValidationError(f"Invalid state: {pr_data['state']}")

        # Validate repository name format
        if not re.match(r"^[\w.-]+/[\w.-]+$", pr_data["repo_name"]):
            raise DataValidationError(
                f"Invalid repository name format: {pr_data['repo_name']}"
            )

        # Validate ID is positive
        if pr_data["id"] <= 0:
            raise DataValidationError(f"Invalid PR ID: {pr_data['id']}")

    def transform_pr_data(self, pr_data: Dict[str, Any]) -> Dict[str, Any]:
        """Transform PR data for storage.

        Args:
            pr_data: Dictionary containing PR information.

        Returns:
            Transformed PR data.
        """
        transformed_data = pr_data.copy()

        # Ensure labels is a list
        transformed_data["labels"] = pr_data.get("labels", [])
        if not isinstance(transformed_data["labels"], list):
            transformed_data["labels"] = [transformed_data["labels"]]

        # Ensure comments is a list
        transformed_data["comments"] = pr_data.get("comments", [])
        if not isinstance(transformed_data["comments"], list):
            transformed_data["comments"] = [transformed_data["comments"]]

        # Add metadata
        transformed_data["processed_at"] = datetime.utcnow().isoformat()

        return transformed_data

    def process_and_store_pr(self, pr_data: Dict[str, Any]) -> None:
        """Process and store PR data in vector store.

        Args:
            pr_data: Dictionary containing PR information.

        Raises:
            DataValidationError: If PR data validation fails.
            VectorStoreError: If storing in vector store fails.
        """
        # Validate PR data
        self.validate_pr_data(pr_data)

        # Transform PR data
        processed_data = self.transform_pr_data(pr_data)

        # Store in vector store
        self.vector_store.store_pr(processed_data)

    def process_and_store_prs_batch(self, prs_data: List[Dict[str, Any]]) -> None:
        """Process and store multiple PRs in vector store.

        Args:
            prs_data: List of PR data dictionaries.

        Raises:
            DataValidationError: If any PR data validation fails.
            VectorStoreError: If storing in vector store fails.
        """
        processed_prs = []
        errors = []

        # Process each PR
        for pr_data in prs_data:
            try:
                # Validate PR data
                self.validate_pr_data(pr_data)

                # Transform PR data
                processed_data = self.transform_pr_data(pr_data)
                processed_prs.append(processed_data)

            except Exception as e:
                errors.append(f"PR #{pr_data.get('id', 'unknown')}: {str(e)}")
                continue

        # Store processed PRs in batch
        if processed_prs:
            self.vector_store.store_prs_batch(processed_prs)

        # Report errors if any
        if errors:
            raise DataValidationError(
                "Failed to process some PRs:\n" + "\n".join(errors)
            )

    def search_similar_prs(self, query: str, limit: int = 5) -> List[Dict[str, Any]]:
        """Search for similar PRs.

        Args:
            query: Search query text.
            limit: Maximum number of results to return.

        Returns:
            List of similar PRs with their scores.
        """
        return self.vector_store.search_similar_prs(query, limit)

    def get_pr(self, pr_id: int) -> Optional[Dict[str, Any]]:
        """Retrieve a specific PR by ID.

        Args:
            pr_id: ID of the PR to retrieve.

        Returns:
            PR data if found, None otherwise.
        """
        return self.vector_store.get_pr(pr_id)

    def delete_pr(self, pr_id: int) -> None:
        """Delete a specific PR from the vector store.

        Args:
            pr_id: ID of the PR to delete.
        """
        self.vector_store.delete_pr(pr_id)

    def delete_collection(self) -> None:
        """Delete the entire collection."""
        self.vector_store.delete_collection()

    def process_pr(self, pr_data: Dict[str, Any]) -> bool:
        """Process a single PR and store it in the vector store."""
        try:
            self.validate_pr_data(pr_data)
            transformed = self.transform_pr_data(pr_data)
            return self.vector_store.store_pr(transformed)
        except Exception as e:
            raise PRProcessingError(f"Failed to process PR: {str(e)}")

    def process_prs_batch(self, prs_data: List[Dict[str, Any]]) -> bool:
        """Process multiple PRs in batch and store them in the vector store."""
        try:
            processed = [self.transform_pr_data(pr) for pr in prs_data]
            return self.vector_store.store_prs_batch(processed)
        except Exception as e:
            raise PRProcessingError(f"Failed to process PRs batch: {str(e)}")

    def process_repository_prs(self, repo_name: str) -> bool:
        """Process all PRs from a repository and store them in the vector store."""
        try:
            if self.github_client is None:
                raise PRProcessingError("GitHub client not initialized")
            prs = self.github_client.get_pull_requests(repo_name)
            prs_data = [
                {
                    "id": pr.number,
                    "title": pr.title,
                    "body": pr.body,
                    "labels": [label.name for label in getattr(pr, "labels", [])],
                }
                for pr in prs
            ]
            return self.process_prs_batch(prs_data)
        except Exception as e:
            raise PRProcessingError(f"Failed to process repository PRs: {str(e)}")
