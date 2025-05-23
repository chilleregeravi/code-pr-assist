# GitHub PR to Qdrant Integration Guide

This document outlines the process of integrating GitHub Pull Request data with Qdrant vector database.

## Prerequisites

1. Python 3.8+
2. Qdrant server running (local or cloud)
3. GitHub Personal Access Token with appropriate permissions
4. Required Python packages:
   - `qdrant-client`
   - `PyGithub`
   - `python-dotenv`

## Setup

1. Install required packages:
```bash
pip install qdrant-client PyGithub python-dotenv
```

2. Set up environment variables:
```bash
GITHUB_TOKEN=your_github_token
QDRANT_URL=your_qdrant_url
QDRANT_API_KEY=your_qdrant_api_key  # if using cloud version
```

## Implementation Steps

### 1. Connect to GitHub API

```python
from github import Github
import os
from dotenv import load_dotenv

load_dotenv()

# Initialize GitHub client
github_token = os.getenv('GITHUB_TOKEN')
g = Github(github_token)
```

### 2. Connect to Qdrant

```python
from qdrant_client import QdrantClient
from qdrant_client.http import models

# Initialize Qdrant client
qdrant_client = QdrantClient(
    url=os.getenv('QDRANT_URL'),
    api_key=os.getenv('QDRANT_API_KEY')  # if using cloud version
)
```

### 3. Create Collection in Qdrant

```python
# Define collection configuration
collection_config = models.VectorParams(
    size=1536,  # Adjust based on your embedding model
    distance=models.Distance.COSINE
)

# Create collection
qdrant_client.create_collection(
    collection_name="github_prs",
    vectors_config=collection_config
)
```

### 4. Fetch and Process PR Data

```python
def fetch_pr_data(repo_name, pr_number):
    repo = g.get_repo(repo_name)
    pr = repo.get_pull(pr_number)

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
```

### 5. Generate Embeddings and Upload to Qdrant

```python
from sentence_transformers import SentenceTransformer

# Initialize embedding model
model = SentenceTransformer('all-MiniLM-L6-v2')

def process_and_upload_pr(pr_data):
    # Generate embedding for PR title and body
    text_to_embed = f"{pr_data['title']} {pr_data['body']}"
    embedding = model.encode(text_to_embed)

    # Prepare point for Qdrant
    point = models.PointStruct(
        id=pr_data['id'],
        vector=embedding.tolist(),
        payload=pr_data
    )

    # Upload to Qdrant
    qdrant_client.upsert(
        collection_name="github_prs",
        points=[point]
    )
```

## Usage Example

```python
# Example usage
repo_name = "owner/repo"
pr_number = 123

# Fetch PR data
pr_data = fetch_pr_data(repo_name, pr_number)

# Process and upload to Qdrant
process_and_upload_pr(pr_data)
```

## Querying PRs

```python
def search_similar_prs(query_text, limit=5):
    # Generate embedding for query
    query_embedding = model.encode(query_text)

    # Search in Qdrant
    search_result = qdrant_client.search(
        collection_name="github_prs",
        query_vector=query_embedding.tolist(),
        limit=limit
    )

    return search_result
```

## Best Practices

1. **Rate Limiting**: Implement rate limiting when fetching PR data from GitHub API
2. **Error Handling**: Add proper error handling for API calls
3. **Batch Processing**: For multiple PRs, use batch operations
4. **Data Validation**: Validate PR data before uploading
5. **Regular Updates**: Implement a mechanism to keep PR data up to date

## Monitoring and Maintenance

1. Monitor Qdrant collection size
2. Implement data retention policies
3. Regular backup of important data
4. Monitor API rate limits
5. Log important operations and errors

## Troubleshooting

Common issues and solutions:

1. **Rate Limit Exceeded**: Implement exponential backoff
2. **Connection Issues**: Add retry mechanism
3. **Vector Size Mismatch**: Ensure consistent embedding dimensions
4. **Memory Issues**: Implement batch processing for large datasets

## Security Considerations

1. Never commit API tokens to version control
2. Use environment variables for sensitive data
3. Implement proper access controls
4. Regular token rotation
5. Monitor API usage patterns
