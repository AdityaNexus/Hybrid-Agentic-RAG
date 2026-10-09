from src.context.models import BuiltContext, ContextItem
from src.validation.validator import validate_answer


def test_supported_claim():

    context = BuiltContext(
        query="How much leave?",
        evidence=[
            ContextItem(
                text="Employees receive 20 days of annual leave.",
                source="test.pdf",
                score=0.9,
                retrieval_method="vector",
            )
        ],
        history=[],
        total_tokens=20,
    )

    result = validate_answer(
        "Employees receive 20 days of annual leave. [Evidence 1]",
        context,
    )

    assert result.valid


def test_unsupported_claim():

    context = BuiltContext(
        query="How much leave?",
        evidence=[
            ContextItem(
                text="Employees receive 20 days of annual leave.",
                source="test.pdf",
                score=0.9,
                retrieval_method="vector",
            )
        ],
        history=[],
        total_tokens=20,
    )

    result = validate_answer(
        "Employees receive 20 days of annual leave. "
        "Employees can carry over 10 days.",
        "[Evidence 1]",
        context,
    )

    assert not result.valid