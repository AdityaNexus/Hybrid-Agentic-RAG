from src.ingestion.models import CanonicalDocument
from src.graph.graph_store import GraphStore


class GraphIndexer:
    def __init__(self, store: GraphStore) -> None:
        self.store = store

    def index_document(
        self,
        document: CanonicalDocument,
    ) -> None:
        self.store.add_document(
            document_id=document.document_id,
            source=document.source,
            title=document.title,
        )

        for chunk in self._chunks(document):
            self.store.add_chunk(
                chunk_id=chunk[0],
                document_id=document.document_id,
                text=chunk[1],
            )

    def _chunks(
        self,
        document: CanonicalDocument,
    ) -> list[tuple[str, str]]:
        # Temporary bridge until the canonical chunk list
        # is passed directly to the graph indexer.
        result = []

        for section in document.sections:
            result.append(
                (
                    f"{document.document_id}:{section.section_id}",
                    section.text,
                )
            )

        return result