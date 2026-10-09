from src.retrieval.evidence import Evidence 
from src.retrieval.graph_retriever import GraphRetriever
from src.retrieval.vector_retriever import VectorRetriever 

class HybridRetriever:
    def __init__(
        self,
        vector_retriever: VectorRetriever,
        graph_retriever: GraphRetriever,    
    ):
        self.vector_retriever = vector_retriever
        self.graph_retriever = graph_retriever 

    def search(
            self,
            query:str,
            vector_top_k : int = 5,
            entity_names : list[str] | None = None,
    )->list[Evidence]:
        evidence : list[Evidence] = []

        vector_results = self.vector_retriever.search(
            query,
            top_k=vector_top_k,
        )

        for result in vector_results:
            evidence.append(
                Evidence(
                    evidence_id = result.chunk_id,
                    text  = result.text,
                    score = result.score,
                    source = result.metadata.get("source",""),
                    retrieval_method = "vector",
                    metadata = result.metadata,
                )
            )

        
        for entity_name in entity_names or []:
            graph_results = self.graph_retriever.search_entity(
                entity_name
            )

            for result in graph_results:
                text = (
                    f"{result.entity} "
                    f"{result.relationship} "
                    f"{result.related_entity}"
                )

                evidence.append(
                    Evidence(
                        evidence_id=(
                            f"graph:"
                            f"{result.entity}:"
                            f"{result.relationship}:"
                            f"{result.related_entity}"
                        ),
                        text=text,
                        score=1.0,
                        source=result.chunk_id,
                        retrieval_method="graph",
                        metadata={
                            "entity": result.entity,
                            "relationship": result.relationship,
                            "related_entity": result.related_entity,
                            "chunk_id": result.chunk_id,
                        },
                    )
                )
        return self._fuse(evidence)

    @staticmethod
    def _fuse(evidence: list[Evidence])-> list[Evidence]:
        seen : dict[str, Evidence] = {}
        for item in evidence:
            existing = seen.get(item.evidence_id)
            if existing is None or item.score > existing.score:
                seen[item.evidence_id] = item

        return sorted(
            seen.values(),
            key = lambda x : x.score,
            reverse = True,
        )

    