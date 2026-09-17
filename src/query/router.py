import re

from src.query.models import ProcessedQuery, QueryRoute


GRAPH_PATTERNS = [
    r"\bwho\b",
    r"\brelationship\b",
    r"\bconnected to\b",
    r"\bworks at\b",
    r"\bdeveloped by\b",
    r"\bcreated by\b",
    r"\bbelongs to\b",
    r"\bdepends on\b",
]


def route_query(query: ProcessedQuery) -> QueryRoute:
    text = query.normalized

    has_graph_signal = any(
        re.search(pattern, text)
        for pattern in GRAPH_PATTERNS
    )

    if query.temporal and has_graph_signal:
        return QueryRoute.HYBRID

    if query.temporal:
        return QueryRoute.WEB

    if has_graph_signal:
        return QueryRoute.GRAPH

    return QueryRoute.VECTOR