from dataclasses import dataclass, field
from enum import Enum


class QueryRoute(str, Enum):
    VECTOR = "vector"
    GRAPH = "graph"
    HYBRID = "hybrid"
    WEB = "web"


@dataclass(slots=True)
class ProcessedQuery:
    original: str
    normalized: str
    keywords: list[str] = field(default_factory=list)
    entities: list[str] = field(default_factory=list)
    temporal: bool = False