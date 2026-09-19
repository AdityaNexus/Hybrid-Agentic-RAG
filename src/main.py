import logging

from src.application import (
    RAGApplication,
    index_documents_with_model,
)
from src.context.memory import ConversationMemory
from src.retrieval.adaptive import AdaptiveRetriever
from src.retrieval.embeddings import EmbeddingModel
from src.retrieval.graph_retriever import GraphRetriever
from src.retrieval.hybrid_retriever import HybridRetriever
from src.retrieval.vector_retriever import VectorRetriever
from src.retrieval.web_retriever import WebRetriever
from src.graph.graph_store import GraphStore
from src.storage.cache import AnswerCache
from src.storage.cache_manager import CacheManager
from src.storage.chroma_store import ChromaStore
from src.storage.document_registry import DocumentRegistry
from src.workflow.components import WorkflowComponents


def create_application():

    embedding_model = EmbeddingModel()

    print("Indexing documents...", flush=True)
    index_documents_with_model(embedding_model)

    chroma_store = ChromaStore()

    vector_retriever = VectorRetriever(
        embedding_model,
        chroma_store,
    )

    graph_store = GraphStore()

    graph_retriever = GraphRetriever(
        graph_store,
    )

    hybrid_retriever = HybridRetriever(
        vector_retriever,
        graph_retriever,
    )

    web_retriever = WebRetriever()

    adaptive_retriever = AdaptiveRetriever(
        hybrid_retriever,
        web_retriever,
    )

    registry = DocumentRegistry()

    cache = AnswerCache()

    cache_manager = CacheManager(
        cache,
        registry,
    )

    memory = ConversationMemory()

    components = WorkflowComponents(
        adaptive_retriever=adaptive_retriever,
        cache_manager=cache_manager,
        cache=cache,
        registry=registry,
        memory=memory,
    )

    return RAGApplication(
        components
    )


def main():
    logging.basicConfig(
        level=logging.INFO,
        format="%(levelname)s %(name)s: %(message)s",
    )

    app = create_application()

    print("Hybrid Agentic RAG")
    print("Type 'exit' to quit.")

    while True:

        query = input("\nYou: ").strip()

        if query.lower() == "exit":
            break

        if not query:
            continue

        try:
            result = app.ask(query)
        except Exception as error:
            print(f"\nRequest failed: {error}")
            continue

        print("\nAssistant:")
        print(result["answer"])

        print("\nCache hit:", result.get("cache_hit"))


if __name__ == "__main__":
    main()