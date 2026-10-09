def estimate_tokens(text: str) -> int:
    if not text.strip():
        return 0

    return max(1, len(text.split()))


def fits_budget(
    current_tokens: int,
    new_text: str,
    max_tokens: int,
) -> bool:
    return (
        current_tokens + estimate_tokens(new_text)
        <= max_tokens
    )
