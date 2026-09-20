from src.retrieval.decision import RetrievalDecision
from src.retrieval.evidence import Evidence
from src.workflow.graph import build_graph


class FakeRetriever:

    def retrieve(self, query, route):

        return RetrievalDecision(
            evidence=[
                Evidence(
                    evidence_id="1",
                    text="LangGraph is a framework for building stateful workflows.",
                    score=0.9,
                    source="test",
                    retrieval_method="vector",
                )
            ],
            confidence=0.9,
            needs_fallback=False,
        )


def test_validation_node(monkeypatch):

    def fake_answer(context, max_tokens=512):
        return (
            "LangGraph is a framework for "
            "building stateful workflows. [Evidence 1]"
        )

    monkeypatch.setattr(
        "src.workflow.graph.answer",
        fake_answer,
    )

    workflow = build_graph(
        FakeRetriever()
    )

    result = workflow.invoke(
        {
            "query": "What is LangGraph?"
        }
    )

    assert "validation" in result

    assert result["validation"].valid is True



def test_invalid_answer_is_regenerated(monkeypatch):

    answers = iter([
        "LangGraph is a database.",
        "LangGraph is a framework for workflows. [Evidence 1]",
    ])

    def fake_answer(context, max_tokens=512):
        return next(answers)

    monkeypatch.setattr(
        "src.workflow.graph.answer",
        fake_answer,
    )

    def fake_generate(
        prompt,
        system_prompt=None,
        temperature=0.0,
        max_tokens=512,
    ):
        return next(answers)

    monkeypatch.setattr(
        "src.workflow.graph.generate",
        fake_generate,
    )

    workflow = build_graph(
        FakeRetriever()
    )

    result = workflow.invoke(
        {
            "query": "What is LangGraph?"
        }
    )

    assert result["validation"].valid is True
    assert result["retry_count"] == 1