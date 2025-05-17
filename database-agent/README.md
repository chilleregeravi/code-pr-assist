# Database Agent

A Python package for processing and storing GitHub Pull Request data in a vector database (Qdrant) for semantic search and analysis.

## GitHub API Integration

The package uses the official GitHub REST API v3 through the PyGithub library. The integration includes:

- Rate limiting handling (5000 requests per hour for authenticated requests)
- Automatic pagination for large result sets
- Retry mechanism with exponential backoff for failed requests
- Support for all PR-related endpoints:
  - Pull Requests
  - Reviews
  - Comments
  - Files changed
  - Commits

### API Version and Authentication

- **API Version**: REST API v3
- **Authentication**: Personal Access Token (PAT) with the following scopes:
  - `repo` (Full control of private repositories)
  - `read:org` (Read organization data)
  - `read:user` (Read user data)

### Rate Limiting

The client automatically handles GitHub's rate limiting:
- 5000 requests per hour for authenticated requests
- Automatic retry with exponential backoff when rate limit is hit
- Respects the `X-RateLimit-Reset` header for optimal retry timing

## Qdrant API Integration

The package uses Qdrant's vector database for storing and searching PR data. The integration includes:

- Vector embeddings using sentence-transformers
- Semantic search capabilities
- Batch processing for efficient data ingestion
- Automatic collection management
- Support for all vector operations:
  - Vector storage
  - Similarity search
  - Batch operations
  - Collection management

### API Version and Authentication

- **API Version**: Qdrant REST API v1
- **Authentication**: API Key (optional)
- **Connection**: HTTP/HTTPS endpoint

### Vector Store Features

The client automatically handles:
- Vector dimensionality (384 for all-MiniLM-L6-v2 model)
- Collection creation and management
- Batch processing with configurable batch sizes
- Error handling and retries
- Connection pooling and management

### Embedding Model

The package uses the `all-MiniLM-L6-v2` model from sentence-transformers by default, which provides:
- 384-dimensional embeddings
- Fast inference speed
- Good semantic search quality
- Support for multiple languages
- Small model size (90MB)

## Components

### 1. GitHub Client (`github_client.py`)

The GitHub client handles fetching PR data from GitHub's API with rate limiting and retry mechanisms.

#### Main Classes

##### `GitHubClient`

```python
def __init__(self, token: Optional[str] = None, base_url: Optional[str] = None, pr_processor: Any = None)
```
- **Purpose**: Initialize GitHub client with authentication and processing settings
- **Inputs**:
  - `token`: GitHub personal access token (optional, can use GITHUB_TOKEN env var)
  - `base_url`: GitHub API base URL (optional)
  - `pr_processor`: Optional PRProcessor instance for processing PRs
- **Raises**: `ValueError` if no token is provided

```python
def get_pr_data(self, repo_name: str, pr_number: int) -> Dict[str, Any]
```
- **Purpose**: Fetch detailed data for a specific PR
- **Inputs**:
  - `repo_name`: Repository name in format 'owner/repo'
  - `pr_number`: Pull request number
- **Returns**: Dictionary containing PR information including:
  - Basic PR info (id, title, body, state)
  - Metadata (created_at, updated_at, author)
  - Comments and reviews
  - Files changed
  - Branch information
  - Merge status
- **Raises**: `PRProcessingError` if fetching fails

```python
def get_repo_prs(self, repo_name: str, state: str = "all", sort: str = "updated", 
                direction: str = "desc", limit: Optional[int] = None) -> Generator[Dict[str, Any], None, None]
```
- **Purpose**: Fetch multiple PRs from a repository
- **Inputs**:
  - `repo_name`: Repository name in format 'owner/repo'
  - `state`: PR state ('open', 'closed', 'all')
  - `sort`: Sort field ('created', 'updated', 'popularity', 'long-running')
  - `direction`: Sort direction ('asc', 'desc')
  - `limit`: Maximum number of PRs to fetch
- **Returns**: Generator yielding PR data dictionaries
- **Raises**: `PRProcessingError` if fetching fails

```python
def process_and_store_prs(self, pr_processor, repo_name: str, state: str = "all", limit: Optional[int] = None) -> None
```
- **Purpose**: Fetch PRs from a repository and store them in the vector database
- **Inputs**:
  - `pr_processor`: PRProcessor instance for storing PR data
  - `repo_name`: Repository name in format 'owner/repo'
  - `state`: PR state to fetch ('open', 'closed', 'all')
  - `limit`: Maximum number of PRs to process
- **Raises**: `PRProcessingError` if processing or storing fails

```python
def search_prs(self, pr_processor, query: str, repo_name: Optional[str] = None, limit: int = 5) -> List[Dict[str, Any]]
```
- **Purpose**: Search for similar PRs in the vector database
- **Inputs**:
  - `pr_processor`: PRProcessor instance for searching PRs
  - `query`: Search query text
  - `repo_name`: Optional repository name to filter results
  - `limit`: Maximum number of results to return
- **Returns**: List of similar PRs with their scores

### 2. PR Processor (`pr_processor.py`)

Handles validation, transformation, and processing of PR data.

#### Main Classes

##### `PRProcessor`

```python
def __init__(self, vector_store: VectorStore, github_client: Optional[Any] = None)
```
- **Purpose**: Initialize PR processor with vector store and optional GitHub client
- **Inputs**:
  - `vector_store`: Vector store instance for storing PR data
  - `github_client`: Optional GitHub client for fetching PR data

