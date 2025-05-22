import logging
from github_agent.qdrant_utils import embed_text, search_similar_prs, upsert_pr

logger = logging.getLogger(__name__)

class EmbeddingAgent:
    def embed(self, text):
        return embed_text(text)

    def search_similar(self, embedding, k=3):
        return search_similar_prs(embedding, k)

    def upsert(self, pr_number, embedding, full_text):
        upsert_pr(pr_number, embedding, full_text)

# This file has been moved to agents/embedding_agent.py. Please update imports accordingly.
