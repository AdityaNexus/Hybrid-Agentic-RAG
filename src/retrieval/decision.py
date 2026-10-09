from dataclasses import dataclass
from src.retrieval.evidence import Evidence 


@dataclass(slots=True)
class RetrievalDecision:
    evidence : list[Evidence]
    confidence : float 
    needs_fallback : bool 