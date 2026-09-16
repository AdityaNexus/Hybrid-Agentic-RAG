from src.query.models import QueryRoute
from src.query.router import route_query

def test_route_query():
    assert(
        route_query("what is the company leave policy")
        == QueryRoute.VECTOR
    )

def test_graph_route():
    assert (
        route_query("Who works at OpenAI?")
        == QueryRoute.GRAPH
    )


def test_web_route():
    assert (
        route_query("What is the latest OpenAI model?")
        == QueryRoute.WEB
    )


def test_hybrid_route():
    assert (
        route_query("Who developed the latest model?")
        == QueryRoute.HYBRID
    )