import re
import json
import logging

from openai import APIError
from src.generation.llm import generate
from src.query.models import ProcessedQuery

logger = logging.getLogger(__name__)

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


PREPROCESS_SYSTEM_PROMPT = """
You preprocess search queries for a retrieval system.
Return only one valid JSON object with exactly these fields:
{
  "normalized": "short, clear retrieval query",
  "keywords": ["important", "terms"],
  "entities": ["people, products, organizations, or other named entities"],
  "temporal": false
}
Keep the user's meaning. Do not answer the query. `temporal` is true only when
the query asks about a date or changing/current information.
""".strip()


def preprocess_query(query: str) -> ProcessedQuery:
    original = query
    if not query or not query.strip():
        raise ValueError("Query cannot be empty.")

    normalized = " ".join(
        query.strip().lower().split()
    )

    try:
        response = generate(
            query.strip(),
            system_prompt=PREPROCESS_SYSTEM_PROMPT,
            temperature=0.0,
            max_tokens=128,
        )
        result = _parse_llm_response(response)
        normalized = _clean_text(result.get("normalized")) or normalized
        keywords = _clean_list(result.get("keywords"))
        entities = _clean_list(result.get("entities"))
        temporal = result.get("temporal")
        if not isinstance(temporal, bool):
            raise ValueError("temporal must be a boolean")
        return ProcessedQuery(
            original=original,
            normalized=normalized,
            keywords=keywords,
            entities=entities,
            temporal=temporal,
        )
    except (
        APIError,
        OSError,
        ValueError,
        TypeError,
        json.JSONDecodeError,
        KeyError,
    ) as error:
        logger.warning("LLM query preprocessing failed; using local fallback: %s", error)
        return _fallback_preprocess_query(original, normalized)


def _fallback_preprocess_query(
    original: str,
    normalized: str,
) -> ProcessedQuery:

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

    entities = _extract_entities(original)

    return ProcessedQuery(
        original=original,
        normalized=normalized,
        keywords=keywords,
        entities=entities,
        temporal=temporal,
    )


def _parse_llm_response(response: str) -> dict:
    text = response.strip()
    if text.startswith("```"):
        text = re.sub(r"^```(?:json)?\s*|\s*```$", "", text, flags=re.IGNORECASE)
    try:
        parsed = json.loads(text)
    except json.JSONDecodeError:
        start = text.find("{")
        end = text.rfind("}")
        if start < 0 or end <= start:
            raise
        parsed = json.loads(text[start : end + 1])
    if not isinstance(parsed, dict):
        raise ValueError("preprocessor response must be a JSON object")
    return parsed


def _clean_text(value: object) -> str:
    return value.strip() if isinstance(value, str) else ""


def _clean_list(value: object) -> list[str]:
    if not isinstance(value, list) or not all(isinstance(item, str) for item in value):
        raise TypeError("preprocessor list fields must contain strings")
    return list(dict.fromkeys(item.strip() for item in value if item.strip()))


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