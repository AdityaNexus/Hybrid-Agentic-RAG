from src.graph.extractor import extract_graph
from src.graph.graph_store import GraphStore
from src.ingestion.chunks import DocumentChunk
from src.ingestion.models import CanonicalDocument


class GraphIndexer:
    def __init__(self, store: GraphStore) -> None:
        self.store = store

    def index_document(
        self,
        document: CanonicalDocument,
        chunks: list[DocumentChunk],
    ) -> None:

        self.store.add_document(
            document_id=document.document_id,
            source=document.source,
            title=document.title,
        )

        for chunk in chunks:
            self.store.add_chunk(
                chunk_id=chunk.chunk_id,
                document_id=document.document_id,
                text=chunk.text,
            )

            extraction = extract_graph(chunk.text)

            entity_ids: dict[str, str] = {}

            for entity in extraction.entities:
                entity_id = self._entity_id(
                    entity.name,
                    entity.entity_type,
                )

                entity_ids[entity.name] = entity_id

                self.store.add_entity(
                    entity_id=entity_id,
                    name=entity.name,
                    entity_type=entity.entity_type,
                )

                self.store.add_mention(
                    chunk_id=chunk.chunk_id,
                    entity_id=entity_id,
                )

            for relationship in extraction.relationships:
                source_id = entity_ids.get(relationship.source)
                target_id = entity_ids.get(relationship.target)

                if source_id is None or target_id is None:
                    continue

                self.store.add_relationship(
                    source_id=source_id,
                    relationship=relationship.relationship,
                    target_id=target_id,
                )

    @staticmethod
    def _entity_id(
        name: str,
        entity_type: str,
    ) -> str:
        return f"{entity_type.lower()}:{name.strip().lower()}"