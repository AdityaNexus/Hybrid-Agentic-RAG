from pathlib import Path
from urllib.parse import urlparse

from docling.document_converter import DocumentConverter

from src.ingestion.fingerprint import calculate_file_hash
from src.ingestion.models import (
    CanonicalDocument,
    DocumentSection,
)


_converter = DocumentConverter()


def _source_type(source: str) -> str:
    if source.startswith(("http://", "https://")):
        return "url"

    return Path(source).suffix.lower().lstrip(".")


def _document_id(source: str, content_hash: str) -> str:
    return content_hash


def parse_source(source: str) -> CanonicalDocument:
    if not source:
        raise ValueError("Source cannot be empty.")

    is_url = source.startswith(("http://", "https://"))

    if not is_url:
        path = Path(source)

        if not path.exists():
            raise FileNotFoundError(source)

        if not path.is_file():
            raise ValueError(f"Not a file: {source}")

        content_hash = calculate_file_hash(path)
        source_name = path.name

    else:
        parsed = urlparse(source)

        if parsed.scheme not in {"http", "https"}:
            raise ValueError("Only HTTP and HTTPS URLs are supported.")

        if not parsed.netloc:
            raise ValueError("Invalid URL.")

        # URL content hash will be established after conversion.
        content_hash = source
        source_name = parsed.netloc

    result = _converter.convert(
        source,
        raises_on_error=True,
        max_num_pages=500,
        max_file_size=50 * 1024 * 1024,
    )

    document = result.document

    markdown = document.export_to_markdown()

    sections = []

    if markdown.strip():
        sections.append(
            DocumentSection(
                section_id="section_0",
                title=None,
                text=markdown.strip(),
            )
        )

    return CanonicalDocument(
        document_id=_document_id(source, content_hash),
        source=source,
        source_type=_source_type(source),
        title=source_name,
        content_hash=content_hash,
        sections=sections,
        metadata={
            "source": source,
            "source_type": _source_type(source),
        },
    )