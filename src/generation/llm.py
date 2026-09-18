from collections.abc import Iterator

from openai import OpenAI

from src.config.settings import settings


client = OpenAI(
    base_url=settings.llm_base_url,
    api_key=settings.llm_api_key,
)


def generate(
    prompt: str,
    *,
    system_prompt: str | None = None,
    temperature: float = 0.0,
    max_tokens: int = 256,
) -> str:

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
    )

    return response.choices[0].message.content or ""


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
    )

    for chunk in stream:
        content = chunk.choices[0].delta.content

        if content:
            yield content