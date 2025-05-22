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


@app.post("/webhook")
async def handle_pr_webhook(request: Request):
    """Handle GitHub PR webhook events."""
    try:
        data = await request.json()
        if "pull_request" not in data:
            logger.info("Webhook received without pull_request data.")
            return JSONResponse(content={"status": "ignored"}, status_code=200)

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

        try:
            github_agent.post_comment(pr.number, summary)
        except Exception:
            logger.warning(f"Could not post comment to PR #{pr.number}.")

        try:
            embedding_agent.upsert(pr.number, embedding, full_text)
        except Exception as e:
            logger.error(f"Failed to upsert PR to Qdrant: {e}")

        return JSONResponse(
            content={"status": "processed", "summary": summary}, status_code=200
        )
    except Exception as e:
        logger.error(f"Webhook processing failed: {e}")
        return JSONResponse(
            content={"status": "error", "message": str(e)}, status_code=500
        )


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
