from src.query.models import QueryRoute
from src.workflow.graph import build_graph


def test_workflow():

    workflow = build_graph()

    result = workflow.invoke(
        {
            "query": "What is the latest Python version?"
        }
    )

    assert "processed_query" in result
    assert "route" in result
    assert result["route"] == QueryRoute.WEB


def test_cache_router():
    from src.workflow.graph import cache_router

    assert (
        cache_router(
            {"cache_hit": True}
        )
        == "cached"
    )

    assert (
        cache_router(
            {"cache_hit": False}
        )
        == "continue"
    )