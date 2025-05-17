import logging

import openai
import requests
from github_agent.config import (
    LLM_PROVIDER,
    OLLAMA_MODEL,
    OLLAMA_URL,
    OPENAI_API_KEY,
    OPENAI_MODEL,
)

openai.api_key = OPENAI_API_KEY
logger = logging.getLogger(__name__)


def gpt_summarize_with_context(pr_text, similar_contexts):
    """Summarize PR and suggest labels using OpenAI GPT or Ollama with context."""
    context_text = "\n---\n".join(similar_contexts)
    prompt = f"""
You are a GitHub bot. Summarize the PR below and suggest appropriate labels.
Context from similar past PRs:
{context_text}
---
New PR:
{pr_text}
"""
    if LLM_PROVIDER == "openai":
        try:
            response = openai.ChatCompletion.create(
                model=OPENAI_MODEL,
                messages=[
                    {"role": "system", "content": "You assist with GitHub PR reviews."},
                    {"role": "user", "content": prompt},
                ],
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            logger.error(f"OpenAI API call failed: {e}")
            return "[Error: Could not generate summary.]"
    elif LLM_PROVIDER == "ollama":
        try:
            payload = {
                "model": OLLAMA_MODEL,
                "messages": [
                    {"role": "system", "content": "You assist with GitHub PR reviews."},
                    {"role": "user", "content": prompt},
                ],
            }
            resp = requests.post(
                f"{OLLAMA_URL}/v1/chat/completions", json=payload, timeout=60
            )
            resp.raise_for_status()
            data = resp.json()
            if "choices" in data and data["choices"]:
                return data["choices"][0]["message"]["content"].strip()
            elif "message" in data:
                return data["message"]["content"].strip()
            else:
                logger.error(f"Unexpected Ollama response: {data}")
                return "[Error: Unexpected Ollama response.]"
        except Exception as e:
            logger.error(f"Ollama API call failed: {e}")
            return "[Error: Could not generate summary from Ollama.]"
    else:
        logger.error(f"Unknown LLM_PROVIDER: {LLM_PROVIDER}")
        return "[Error: Unknown LLM provider configured.]"
