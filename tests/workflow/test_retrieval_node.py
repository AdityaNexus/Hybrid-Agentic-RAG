from src.retrieval.decision import RetrievalDecision
from src.retrieval.evidence import Evidence
from src.workflow.graph import build_graph


class FakeRetriever:

    def retrieve(self, query, route):

        return RetrievalDecision(
            evidence=[
                Evidence(
                    evidence_id="test-1",
                    text="LangGraph is a framework for building stateful workflows.",
                    score=0.9,
                    source="test",
                    retrieval_method="vector",
                )
            ],
            confidence=0.9,
            needs_fallback=False,
        )


def test_retrieval_node():

    workflow = build_graph(
        FakeRetriever()
    )

    result = workflow.invoke(
        {
            "query": "What is LangGraph?"
        }
    )

    assert "retrieval" in result

    assert len(
        result["retrieval"].evidence
    ) == 1