from src.graph.graph_store import GraphStore


def test_graph_store(tmp_path):
    store = GraphStore(tmp_path / "graph")

    store.add_document(
        document_id="doc1",
        source="test.pdf",
        title="Test Document",
    )

    store.add_chunk(
        chunk_id="chunk1",
        document_id="doc1",
        text="Rahul works at OpenAI.",
    )

    store.add_entity(
        entity_id="entity1",
        name="Rahul",
        entity_type="PERSON",
    )

    store.add_mention(
        chunk_id="chunk1",
        entity_id="entity1",
    )

    store.close()