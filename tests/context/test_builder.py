from src.context.builder import ContextBuilder
from src.retrieval.evidence import Evidence

def make_evidence(
        text:str,
        score:float,

)->Evidence:
    return Evidence(
        evidence_id = text,
        text = text,
        score = score,
        source = "test",
        retrieval_method = "vector",
    )

def test_context_builder():
    evidence = [
        make_evidence(
            "Employee recieve 20 days of annual leave",
            0.9,
        ),
        make_evidence(
            "Leave requires manager approval",
            0.8,
        ),
    ]

    builder = ContextBuilder(max_tokens=100)

    context = builder.build(
        "What is the leave policy?",
        evidence,
    )

    assert context.query == "What is the leave policy?"
    assert len(context.evidence) == 2
    assert context.total_tokens > 0


def test_duplicate_evidence_removed():
    evidence = [
        make_evidence("Employees receive 20 days leave.", 0.9),
        make_evidence("Employees receive 20 days leave.", 0.8),
    ]

    builder = ContextBuilder()

    context = builder.build(
        "How much leave?",
        evidence,
    )

    assert len(context.evidence) == 1


def test_context_budget():
    evidence = [
        make_evidence(
            "word " * 100,
            0.9,
        ),
    ]

    builder = ContextBuilder(max_tokens=20)

    context = builder.build(
        "test",
        evidence,
    )

    assert len(context.evidence) == 0