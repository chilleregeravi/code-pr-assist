# main.py
import logging

import uvicorn
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from github_agent.github_utils import post_comment_to_pr
from github_agent.llm_utils import gpt_summarize_with_context
from github_agent.models import PullRequestData
from github_agent.qdrant_utils import embed_text, search_similar_prs, upsert_pr

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()


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
        embedding = embed_text(full_text)
        similar = search_similar_prs(embedding)
        similar_bodies = [x["text"] for x in similar if "text" in x]
        summary = gpt_summarize_with_context(full_text, similar_bodies)

        try:
            post_comment_to_pr(pr.number, summary)
        except Exception:
            logger.warning(f"Could not post comment to PR #{pr.number}.")

        try:
            upsert_pr(pr.number, embedding, full_text)
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
