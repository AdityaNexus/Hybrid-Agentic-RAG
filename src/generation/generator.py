from collections.abc import Iterator
from src.context.models import BuiltContext
from src.generation.llm import generate, generate_stream
from src.generation.prompts import SYSTEM_PROMPT, build_generation_prompt



def answer(
        context: BuiltContext,
        *,
        max_tokens: int | None = 512,
)->str:
    prompt = build_generation_prompt(context)

    return generate(
        prompt,
        system_prompt=SYSTEM_PROMPT,
        temperature=0.0,
        max_tokens=max_tokens,
    )


def answer_stream(
    context: BuiltContext,
    *,
    max_tokens: int = 512,
) -> Iterator[str]:

    prompt = build_generation_prompt(context)

    yield from generate_stream(
        prompt,
        system_prompt=SYSTEM_PROMPT,
        temperature=0.0,
        max_tokens=max_tokens,
    )