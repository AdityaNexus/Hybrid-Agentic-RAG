from src.retrieval.evidence import Evidence

from src.retrieval.config import (
    MAX_EVIDENCE,
    VECTOR_MIN_SCORE,
)

def calculate_confidence(
        evidence : list[Evidence]
)->float:

    if not evidence:
        return 0.0

    scores = [max(0.0, min(1.0,item.score))
              for item in evidence]

    scores.sort(reverse=True)

    if len(scores)==1:
        return scores[0]

    return (
        scores[0]*0.6
        +scores[1]*0.3
        + (
            sum(scores[2:])/len(scores[2:])
            if len(scores)>2 else 0.0
        )*0.1
    )

def needs_fallback(
        evidence : list[Evidence],

)->bool:
    if not evidence:
        return True 

    strongest = max(
        item.score
        for item in evidence
    )

    return strongest <VECTOR_MIN_SCORE