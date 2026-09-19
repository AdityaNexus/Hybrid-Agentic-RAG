from src.storage.cache import AnswerCache
from src.storage.knowledge_version import get_knowledge_version
from src.storage.document_registry import DocumentRegistry


class CacheManager:
    def __init__(
        self,
        cache: AnswerCache,
        registry: DocumentRegistry,
    ) -> None:
        self.cache = cache
        self.registry = registry

    def get(
        self,
        query: str,
    ) -> str | None:

        knowledge_version = get_knowledge_version(
            self.registry
        )

        cached = self.cache.get(
            query,
            knowledge_version,
        )

        if cached is None:
            return None

        return cached.answer

    def put(
        self,
        query: str,
        answer: str,
    ) -> None:

        knowledge_version = get_knowledge_version(
            self.registry
        )

        self.cache.put(
            query=query,
            answer=answer,
            knowledge_version=knowledge_version,
        )