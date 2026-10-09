from src.context.models import BuiltContext, ContextItem
from src.generation.regenerator import generate_grounded_answer


def test_grounded_answer(monkeypatch):

    def fake_answer(context):
        return (
            "Employees receive 20 days of annual leave. "
            "[Evidence 1]"
        )

    monkeypatch.setattr(
        "src.generation.regenerator.answer",
        fake_answer,
    )

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

    result, valid = generate_grounded_answer(context)

    assert valid
    assert "20 days" in result