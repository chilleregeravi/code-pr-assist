import logging
from typing import List, Optional

import requests
from github_agent.config import (
    LLM_PROVIDER,
    OLLAMA_MODEL,
    OLLAMA_URL,
    OPENAI_API_KEY,
    OPENAI_MODEL,
)
from openai import APIError, APITimeoutError, OpenAI, OpenAIError, RateLimitError

logger = logging.getLogger(__name__)

# Initialize OpenAI client globally
_openai_client: Optional[OpenAI] = None


def _get_openai_client() -> OpenAI:
    """Get or create OpenAI client instance."""
    global _openai_client
    if _openai_client is None:
        _openai_client = OpenAI(
            api_key=OPENAI_API_KEY,
            timeout=60.0,
        )
    return _openai_client


def gpt_summarize_with_context(pr_text: str, similar_contexts: List[str]) -> str:
    """Summarize PR and suggest labels using OpenAI GPT or Ollama with context."""
    # Truncate PR text if too long (max ~2000 tokens, roughly 8000 chars)
    if len(pr_text) > 7000:
        pr_text = pr_text[:7000] + "... (truncated)"

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
            client = _get_openai_client()
            response = client.chat.completions.create(
                model=OPENAI_MODEL,
                messages=[
                    {"role": "system", "content": "You assist with GitHub PR reviews."},
                    {"role": "user", "content": prompt},
                ],
                timeout=60.0,
            )
            content = response.choices[0].message.content
            if not content:
                return "[Error: Empty response from LLM.]"
            return content.strip()

        except RateLimitError as e:
            logger.error(f"OpenAI rate limit exceeded: {e}")
            return "[Error: Rate limit exceeded. Please try again later.]"

        except APITimeoutError as e:
            logger.error(f"OpenAI API timeout: {e}")
            return "[Error: Request timed out. Please try again.]"

        except APIError as e:
            logger.error(f"OpenAI API error: {e}")
            return "[Error: API error occurred.]"

        except OpenAIError as e:
            logger.error(f"OpenAI SDK error: {e}")
            return "[Error: Could not generate summary.]"

        except Exception as e:
            logger.error(f"Unexpected error in OpenAI call: {e}")
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
                content = data["choices"][0]["message"]["content"]
                if not content:
                    return "[Error: Empty response from LLM.]"
                return content.strip()
            elif "message" in data:
                content = data["message"]["content"]
                if not content:
                    return "[Error: Empty response from LLM.]"
                return content.strip()
            else:
                logger.error(f"Unexpected Ollama response: {data}")
                return "[Error: Unexpected Ollama response.]"

        except requests.exceptions.Timeout as e:
            logger.error(f"Ollama request timeout: {e}")
            return "[Error: Request timed out. Please try again.]"

        except requests.exceptions.RequestException as e:
            logger.error(f"Ollama request failed: {e}")
            return "[Error: Could not generate summary from Ollama.]"

        except Exception as e:
            logger.error(f"Unexpected error in Ollama call: {e}")
            return "[Error: Could not generate summary from Ollama.]"

    else:
        logger.error(f"Unknown LLM_PROVIDER: {LLM_PROVIDER}")
        return "[Error: Unknown LLM provider configured.]"
