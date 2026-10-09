from src.query.models import QueryRoute
from src.query.preprocessor import preprocess_query
from src.query.router import route_query


def test_vector_route():
    query = preprocess_query(
        "What is the company leave policy?"
    )

    assert route_query(query) == QueryRoute.VECTOR


def test_graph_route():
    query = preprocess_query(
        "Who works at OpenAI?"
    )

    assert route_query(query) == QueryRoute.GRAPH


def test_web_route():
    query = preprocess_query(
        "What is the latest OpenAI model?"
    )

    assert route_query(query) == QueryRoute.WEB


def test_hybrid_route():
    query = preprocess_query(
        "Who developed the latest model?"
    )

    assert route_query(query) == QueryRoute.HYBRID