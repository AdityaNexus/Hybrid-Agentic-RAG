from src.ingestion.chunks import DocumentChunk
from src.retrieval.embeddings import EmbeddingModel
from src.storage.chroma_store import ChromaStore


class ChromaIndexer:
    def __init__(
        self,
        embedding_model: EmbeddingModel,
        store: ChromaStore,
    ) -> None:
        self.embedding_model = embedding_model
        self.store = store

    def index_chunks(
        self,
        chunks: list[DocumentChunk],
    ) -> None:
        if not chunks:
            return

        texts = [
            chunk.text
            for chunk in chunks
        ]

        embeddings = self.embedding_model.embed_documents(
            texts
        )

        ids = [
            chunk.chunk_id
            for chunk in chunks
        ]

        metadatas = [
            {
                **chunk.metadata,
                "document_id": chunk.document_id,
                "chunk_index": chunk.chunk_index,
                "section_id": chunk.section_id or "",
                "page_number": chunk.page_number or -1,
            }
            for chunk in chunks
        ]

        self.store.upsert(
            ids=ids,
            documents=texts,
            embeddings=embeddings,
            metadatas=metadatas,
        )