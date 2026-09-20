from dataclasses import dataclass, field
from typing import Any


@dataclass(slots=True)
class ContextItem:
    text: str
    source: str
    score: float
    retrieval_method: str
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(slots=True)
class BuiltContext:
    query: str
    evidence: list[ContextItem]
    history: list[str]
    total_tokens: int