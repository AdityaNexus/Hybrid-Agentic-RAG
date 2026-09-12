from src.ingestion.chunker import chunk_document
from src.ingestion.models import (
    CanonicalDocument,
    DocumentSection,
)


def create_test_document() -> CanonicalDocument:
    return CanonicalDocument(
        document_id="doc_test",
        source="test.md",
        source_type="md",
        title="Test",
        content_hash="hash_test",
        sections=[
            DocumentSection(
                section_id="section_1",
                title="Introduction",
                text=(
                    "Agentic RAG combines retrieval and generation. "
                    "Vector search finds semantically similar information. "
                    "Graph retrieval finds relationships between entities."
                ),
            )
        ],
    )


def test_document_is_chunked():
    document = create_test_document()

    chunks = chunk_document(
        document,
        max_tokens=10,
        overlap_tokens=2,
    )

    assert chunks
    assert len(chunks) > 1


def test_chunk_metadata():
    document = create_test_document()

    chunks = chunk_document(
        document,
        max_tokens=20,
        overlap_tokens=2,
    )

    chunk = chunks[0]

    assert chunk.document_id == "doc_test"
    assert chunk.chunk_id
    assert chunk.text
    assert chunk.chunk_index == 0


def test_invalid_chunk_size():
    document = create_test_document()

    try:
        chunk_document(
            document,
            max_tokens=10,
            overlap_tokens=10,
        )
    except ValueError:
        pass
    else:
        raise AssertionError("Expected ValueError")