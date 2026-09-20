import re


CITATION_PATTERN = re.compile(
    r"\[Evidence\s+(\d+)\]",
    re.IGNORECASE,
)


def extract_citations(answer: str) -> list[int]:
    return [
        int(match)
        for match in CITATION_PATTERN.findall(answer)
    ]


def validate_citations(
    answer: str,
    evidence_count: int,
) -> bool:

    citations = extract_citations(answer)

    if not citations:
        return False

    return all(
        1 <= citation <= evidence_count
        for citation in citations
    )