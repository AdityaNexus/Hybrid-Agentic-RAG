from sentence_transformers import SentenceTransformer

MODEL_NAME = "BAAI/bge-small-en-v1.5"

class EmbeddingModel:
    def __init__(self,model_name:str = MODEL_NAME)->None:
        self.model = SentenceTransformer(model_name)

    def embed_documents(self,texts: list[str])->list[list[float]]:
        if not texts:
            return []

        embeddings = self.model.encode(texts,normalize_embeddings=True,show_progress_bar = False)

        return embeddings.tolist()

    def embed_query(self,text:str)->list[float]:
        if not text.strip():
            raise ValueError("Query text cannot be empty.")

        embeddding = self.model.encode(text,normalize_embeddings=True,show_progress_bar = False)

        return embeddding.tolist()