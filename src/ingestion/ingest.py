from dataclasses import dataclass

from src.ingestion.chunker import chunk_document
from src.ingestion.chunks import DocumentChunk
from src.ingestion.parser import parse_source
from src.ingestion.router import detect_source
from src.ingestion.models import CanonicalDocument
from src.ingestion.source_identity import get_source_fingerprint
from src.storage.document_registry import DocumentRegistry, DocumentRecord
@dataclass(slots=True)
class IngestionResult:
    document: CanonicalDocument
    chunks: list[DocumentChunk]
    skipped : bool


def ingest(source:str,registry : DocumentRegistry)->IngestionResult |None:

    source_type, fingerprint = get_source_fingerprint(
        source
    )

    existing = registry.get(source)

    if (
        existing is not None
        and existing.content_hash == fingerprint
    ):
        return None

    document = parse_source(source)

    chunks = chunk_document(document)

    registry.upsert(
        record=DocumentRecord(
            source=source,
            source_type=source_type,
            content_hash=fingerprint,
            document_id=document.document_id,
        )
    )

    return IngestionResult(
        document=document,
        chunks=chunks,
        skipped=False,
    )