from pathlib import Path

from src.config.settings import settings
from src.graph.graph_indexer import GraphIndexer
from src.ingestion.ingest import ingest
from src.retrieval.embeddings import EmbeddingModel
from src.storage.chroma_store import ChromaStore
from src.storage.document_registry import DocumentRegistry
from src.graph.graph_store import GraphStore
from src.storage.indexer import ChromaIndexer
from src.workflow.components import WorkflowComponents
from src.workflow.graph import build_graph


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


def index_documents() -> None:
    embedding_model = EmbeddingModel()
    index_documents_with_model(embedding_model)


def index_documents_with_model(
    embedding_model: EmbeddingModel,
) -> None:
    chroma_store = ChromaStore()
    graph_store = GraphStore()
    registry = DocumentRegistry()
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

                chroma_indexer.index_chunks(result.chunks)
                graph_indexer.index_document(
                    result.document,
                    result.chunks,
                )
                print(f"Successfully indexed: {source_path.name}")
            except Exception as e:
                print(f"Error indexing {source_path.name}: {e}")
                continue
    finally:
        graph_store.close()
        registry.close()