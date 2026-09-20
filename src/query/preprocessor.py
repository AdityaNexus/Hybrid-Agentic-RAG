import re

from src.query.models import ProcessedQuery


STOP_WORDS = {
    "the",
    "is",
    "a",
    "an",
    "of",
    "to",
    "in",
    "on",
    "for",
    "and",
    "or",
    "what",
    "how",
    "why",
    "when",
    "where",
    "who",
    "does",
    "do",
    "did",
}


TEMPORAL_WORDS = {
    "today",
    "currently",
    "current",
    "latest",
    "recent",
    "now",
    "yesterday",
    "tomorrow",
}


def preprocess_query(query: str) -> ProcessedQuery:
    original = query

    normalized = " ".join(
        query.strip().lower().split()
    )

    if not normalized:
        raise ValueError("Query cannot be empty.")

    words = re.findall(
        r"\b[a-zA-Z0-9][a-zA-Z0-9_-]*\b",
        normalized,
    )

    keywords = [
        word
        for word in words
        if word not in STOP_WORDS
    ]

    temporal = any(
        word in TEMPORAL_WORDS
        for word in words
    ) or any(
        re.match(r"^20\d{2}$", word) for word in words
    )

    entities = _extract_entities(query)

    return ProcessedQuery(
        original=original,
        normalized=normalized,
        keywords=keywords,
        entities=entities,
        temporal=temporal,
    )


def _extract_entities(query: str) -> list[str]:
    """
    Lightweight entity candidate extraction.

    Currently detects capitalized multi-word/single-word names.
    This is only a candidate generator, not true NER.
    """

    matches = re.findall(
        r"\b[A-Z][A-Za-z0-9-]*(?:\s+[A-Z][A-Za-z0-9-]*)*\b",
        query,
    )

    return list(dict.fromkeys(matches))