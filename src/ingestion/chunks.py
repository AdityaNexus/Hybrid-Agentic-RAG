from dataclasses import dataclass,field
from typing import Any


@dataclass(slots=True)
class DocumentChunk:
    chunk_id :str
    document_id : str

    text:str

    chunk_index:int

    section_id:str |None = None
    page_number:int |None = None
    token_count:int  = 0

    metadata:dict[str, Any]  = field(default_factory=dict)