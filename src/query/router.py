import re

from src.query.models import ProcessedQuery, QueryRoute

GRAPH_PROTOTYPES = [
    "Who works at the company?",
    "What is the relationship between this and that?",
    "Who developed this software?",
    "What components does this depend on?",
    "Who is connected to this person?",
]

VECTOR_PROTOTYPES = [
    "What is the policy for vacation?",
    "Explain the architecture of the system.",
    "How do I install the software?",
    "What are the benefits?",
    "Summarize the document.",
]

def cosine_similarity(a: list[float], b: list[float]) -> float:
    dot = sum(x * y for x, y in zip(a, b))
    norm_a = sum(x * x for x in a) ** 0.5
    norm_b = sum(x * x for x in b) ** 0.5
    return dot / (norm_a * norm_b) if norm_a and norm_b else 0.0

_PROTOTYPE_EMBEDDINGS = None

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


def route_query(
    query: ProcessedQuery,
    embedding_model=None,
) -> QueryRoute:
    global _PROTOTYPE_EMBEDDINGS

    has_graph_signal = any(
        re.search(pattern, query.normalized)
        for pattern in GRAPH_PATTERNS
    )

    if query.temporal:
        return QueryRoute.HYBRID if has_graph_signal else QueryRoute.WEB

    if embedding_model is None:
        return QueryRoute.GRAPH if has_graph_signal else QueryRoute.VECTOR

    if _PROTOTYPE_EMBEDDINGS is None:
        _PROTOTYPE_EMBEDDINGS = {
            "graph": embedding_model.embed_documents(GRAPH_PROTOTYPES),
            "vector": embedding_model.embed_documents(VECTOR_PROTOTYPES),
        }
    
    query_emb = embedding_model.embed_query(query.normalized)
    
    max_graph_sim = max(cosine_similarity(query_emb, p_emb) for p_emb in _PROTOTYPE_EMBEDDINGS["graph"])
    max_vector_sim = max(cosine_similarity(query_emb, p_emb) for p_emb in _PROTOTYPE_EMBEDDINGS["vector"])
    
    if max_graph_sim > max_vector_sim and max_graph_sim > 0.6:
        return QueryRoute.GRAPH

    if has_graph_signal and max_graph_sim >= max_vector_sim * 0.9:
        return QueryRoute.GRAPH

    return QueryRoute.VECTOR