from functools import lru_cache
from typing import Sequence

from groq import Groq

from config import LLM_MODEL, LLM_PROVIDER, can_use_groq, require_groq_api_key


@lru_cache(maxsize=1)
def _client() -> Groq:
    """Return a cached Groq client instance."""

    if not can_use_groq():
        raise RuntimeError("Groq provider is disabled; set LLM_PROVIDER=groq and GROQ_API_KEY to enable it.")

    return Groq(api_key=require_groq_api_key())


def chat_completion(
    messages: Sequence[dict[str, str]],
    *,
    model: str | None = None,
    temperature: float = 0.2,
    max_tokens: int = 800,
) -> str:
    """Call the Groq Chat Completions API and return the text content."""

    if LLM_PROVIDER != "groq":
        raise RuntimeError("LLM provider is set to local; Groq completions are disabled.")

    response = _client().chat.completions.create(
        model=model or LLM_MODEL,
        messages=[{"role": m["role"], "content": m["content"]} for m in messages],
        temperature=temperature,
        max_tokens=max_tokens,
    )

    choice = response.choices[0]
    content = choice.message.content or ""
    return content.strip()
