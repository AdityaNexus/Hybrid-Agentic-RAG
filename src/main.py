from src.ingestion.ingest import ingest
from src.retrieval.embeddings import EmbeddingModel
from src.retrieval.vector_retriever import VectorRetriever
from src.storage.chroma_store import ChromaStore
from src.storage.document_registry import DocumentRegistry
from src.storage.indexer import ChromaIndexer
from src.graph.graph_indexer import GraphIndexer
from src.graph.graph_store import GraphStore
graph_store = GraphStore()
graph_indexer = GraphIndexer(graph_store)

def main() -> None:
    source = "data/documents/AdityaResume.pdf"

    registry = DocumentRegistry()

    result = ingest(
        source,
        registry,
    )

    if result is None:
        print("Document already indexed. Skipping ingestion.")
        return

    print(
        f"Document: {result.document.title}"
    )

    print(
        f"Chunks: {len(result.chunks)}"
    )

    embedding_model = EmbeddingModel()

    store = ChromaStore()

    indexer = ChromaIndexer(
        embedding_model,
        store,
    )

    print("Indexing...")

    print("Buiding Graph...")
    graph_indexer.index_document(
        result.document,
        result.chunks,
    )
    graph_store.close()
    
    indexer.index_chunks(
        result.chunks
    )

    print(
        f"Chroma count: {store.count()}"
    )


if __name__ == "__main__":
    main()