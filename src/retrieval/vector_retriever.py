from dataclasses import dataclass
from typing import Any

from src.retrieval.embeddings import EmbeddingModel
from src.storage.chroma_store import ChromaStore


@dataclass(slots=True)
class RetrievedChunk:
    chunk_id: str
    text: str
    score: float
    metadata: dict[str, Any]


class VectorRetriever:
    def __init__(
        self,
        embedding_model: EmbeddingModel,
        store: ChromaStore,
    ) -> None:
        self.embedding_model = embedding_model
        self.store = store

    def search(
        self,
        query: str,
        *,
        top_k: int = 5,
    ) -> list[RetrievedChunk]:

        query_embedding = self.embedding_model.embed_query(query)

        result = self.store.search(
            query_embedding,
            top_k=top_k,
        )

        documents = result["documents"][0]
        ids = result["ids"][0]
        metadatas = result["metadatas"][0]
        distances = result["distances"][0]

        retrieved = []

        for chunk_id, text, metadata, distance in zip(
            ids,
            documents,
            metadatas,
            distances,
        ):
            retrieved.append(
                RetrievedChunk(
                    chunk_id=chunk_id,
                    text=text,
                    score=1.0 - distance,
                    metadata=metadata,
                )
            )

        return retrieved