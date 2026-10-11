
import logging

import httpx
from claude_agent_sdk import AssistantMessage, ClaudeAgentOptions, TextBlock, query

from backend.app.core.config import settings

logger = logging.getLogger(__name__)


class LLMServiceError(Exception):
    pass


async def generate_local(prompt: str) -> str:
    url = f"{settings.ollama_base_url}/api/chat"
    payload = {
        "model": settings.ollama_model,
        "messages": [{"role": "user", "content": prompt}],
        "stream": False,
    }

    try:
        async with httpx.AsyncClient(timeout=120.0) as client:
            response = await client.post(url, json=payload)
            response.raise_for_status()
            data = response.json()
            content = data.get("message", {}).get("content", "").strip()

            if not content:
                raise LLMServiceError("Ollama returned an empty response.")

            return content
    except LLMServiceError:
        raise
    except (httpx.HTTPError, ValueError) as exc:
        logger.exception("Local LLM request failed")
        raise LLMServiceError("Local LLM request failed.") from exc


async def generate_cloud(prompt: str) -> str:
    if not settings.anthropic_api_key:
        raise LLMServiceError(
            "Claude Agent SDK requires ANTHROPIC_API_KEY. "
            "Configure the key to use the cloud provider."
        )

    options = ClaudeAgentOptions(
        system_prompt=(
            "You are Lenny Growth Assistant. "
            "Answer using the supplied podcast transcript evidence. "
            "Follow the instructions and citation rules in the user prompt. "
            "Do not invent sources or unsupported facts."
        ),
        max_turns=1,
        tools=[],
        env={"ANTHROPIC_API_KEY": settings.anthropic_api_key},
    )

    try:
        response_parts = []

        async for message in query(prompt=prompt, options=options):
            if isinstance(message, AssistantMessage):
                for block in message.content:
                    if isinstance(block, TextBlock):
                        response_parts.append(block.text)

        content = "\n".join(response_parts).strip()

        if not content:
            raise LLMServiceError("Claude Agent SDK returned an empty response.")

        return content
    except LLMServiceError:
        raise
    except Exception as exc:
        logger.exception("Claude Agent SDK request failed")
        raise LLMServiceError("Claude Agent SDK request failed.") from exc


async def generate_response(
    prompt: str,
    provider: str | None = None,
) -> str:
    selected_provider = provider or settings.llm_provider

    if selected_provider == "cloud":
        try:
            return await generate_cloud(prompt)
        except LLMServiceError:
            logger.warning(
                "Claude Agent SDK failed; falling back to local Ollama."
            )
            return await generate_local(prompt)

    return await generate_local(prompt)
