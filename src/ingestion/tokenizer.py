def estimate_tokens(text: str) -> int:
    """
    Temporary lightweight token estimate.

    We will replace this with the actual tokenizer used by
    the embedding model once the embedding stack is selected.
    """
    if not text.strip():
        return 0

    return max(1, len(text.split()))