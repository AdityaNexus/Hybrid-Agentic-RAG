from dataclasses import dataclass

from src.retrieval.adaptive import AdaptiveRetriever
from src.storage.cache import AnswerCache
from src.storage.cache_manager import CacheManager
from src.storage.document_registry import DocumentRegistry
from src.context.memory import ConversationMemory

@dataclass(slots=True)
class WorkflowComponents:
    adaptive_retriever: AdaptiveRetriever
    cache_manager: CacheManager
    cache: AnswerCache
    memory: ConversationMemory
    registry: DocumentRegistry