```python
def validate_pr_data(self, pr_data: Dict[str, Any]) -> None
```
- **Purpose**: Validate PR data structure and types
- **Inputs**:
  - `pr_data`: Dictionary containing PR information
- **Raises**: `DataValidationError` if validation fails

```python
def transform_pr_data(self, pr_data: Dict[str, Any]) -> Dict[str, Any]
```
- **Purpose**: Transform PR data for storage
- **Inputs**:
  - `pr_data`: Dictionary containing PR information
- **Returns**: Transformed PR data with:
  - Normalized lists for labels and comments
  - Added metadata (processed_at timestamp)

```python
def process_pr(self, pr_data: Dict[str, Any]) -> bool
```
- **Purpose**: Process a single PR and store it in the vector store
- **Inputs**:
  - `pr_data`: Dictionary containing PR information
- **Returns**: True if successful
- **Raises**: `PRProcessingError` if processing fails

```python
def process_prs_batch(self, prs_data: List[Dict[str, Any]]) -> bool
```
- **Purpose**: Process multiple PRs in batch and store them in the vector store
- **Inputs**:
  - `prs_data`: List of PR data dictionaries
- **Returns**: True if successful
- **Raises**: `PRProcessingError` if processing fails

```python
def process_repository_prs(self, repo_name: str) -> bool
```
- **Purpose**: Process all PRs from a repository and store them in the vector store
- **Inputs**:
  - `repo_name`: Repository name in format 'owner/repo'
- **Returns**: True if successful
- **Raises**: `PRProcessingError` if processing fails

### 3. Vector Store (`vector_store.py`)

The vector store interface and Qdrant implementation for storing and searching PR data.

#### Main Classes

##### `VectorStore` (Abstract Base Class)

Abstract interface defining vector store operations.

##### `QdrantStore`

```python
def __init__(self, url: Optional[str] = None, api_key: Optional[str] = None, 
            collection_name: str = "github_prs", embedding_model: str = "all-MiniLM-L6-v2",
            batch_size: int = 100)
```
- **Purpose**: Initialize Qdrant store with connection settings
- **Inputs**:
  - `url`: Qdrant server URL (optional, can use QDRANT_URL env var)
  - `api_key`: Qdrant API key (optional, can use QDRANT_API_KEY env var)
  - `collection_name`: Name of the collection to use
  - `embedding_model`: Name of the sentence transformer model
  - `batch_size`: Number of points to process in each batch
- **Raises**: `ConfigurationError` if URL not provided

```python
def store_pr(self, pr_data: Dict[str, Any]) -> bool
```
- **Purpose**: Store a single PR in the vector store
- **Inputs**:
  - `pr_data`: Dictionary containing PR information
- **Returns**: True if successful
- **Raises**: 
  - `ConnectionError` if store not initialized
  - `VectorStoreError` if storing fails

```python
def store_prs_batch(self, prs_data: List[Dict[str, Any]]) -> bool
```
- **Purpose**: Store multiple PRs in the vector store
- **Inputs**:
  - `prs_data`: List of PR data dictionaries
- **Returns**: True if successful
- **Raises**: 
  - `ConnectionError` if store not initialized
  - `VectorStoreError` if storing fails

```python
def search_similar_prs(self, query: str, limit: int = 5) -> List[Dict[str, Any]]
```
- **Purpose**: Search for similar PRs based on query text
- **Inputs**:
  - `query`: Search query text
  - `limit`: Maximum number of results to return
- **Returns**: List of similar PRs with their scores
- **Raises**: 
  - `ConnectionError` if store not initialized
  - `VectorStoreError` if search fails

```python
def delete_pr(self, pr_id: int) -> bool
```
- **Purpose**: Delete a specific PR from the vector store
- **Inputs**:
  - `pr_id`: ID of the PR to delete
- **Returns**: True if successful
- **Raises**: 
  - `ConnectionError` if store not initialized
  - `VectorStoreError` if deletion fails

```python
def delete_collection(self) -> bool
```
- **Purpose**: Delete the entire collection
- **Returns**: True if successful
- **Raises**: 
  - `ConnectionError` if store not initialized
  - `VectorStoreError` if deletion fails

## Usage Example

```python
from database_agent import GitHubClient, QdrantStore, PRProcessor

# Initialize components
github_client = GitHubClient(token="your_github_token")
vector_store = QdrantStore(url="your_qdrant_url")
pr_processor = PRProcessor(vector_store=vector_store, github_client=github_client)

# Initialize vector store
vector_store.initialize()

# Process PRs from a repository
pr_processor.process_repository_prs("owner/repo")

# Search for similar PRs
similar_prs = pr_processor.search_similar_prs(
    query="Add authentication feature",
    limit=5
)

# Delete a specific PR
pr_processor.delete_pr(pr_id=123)

# Delete all PRs
pr_processor.delete_collection()
```

## Environment Variables

- `GITHUB_TOKEN`: GitHub personal access token
- `QDRANT_URL`: Qdrant server URL
- `QDRANT_API_KEY`: Qdrant API key

## Dependencies

- PyGithub
- qdrant-client
- sentence-transformers
- pytest (for testing)
- black (for code formatting)
- isort (for import sorting)
- flake8 (for linting)
- mypy (for type checking) 