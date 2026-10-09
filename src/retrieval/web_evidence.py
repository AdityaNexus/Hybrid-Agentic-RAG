from src.retrieval.evidence import Evidence
from src.retrieval.web_models import WebResult


def web_to_evidence(
    results: list[WebResult],
) -> list[Evidence]:

    evidence = []

    for index, result in enumerate(results):
        evidence.append(
            Evidence(
                evidence_id=f"web:{index}:{result.url}",
                text=result.snippet,
                score=1.0 / (index + 1),
                source=result.url,
                retrieval_method="web",
                metadata={
                    "title": result.title,
                    "url": result.url,
                },
            )
        )

    return evidence