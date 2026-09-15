from src.retrieval.embeddings import EmbeddingModel

def test_embed():
    model = EmbeddingModel()

    embedding = model.embed_query("What is retrieval augmented generation?")
    assert embedding
    assert isinstance(embedding, list)
    assert len(embedding) ==384