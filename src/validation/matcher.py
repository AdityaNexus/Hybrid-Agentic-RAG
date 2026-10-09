import re

from src.context.models import BuiltContext
from src.validation.models import ClaimResult


def _words(text: str) -> set[str]:
    return set(
        re.findall(
            r"\b[a-zA-Z0-9-]+\b",
            text.lower(),
        )
    )


def match_claim(
    claim: str,
    context: BuiltContext,
) -> ClaimResult:

    claim_words = _words(claim)

    best_overlap = 0.0
    best_evidence: list[int] = []

    for index, evidence in enumerate(
        context.evidence,
        start=1,
    ):
        evidence_words = _words(evidence.text)

        if not claim_words:
            continue

        overlap = len(
            claim_words & evidence_words
        ) / len(claim_words)

        if overlap > best_overlap:
            best_overlap = overlap
            best_evidence = [index]

    return ClaimResult(
        claim=claim,
        supported=best_overlap >= 0.5,
        evidence_ids=best_evidence,
    )