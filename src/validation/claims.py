import re


def extract_claims(answer: str) -> list[str]:
    """
    Lightweight claim splitter.

    This is intentionally deterministic.
    """

    text = answer.strip()

    if not text:
        return []

    sentences = re.split(
        r"(?<=[.!?])\s+",
        text,
    )

    claims = []

    for sentence in sentences:
        sentence = sentence.strip()

        if not sentence:
            continue

        # Remove evidence citation markers.
        sentence = re.sub(
            r"\[Evidence\s+\d+\]",
            "",
            sentence,
            flags=re.IGNORECASE,
        ).strip()

        if sentence:
            claims.append(sentence)

    return claims