from src.context.budget import estimate_tokens
from src.context.models import BuiltContext
from src.context.memory import ConversationMessage


def select_history(
    messages: list[ConversationMessage],
    *,
    max_tokens: int,
) -> list[str]:

    selected: list[str] = []
    used_tokens = 0

    for message in reversed(messages):
        text = f"{message.role}: {message.content}"
        tokens = estimate_tokens(text)

        if used_tokens + tokens > max_tokens:
            break

        selected.insert(0, text)
        used_tokens += tokens

    return selected