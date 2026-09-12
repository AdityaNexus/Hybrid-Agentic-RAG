from dataclasses import dataclass , field
from typing import Any

@dataclass(slots=True)
class DocumentSection:
    section_id: str
    title: str |None
    text: str
    page_number: int |None = None
    metadata: dict[str, Any]  = field(default_factory=dict)

@dataclass(slots=True)
class DocumentTable:
    table_id: str
    content: str
    page_number: int | None = None
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(slots=True)
class CanonicalDocument:
    document_id: str
    source: str
    source_type: str
    title: str | None
    content_hash: str

    sections: list[DocumentSection] = field(default_factory=list)
    tables: list[DocumentTable] = field(default_factory=list)

    metadata: dict[str, Any] = field(default_factory=dict)

    def full_text(self)->str:
        return"\n\n".join(
            section.text 
            for section in self.sections
            if section.text.strip()
        )