from pathlib import Path

from docling.document_converter import DocumentConverter

from src.ingestion.fingerprint import calculate_file_hash
from src.ingestion.models import (
    CanonicalDocument,
    DocumentSection,
    DocumentTable,
)


_converter = DocumentConverter()


def parse_file(path: str | Path) -> CanonicalDocument:
    path = Path(path).resolve()

    if not path.exists():
        raise FileNotFoundError(path)

    content_hash = calculate_file_hash(path)

    result = _converter.convert(path)

    document = result.document

    sections: list[DocumentSection] = []
    tables: list[DocumentTable] = []

    section_index = 0

    for item, _level in document.iterate_items():
        item_type = type(item).__name__

        if item_type == "TextItem":
            text = item.text.strip()

            if not text:
                continue

            sections.append(
                DocumentSection(
                    section_id=f"section_{section_index}",
                    title=None,
                    text=text,
                )
            )

            section_index += 1

        elif item_type == "TableItem":
            tables.append(
                DocumentTable(
                    table_id=f"table_{len(tables)}",
                    content=item.export_to_markdown(),
                )
            )

    return CanonicalDocument(
        document_id=content_hash,
        source=str(path),
        source_type=path.suffix.lower().lstrip("."),
        title=path.stem,
        content_hash=content_hash,
        sections=sections,
        tables=tables,
        metadata={
            "filename": path.name,
            "extension": path.suffix.lower(),
        },
    )