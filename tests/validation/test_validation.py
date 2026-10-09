from src.context.models import BuiltContext, ContextItem
from src.validation.validator import validate_answer


def test_valid_answer():
    context = BuiltContext(
        query="How much leave?",
        evidence=[
            ContextItem(
                text="Employees receive 20 days of leave.",
                source="test.pdf",
                score=0.9,
                retrieval_method="vector",
            )
        ],
        history=[],
        total_tokens=10,
    )

    result = validate_answer(
        "Employees receive 20 days of leave. [Evidence 1]",
        context,
    )

    assert result.valid


def test_missing_citation():
    context = BuiltContext(
        query="How much leave?",
        evidence=[
            ContextItem(
                text="Employees receive 20 days of leave.",
                source="test.pdf",
                score=0.9,
                retrieval_method="vector",
            )
        ],
        history=[],
        total_tokens=10,
    )

    result = validate_answer(
        "Employees receive 20 days of leave.",
        context,
    )

    assert not result.valid


def test_invalid_citation():
    context = BuiltContext(
        query="How much leave?",
        evidence=[
            ContextItem(
                text="Employees receive 20 days of leave.",
                source="test.pdf",
                score=0.9,
                retrieval_method="vector",
            )
        ],
        history=[],
        total_tokens=10,
    )

    result = validate_answer(
        "Employees receive 20 days. [Evidence 5]",
        context,
    )

    assert not result.valid