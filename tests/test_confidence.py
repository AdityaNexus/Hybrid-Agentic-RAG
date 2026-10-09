from src.retrieval.confidence import (
    calculate_confidence,
    needs_fallback,
)
from src.retrieval.evidence import Evidence


def make_evidence(score: float) -> Evidence:
    return Evidence(
        evidence_id=str(score),
        text="test",
        score=score,
        source="test",
        retrieval_method="vector",
    )


def test_strong_evidence():
    evidence = [
        make_evidence(0.9),
        make_evidence(0.8),
    ]

    confidence = calculate_confidence(evidence)

    assert confidence > 0.7
    assert not needs_fallback(evidence)


def test_weak_evidence():
    evidence = [
        make_evidence(0.2),
        make_evidence(0.1),
    ]

    assert needs_fallback(evidence)


def test_empty_evidence():
    assert calculate_confidence([]) == 0.0
    assert needs_fallback([])