import os
from github import Github
from qdrant_client import QdrantClient
from qdrant_client.http import models
from sentence_transformers import SentenceTransformer
from dotenv import load_dotenv
import time
from typing import List, Dict, Any

# Load environment variables
load_dotenv()

class GitHubPRToQdrant:
    def __init__(self):
        # Initialize GitHub client
        self.github_token = os.getenv('GITHUB_TOKEN')
        if not self.github_token:
            raise ValueError("GitHub token not found in environment variables")
        self.github_client = Github(self.github_token)

        # Initialize Qdrant client
        self.qdrant_url = os.getenv('QDRANT_URL')
        self.qdrant_api_key = os.getenv('QDRANT_API_KEY')
        self.qdrant_client = QdrantClient(
            url=self.qdrant_url,
            api_key=self.qdrant_api_key
        )

        # Initialize embedding model
        self.model = SentenceTransformer('all-MiniLM-L6-v2')

        # Create collection if it doesn't exist
        self._ensure_collection_exists()

    def _ensure_collection_exists(self):
        """Ensure the Qdrant collection exists, create if it doesn't."""
        collections = self.qdrant_client.get_collections().collections
        collection_names = [collection.name for collection in collections]

        if "github_prs" not in collection_names:
            collection_config = models.VectorParams(
                size=384,  # Size for all-MiniLM-L6-v2 model
                distance=models.Distance.COSINE
            )
            self.qdrant_client.create_collection(
                collection_name="github_prs",
                vectors_config=collection_config
            )

    def fetch_pr_data(self, repo_name: str, pr_number: int) -> Dict[str, Any]:
        """Fetch PR data from GitHub."""
        try:
            repo = self.github_client.get_repo(repo_name)
            pr = repo.get_pull(pr_number)

            # Add delay to respect rate limits
            time.sleep(0.5)

            pr_data = {
                "id": pr.number,
                "title": pr.title,
                "body": pr.body,
                "state": pr.state,
                "created_at": pr.created_at.isoformat(),
                "updated_at": pr.updated_at.isoformat(),
                "author": pr.user.login,
                "labels": [label.name for label in pr.labels],
                "comments": [comment.body for comment in pr.get_issue_comments()]
            }

            return pr_data
        except Exception as e:
            print(f"Error fetching PR data: {str(e)}")
            raise

    def process_and_upload_pr(self, pr_data: Dict[str, Any]):
        """Process PR data and upload to Qdrant."""
        try:
            # Generate embedding
            text_to_embed = f"{pr_data['title']} {pr_data['body']}"
            embedding = self.model.encode(text_to_embed)

            # Prepare point for Qdrant
            point = models.PointStruct(
                id=pr_data['id'],
                vector=embedding.tolist(),
                payload=pr_data
            )

            # Upload to Qdrant
            self.qdrant_client.upsert(
                collection_name="github_prs",
                points=[point]
            )

            print(f"Successfully uploaded PR #{pr_data['id']} to Qdrant")
        except Exception as e:
            print(f"Error processing and uploading PR: {str(e)}")
            raise

    def search_similar_prs(self, query_text: str, limit: int = 5) -> List[Dict[str, Any]]:
        """Search for similar PRs in Qdrant."""
        try:
            # Generate embedding for query
            query_embedding = self.model.encode(query_text)

            # Search in Qdrant
            search_result = self.qdrant_client.search(
                collection_name="github_prs",
                query_vector=query_embedding.tolist(),
                limit=limit
            )

            return [
                {
                    "id": hit.id,
                    "score": hit.score,
                    "payload": hit.payload
                }
                for hit in search_result
            ]
        except Exception as e:
            print(f"Error searching similar PRs: {str(e)}")
            raise

def main():
    # Example usage
    try:
        # Initialize the integration
        pr_integration = GitHubPRToQdrant()

        # Example: Fetch and upload a PR
        repo_name = "owner/repo"  # Replace with actual repo
        pr_number = 123  # Replace with actual PR number

        # Fetch PR data
        pr_data = pr_integration.fetch_pr_data(repo_name, pr_number)

        # Process and upload to Qdrant
        pr_integration.process_and_upload_pr(pr_data)

        # Example: Search for similar PRs
        query = "Add new feature for user authentication"
        similar_prs = pr_integration.search_similar_prs(query)

        print("\nSimilar PRs found:")
        for pr in similar_prs:
            print(f"PR #{pr['id']} - Score: {pr['score']}")
            print(f"Title: {pr['payload']['title']}\n")

    except Exception as e:
        print(f"Error in main execution: {str(e)}")

if __name__ == "__main__":
    main()
