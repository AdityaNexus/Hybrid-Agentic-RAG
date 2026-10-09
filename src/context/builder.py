from src.context.budget import estimate_tokens, fits_budget
from src.context.models import BuiltContext, ContextItem
from src.retrieval.evidence import Evidence


DEFAULT_CONTEXT_BUDGET = 1200


class ContextBuilder:
    def __init__(
        self,
        max_tokens: int = DEFAULT_CONTEXT_BUDGET,
    ) -> None:
        self.max_tokens = max_tokens
    

    def build(
        self,
        query: str,
        evidence: list[Evidence],
        history: list[str] | None = None,
    ) -> BuiltContext:
        evidence = self._deduplicate(evidence)
        history = history or []

        selected_evidence: list[ContextItem] = []
        selected_history: list[str] = []

        used_tokens = estimate_tokens(query)

        # -----------------------------
        # Evidence first
        # -----------------------------

        for item in evidence:
            if fits_budget(
                used_tokens,
                item.text,
                self.max_tokens,
            ):
                selected_evidence.append(
                    ContextItem(
                        text=item.text,
                        source=item.source,
                        score=item.score,
                        retrieval_method=item.retrieval_method,
                        metadata=item.metadata,
                    )
                )

                used_tokens += estimate_tokens(item.text)

        # -----------------------------
        # Recent history
        # -----------------------------

        for message in reversed(history):
            if fits_budget(
                used_tokens,
                message,
                self.max_tokens,
            ):
                selected_history.insert(0, message)
                used_tokens += estimate_tokens(message)

        return BuiltContext(
            query=query,
            evidence=selected_evidence,
            history=selected_history,
            total_tokens=used_tokens,
        )

    @staticmethod
    def _deduplicate(
        evidence: list[Evidence],
    ) -> list[Evidence]:

        seen: set[str] = set()
        result: list[Evidence] = []

        for item in evidence:
            normalized = " ".join(
                item.text.lower().split()
            )

            if normalized in seen:
                continue

            seen.add(normalized)
            result.append(item)

        return result