from src.graph.graph_store import GraphStore
from src.retrieval.graph_retriever import GraphRetriever


def test_graph_retrieval(tmp_path):
    store = GraphStore(tmp_path / "graph")

    store.add_entity(
        "organization:openai",
        "OpenAI",
        "ORGANIZATION",
    )

    store.add_entity(
        "product:gpt-4",
        "GPT-4",
        "PRODUCT",
    )

    store.add_relationship(
        "organization:openai",
        "developed",
        "product:gpt-4",
        "chunk-1",
    )

    retriever = GraphRetriever(store)

    results = retriever.search_entity("OpenAI")

    assert len(results) == 1
    assert results[0].related_entity == "GPT-4"
    assert results[0].relationship == "developed"

    store.close()