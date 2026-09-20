from pathlib import Path

from src.config.settings import settings
from src.graph.graph_indexer import GraphIndexer
from src.ingestion.ingest import ingest
from src.retrieval.embeddings import EmbeddingModel
from src.retrieval.adaptive import AdaptiveRetriever
from src.retrieval.graph_retriever import GraphRetriever
from src.retrieval.hybrid_retriever import HybridRetriever
from src.retrieval.vector_retriever import VectorRetriever
from src.retrieval.web_retriever import WebRetriever
from src.context.memory import ConversationMemory
from src.storage.chroma_store import ChromaStore
from src.storage.cache import AnswerCache
from src.storage.cache_manager import CacheManager
from src.storage.document_registry import DocumentRegistry
from src.graph.graph_store import GraphStore
from src.storage.indexer import ChromaIndexer
from src.workflow.components import WorkflowComponents
from src.workflow.graph import build_graph


def create_application() -> "RAGApplication":
    print("Initializing EmbeddingModel...")
    embedding_model = EmbeddingModel()
    # index_documents_with_model(embedding_model) # Removed to prevent blocking startup

    print("Initializing ChromaStore...")
    chroma_store = ChromaStore()
    vector_retriever = VectorRetriever(
        embedding_model,
        chroma_store,
    )

    print("Initializing GraphStore...")
    graph_store = GraphStore()
    graph_retriever = GraphRetriever(graph_store)
    hybrid_retriever = HybridRetriever(
        vector_retriever,
        graph_retriever,
    )
    web_retriever = WebRetriever()
    adaptive_retriever = AdaptiveRetriever(
        hybrid_retriever,
        web_retriever,
    )

    print("Initializing Registries and Memory...")
    registry = DocumentRegistry()
    cache = AnswerCache()
    cache_manager = CacheManager(cache, registry)
    memory = ConversationMemory()
    print("Application Initialization Complete.")

    components = WorkflowComponents(
        adaptive_retriever=adaptive_retriever,
        cache_manager=cache_manager,
        cache=cache,
        registry=registry,
        memory=memory,
    )

    return RAGApplication(components)


class RAGApplication:

    def __init__(
        self,
        components: WorkflowComponents,
    ) -> None:

        self.components = components
        self.workflow = build_graph(
            components
        )

    def ask(
        self,
        query: str,
    ):

        return self.workflow.invoke(
            {
                "query": query,
            }
        )


def index_documents_with_components(
    components: WorkflowComponents,
) -> None:
    embedding_model = components.adaptive_retriever.hybrid_retriever.vector_retriever.embedding_model
    chroma_store = components.adaptive_retriever.hybrid_retriever.vector_retriever.store
    graph_store = components.adaptive_retriever.hybrid_retriever.graph_retriever.store
    registry = components.registry

    chroma_indexer = ChromaIndexer(embedding_model, chroma_store)
    graph_indexer = GraphIndexer(graph_store)

    try:
        for source_path in Path(settings.documents_dir).iterdir():
            if not source_path.is_file():
                continue

            source = source_path.as_posix()
            indexed = chroma_store.collection.get(
                where={"source": source},
                limit=1,
            )
            force_reindex = not indexed["ids"]

            try:
                result = ingest(
                    source,
                    registry,
                    force=force_reindex,
                )

                if result is None:
                    continue

                chroma_store.delete_by_document(result.document.document_id)
                chroma_indexer.index_chunks(result.chunks)
                graph_indexer.index_document(
                    result.document,
                    result.chunks,
                )
                print(f"Successfully indexed: {source_path.name}")
            except Exception as e:
                print(f"Error indexing {source_path.name}: {e}")
                continue
    except Exception as e:
        print(f"Indexing error: {e}")