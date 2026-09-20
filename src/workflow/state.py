from typing import TypedDict

from src.query.models import ProcessedQuery, QueryRoute
from src.retrieval.decision import RetrievalDecision
from src.context.models import BuiltContext
from src.validation.models import ValidationResult
from src.context.memory import ConversationMemory

class RAGState(TypedDict, total=False):
    query: str
    processed_query: ProcessedQuery
    route: QueryRoute

    retrieval: RetrievalDecision
    context: BuiltContext

    answer: str
    validation: ValidationResult
    memory: ConversationMemory
    cache_hit: bool
    retry_count: int