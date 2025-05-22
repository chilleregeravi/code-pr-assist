import logging
import openai
from github_agent.config import OPENAI_API_KEY, OPENAI_MODEL

openai.api_key = OPENAI_API_KEY
logger = logging.getLogger(__name__)

class LLMAgent:
    def summarize_with_context(self, pr_text, similar_contexts):
        context_text = "\n---\n".join(similar_contexts)
        prompt = f"""
You are a GitHub bot. Summarize the PR below and suggest appropriate labels.
Context from similar past PRs:
{context_text}
---
New PR:
{pr_text}
"""
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

# This file has been moved to agents/llm_agent.py. Please update imports accordingly.
