# main.py
import logging

import uvicorn
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from github_agent.agents.llm_agent import LLMAgent
from github_agent.agents.embedding_agent import EmbeddingAgent
from github_agent.agents.github_agent import GitHubAgent
from github_agent.models import PullRequestData

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()

llm_agent = LLMAgent()
embedding_agent = EmbeddingAgent()
github_agent = GitHubAgent()

@app.get("/")
async def root():
    """Root endpoint."""
    return {"message": "GitHub PR Agent - OpenAI-powered PR analysis"}

@app.get("/health")
async def health():
    """Health check endpoint."""
    return {"status": "healthy"}


@app.post("/webhook")
async def handle_pr_webhook(request: Request):
    """Handle GitHub PR webhook events."""
    # Check for required header
    event_type = request.headers.get("X-GitHub-Event")
    if not event_type:
        return JSONResponse(
            content={"detail": "Missing X-GitHub-Event header"},
            status_code=400
        )
    
    # Validate event type
    if event_type != "pull_request":
        return JSONResponse(
            content={"detail": f"Unsupported event type: {event_type}"},
            status_code=400
        )

    try:
        data = await request.json()
        if "pull_request" not in data or "action" not in data:
            logger.info("Webhook received without required data.")
            return JSONResponse(
                content={"detail": "Missing required fields"},
                status_code=422
            )

        pr_info = data["pull_request"]
        required_fields = ["title", "body", "number", "diff_url"]
        if not all(field in pr_info for field in required_fields):
            logger.error("Missing required PR fields in webhook payload.")
            return JSONResponse(
                content={"status": "error", "message": "Missing PR fields"},
                status_code=400,
            )

        pr = PullRequestData(
            title=pr_info["title"],
            body=pr_info["body"],
            number=pr_info["number"],
            diff_url=pr_info["diff_url"],
        )

        full_text = f"Title: {pr.title}\n\n{pr.body}"
        embedding = embedding_agent.embed(full_text)
        similar = embedding_agent.search_similar(embedding)
        similar_bodies = [x["text"] for x in similar if "text" in x]
        summary = llm_agent.summarize_with_context(full_text, similar_bodies)

        comment_posted = False
        embedding_stored = False
        
        # Try to post the comment
        try:
            github_agent.post_comment(pr.number, summary)
            comment_posted = True
        except Exception as e:
            logger.warning(f"Could not post comment to PR #{pr.number}: {e}")

        # Try to store the embedding
        try:
            embedding_agent.upsert(pr.number, embedding, full_text)
            embedding_stored = True
        except Exception as e:
            logger.error(f"Failed to upsert PR to Qdrant: {e}")

        # Determine status based on operations
        status = "processed" if comment_posted and embedding_stored else "partially_processed"
            
        # Convert the numpy array to a list to make it JSON serializable
        embedding_list = embedding.tolist() if embedding is not None else None
        
        return JSONResponse(
            content={
                "status": status,
                "summary": str(summary),
                "comment_posted": bool(comment_posted),
                "embedding_stored": bool(embedding_stored),
                "embedding": embedding_list
            },
            status_code=200
        )
    except Exception as e:
        logger.error(f"Webhook processing failed: {e}")
        logger.exception("Webhook processing failed")
        return JSONResponse(
            content={"status": "error", "detail": str(e)}, 
            status_code=500
        )


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
