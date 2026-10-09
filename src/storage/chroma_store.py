from pathlib import Path
from typing import Any
import chromadb
class ChromaStore:
    def __init__(
            self,
            persist_directory: str = "data/chroma",
            collection_name : str = "documents",
    )->None:
        Path(persist_directory).mkdir(parents=True,exist_ok=True)

        self.client = chromadb.PersistentClient(path=persist_directory)
        self.collection = self.client.get_or_create_collection(
            name=collection_name,
            metadata={"hnsw:space":"cosine"},
        )

    def upsert(
            self,
            ids: list[str],
            documents : list[str],
            embeddings: list[list[float]],
            metadatas: list[dict[str, Any]],

    )->None:
        if not ids:
            return

        if not (
            len(ids)==len(documents)==len(embeddings)==len(metadatas)
        ):
            raise ValueError(
                "Length of ids, documents, embeddings, and metadatas must be the same."
            )

        self.collection.upsert(
            ids = ids,
            documents = documents,
            embeddings = embeddings,
            metadatas = metadatas,

        )

    def count(self)->int:
        return self.collection.count()

    def search(
            self,
            query_embedding:list[float],
            *,
            top_k : int = 5,
    )->dict:
        if top_k <=0:
            raise ValueError("top_k must be a positive integer.")

        return self.collection.query(
            query_embeddings = [query_embedding],
            n_results = top_k,
            include = [
                "documents",
                "metadatas",
                "distances",
            ]
        )

    def delete_by_document(
        self,
        document_id: str,
    ) -> None:
        self.collection.delete(
            where={
                "document_id": document_id,
            }
        )