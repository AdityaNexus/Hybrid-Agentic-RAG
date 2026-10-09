import re
import json
import logging

from src.config.settings import settings
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

logger = logging.getLogger(__name__)

class LLMQueryRouter:
    def route(self, query: ProcessedQuery) -> QueryRoute:
        from src.generation.llm import generate
        
        system_prompt = """
You are a query router. Route the user's query to one of the following retrieval methods:
- "web": For questions about real-world facts, current events, general knowledge outside the company, or temporal information. Use this for questions about external entities (like 'Japan', 'Google', public figures).
- "graph": For internal entity relationships, who works where, organizational lookup, or who/what connects to whom.
- "vector": For general semantic search over internal document passages, policy documents, or summaries.
- "hybrid": For questions requiring both internal document passages and internal entity relationships.

If the query asks about real-world facts, public figures, or external entities, always choose "web".

Return only one valid JSON object with exactly this field:
{
  "route": "web"
}
""".strip()
        
        prompt = f"Query: {query.normalized}\nTemporal: {query.temporal}"
        
        response = generate(
            prompt,
            system_prompt=system_prompt,
            temperature=0.0,
            max_tokens=64,
        )
        
        text = response.strip()
        if text.startswith("```"):
            text = re.sub(r"^```(?:json)?\s*|\s*```$", "", text, flags=re.IGNORECASE)
            
        try:
            parsed = json.loads(text)
            choice = parsed.get("route", "").lower()
            return QueryRoute(choice)
        except (json.JSONDecodeError, ValueError) as error:
            raise RuntimeError(f"Invalid LLM routing response: {text!r}") from error

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

WEB_PATTERNS = [
    r"\b(today|currently|current|latest|recent|now|yesterday|tomorrow)\b",
    r"\b20\d{2}\b",
    r"\broad\s*map\b",
    r"\broadmap\b",
    r"\btrend(s)?\b",
    r"\bforecast(s|ing)?\b",
    r"\bfuture\b",
    r"\boutlook\b",
    r"\bwhat('s| is) new\b",
]


def route_query(
    query: ProcessedQuery,
    embedding_model=None,
    decision_router: LLMQueryRouter | None = None,
) -> QueryRoute:
    global _PROTOTYPE_EMBEDDINGS

    if decision_router is not None:
        try:
            return decision_router.route(query)
        except RuntimeError as error:
            logger.warning("LLM routing failed; using local routing fallback: %s", error)

    has_graph_signal = any(
        re.search(pattern, query.normalized)
        for pattern in GRAPH_PATTERNS
    )

    has_web_signal = query.temporal or any(
        re.search(pattern, query.normalized)
        for pattern in WEB_PATTERNS
    )

    if has_web_signal:
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