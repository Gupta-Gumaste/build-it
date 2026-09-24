"""Single entry point for all AI calls. Swapping providers means editing this file only."""

import logging
from dataclasses import dataclass

from app.core.config import settings

logger = logging.getLogger("llm")


@dataclass
class LLMResponse:
    text: str
    input_tokens: int
    output_tokens: int
    provider: str
    model: str


def generate(system: str, messages: list[dict[str, str]]) -> LLMResponse:
    """Send `system` + `messages` ([{role, content}, ...]) to the configured provider.

    Returns the raw text response and token usage. Callers are responsible for
    parsing/validating the text (e.g. as JSON or as CadQuery code).
    """
    provider = settings.ai_provider
    if provider == "anthropic":
        response = _generate_anthropic(system, messages)
    elif provider == "gemini":
        response = _generate_gemini(system, messages)
    else:
        raise ValueError(f"Unknown AI provider: {provider!r}")

    logger.info(
        "llm_call provider=%s model=%s input_tokens=%d output_tokens=%d",
        response.provider,
        response.model,
        response.input_tokens,
        response.output_tokens,
    )
    return response


def _generate_anthropic(system: str, messages: list[dict[str, str]]) -> LLMResponse:
    import anthropic

    client = anthropic.Anthropic(api_key=settings.anthropic_api_key)
    model = settings.anthropic_model
    resp = client.messages.create(
        model=model,
        max_tokens=4096,
        system=system,
        messages=messages,
    )
    text = "".join(block.text for block in resp.content if block.type == "text")
    return LLMResponse(
        text=text,
        input_tokens=resp.usage.input_tokens,
        output_tokens=resp.usage.output_tokens,
        provider="anthropic",
        model=model,
    )


def _generate_gemini(system: str, messages: list[dict[str, str]]) -> LLMResponse:
    from google import genai
    from google.genai import types

    client = genai.Client(api_key=settings.gemini_api_key)
    model = settings.gemini_model

    contents = [
        types.Content(role=_gemini_role(m["role"]), parts=[types.Part.from_text(text=m["content"])])
        for m in messages
    ]
    resp = client.models.generate_content(
        model=model,
        contents=contents,
        config=types.GenerateContentConfig(system_instruction=system),
    )
    usage = resp.usage_metadata
    return LLMResponse(
        text=resp.text or "",
        input_tokens=usage.prompt_token_count if usage else 0,
        output_tokens=usage.candidates_token_count if usage else 0,
        provider="gemini",
        model=model,
    )


def _gemini_role(role: str) -> str:
    return "model" if role == "assistant" else "user"
