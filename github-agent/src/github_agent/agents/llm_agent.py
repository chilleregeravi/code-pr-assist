import logging
from typing import List

from github_agent.config import OPENAI_API_KEY, OPENAI_MODEL
from openai import APIError, APITimeoutError, OpenAI, OpenAIError, RateLimitError
from opentelemetry import trace

logger = logging.getLogger(__name__)
tracer = trace.get_tracer(__name__)


class LLMAgent:
    def __init__(self) -> None:
        """Initialize the LLM agent with OpenAI client."""
        self.client = OpenAI(
            api_key=OPENAI_API_KEY,
            timeout=60.0,  # 60 second timeout
        )

    def summarize_with_context(self, pr_text: str, similar_contexts: List[str]) -> str:
        with tracer.start_as_current_span("LLMAgent.summarize_with_context") as span:
            span.set_attribute("text.length", len(pr_text))
            span.set_attribute("similar_bodies.count", len(similar_contexts))

            """Summarize PR and suggest labels using OpenAI GPT with context."""
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
                response = self.client.chat.completions.create(
                    model=OPENAI_MODEL,
                    messages=[
                        {"role": "system", "content": "You assist with GitHub PR reviews."},
                        {"role": "user", "content": prompt},
                    ],
                    timeout=60.0,  # Request-specific timeout
                )
                content = response.choices[0].message.content
                if content is None:
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
                logger.error(f"Unexpected error: {e}")
                return "[Error: Could not generate summary.]"
