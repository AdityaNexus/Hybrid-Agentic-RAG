import re

from src.query.models import QueryRoute


GRAPH_PATTERNS = [
    r"\bwho\b",
    r"\bwhat is related to\b",
    r"\brelationship\b",
    r"\bconnected to\b",
    r"\bworks at\b",
    r"\bdeveloped by\b",
    r"\bcreated by\b",
    r"\bbelongs to\b",
    r"\bdepends on\b",
]

WEB_PATTERNS = [
    r"\btoday\b",
    r"\bcurrently\b",
    r"\blatest\b",
    r"\brecent\b",
    r"\bnews\b",
    r"\bcurrent\b",
    r"\bnow\b",
]


def route_query(query: str) -> QueryRoute:
    query = query.strip().lower()

    if not query:
        raise ValueError("Query cannot be empty.")

    has_graph_signal = any(
        re.search(pattern, query)
        for pattern in GRAPH_PATTERNS
    )

    has_web_signal = any(
        re.search(pattern, query)
        for pattern in WEB_PATTERNS
    )

    if has_web_signal and has_graph_signal:
        return QueryRoute.HYBRID

    if has_web_signal:
        return QueryRoute.WEB

    if has_graph_signal:
        return QueryRoute.GRAPH

    return QueryRoute.VECTOR