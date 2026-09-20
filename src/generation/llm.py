from collections.abc import Iterator
import logging

from openai import OpenAI

from src.config.settings import settings


client = OpenAI(
    base_url=settings.llm_base_url,
    api_key=settings.llm_api_key,
    timeout=None,
    max_retries=0,
)

logger = logging.getLogger(__name__)


def generate(
    prompt: str,
    *,
    system_prompt: str | None = None,
    temperature: float = 0.0,
    max_tokens: int = 256,
) -> str:

    logger.info("Sending LLM request: max_tokens=%s", max_tokens)

    messages = []

    if system_prompt:
        messages.append(
            {
                "role": "system",
                "content": system_prompt,
            }
        )

    messages.append(
        {
            "role": "user",
            "content": prompt,
        }
    )

    response = client.chat.completions.create(
        model=settings.llm_model,
        messages=messages,
        temperature=temperature,
        max_tokens=max_tokens,
        extra_body={
            "chat_template_kwargs": {
                "enable_thinking": settings.llm_enable_thinking,
            }
        },
    )

    content = response.choices[0].message.content or ""
    logger.info("LLM response received: characters=%s", len(content))
    return content


def generate_stream(
    prompt: str,
    *,
    system_prompt: str | None = None,
    temperature: float = 0.0,
    max_tokens: int = 256,
) -> Iterator[str]:

    messages = []

    if system_prompt:
        messages.append(
            {
                "role": "system",
                "content": system_prompt,
            }
        )

    messages.append(
        {
            "role": "user",
            "content": prompt,
        }
    )

    stream = client.chat.completions.create(
        model=settings.llm_model,
        messages=messages,
        temperature=temperature,
        max_tokens=max_tokens,
        stream=True,
        extra_body={
            "chat_template_kwargs": {
                "enable_thinking": settings.llm_enable_thinking,
            }
        },
    )

    for chunk in stream:
        content = chunk.choices[0].delta.content

        if content:
            yield content