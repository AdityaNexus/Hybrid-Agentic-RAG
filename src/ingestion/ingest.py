from dataclasses import dataclass

from src.ingestion.chunker import chunk_document
from src.ingestion.chunks import DocumentChunk
from src.ingestion.parser import parse_file
from src.ingestion.router import detect_source
from src.ingestion.models import CanonicalDocument

@dataclass(slots=True)
class IngestionResult:
    document: CanonicalDocument
    chunks: list[DocumentChunk]


def ingest(source: str) -> IngestionResult:
    source_type = detect_source(source)

    if source_type == "url":
        raise NotImplementedError(
            "URL ingestion is coming next."
        )

    document = parse_file(source)

    chunks = chunk_document(document)

    return IngestionResult(
        document=document,
        chunks=chunks,
    )