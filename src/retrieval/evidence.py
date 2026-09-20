from dataclasses import dataclass, field
from typing import Any 

@dataclass(slots=True)
class Evidence:
    evidence_id : str 
    text : str 
    score:float 
    source:str 
    retrieval_method : str 
    metadata: dict[str, Any] = field(default_factory=dict)