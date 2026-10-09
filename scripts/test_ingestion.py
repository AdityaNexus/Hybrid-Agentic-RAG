from src.graph.graph_store import GraphStore
from src.graph.graph_indexer import GraphIndexer

from src.ingestion.ingest import ingest
from src.retrieval.embeddings import EmbeddingModel

from src.storage.chroma_store import ChromaStore
from src.storage.document_registry import DocumentRegistry
from src.storage.indexer import ChromaIndexer


SOURCE = "data/documents/test_policy.txt"


def main():

    registry = DocumentRegistry()

    result = ingest(
        SOURCE,
        registry,
    )

    if result is None:
        print("Document is already indexed and unchanged.")
        registry.close()
        return

    print("Document parsed.")
    print("Chunks:", len(result.chunks))

    embedding_model = EmbeddingModel()
    chroma_store = ChromaStore()

    chroma_indexer = ChromaIndexer(
        embedding_model,
        chroma_store,
    )

    chroma_indexer.index_chunks(result.chunks)

    graph_store = GraphStore()

    graph_indexer = GraphIndexer(
        graph_store
    )

    graph_indexer.index_document(
        result.document,
        result.chunks,
    )

    print("Chroma documents:", chroma_store.count())
    print("Ingestion complete.")

    graph_store.close()
    registry.close()


if __name__ == "__main__":
    main()