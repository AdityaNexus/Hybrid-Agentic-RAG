from src.query.models import ProcessedQuery, QueryRoute
from src.retrieval.decision import RetrievalDecision
from src.retrieval.evidence import Evidence
from src.retrieval.hybrid_retriever import HybridRetriever
from src.retrieval.web_evidence import web_to_evidence
from src.retrieval.web_retriever import WebRetriever

class AdaptiveRetriever:
    def __init__(
        self,
        hybrid_retriever: HybridRetriever,
        web_retriever: WebRetriever,
    ) -> None:
        self.hybrid_retriever = hybrid_retriever
        self.web_retriever = web_retriever

    def retrieve(
        self,
        query: ProcessedQuery,
        route: QueryRoute,
    ) -> RetrievalDecision:

        evidence: list[Evidence] = []

        # --------------------------------
        # Initial retrieval
        # --------------------------------

        if route == QueryRoute.VECTOR:
            evidence = self.hybrid_retriever.search(
                query.normalized,
                vector_top_k=5,
            )

            confidence = self._confidence(evidence)

            if confidence < 0.45:
                web_results = self.web_retriever.search(
                    query.normalized,
                )
                evidence.extend(web_to_evidence(web_results))

        elif route == QueryRoute.GRAPH:
            evidence = self.hybrid_retriever.search(
                query.normalized,
                vector_top_k=2,
                entity_names=query.entities,
            )

        elif route == QueryRoute.HYBRID:
            evidence = self.hybrid_retriever.search(
                query.normalized,
                vector_top_k=5,
                entity_names=query.entities,
            )

        elif route == QueryRoute.WEB:
            web_results = self.web_retriever.search(
                query.normalized,
            )
            evidence = web_to_evidence(web_results)

        confidence = self._confidence(evidence)

        return RetrievalDecision(
            evidence=evidence[:8],
            confidence=confidence,
            needs_fallback=confidence < 0.45,
        )

    @staticmethod
    def _confidence(
        evidence: list[Evidence],
    ) -> float:
        if not evidence:
            return 0.0

        scores = sorted(
            (
                max(0.0, min(1.0, item.score))
                for item in evidence
            ),
            reverse=True,
        )

        # Weighted confidence.
        weights = [0.6, 0.3, 0.1]

        confidence = 0.0

        for score, weight in zip(scores[:3], weights):
            confidence += score * weight

        return confidence