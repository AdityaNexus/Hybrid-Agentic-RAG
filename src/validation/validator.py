from src.context.models import BuiltContext
from src.validation.citations import extract_citations
from src.validation.claims import extract_claims
from src.validation.matcher import match_claim
from src.validation.models import ClaimResult, ValidationResult


def validate_answer(
    answer: str,
    citations_or_context: str | BuiltContext,
    context: BuiltContext | None = None,
) -> ValidationResult:
    if context is None:
        if not isinstance(citations_or_context, BuiltContext):
            raise TypeError("context must be provided as a BuiltContext.")
        context = citations_or_context
    else:
        if not isinstance(citations_or_context, str):
            raise TypeError("citations must be provided as a string.")
        answer = f"{answer} {citations_or_context}"

    if not answer.strip():
        return ValidationResult(
            valid=False,
            claims=[],
            reason="Empty answer.",
        )

    if not context.evidence:
        return ValidationResult(
            valid=False,
            claims=[],
            reason="No evidence available.",
        )

    # --------------------------------
    # 1. Validate citations
    # --------------------------------

    citations = extract_citations(answer)

    if not citations:
        return ValidationResult(
            valid=False,
            claims=[],
            reason="Answer contains no evidence citations.",
        )

    invalid_citations = [
        citation
        for citation in citations
        if citation < 1
        or citation > len(context.evidence)
    ]

    if invalid_citations:
        return ValidationResult(
            valid=False,
            claims=[],
            reason=(
                f"Invalid evidence citation(s): "
                f"{invalid_citations}"
            ),
        )

    # --------------------------------
    # 2. Extract claims
    # --------------------------------

    claims = extract_claims(answer)

    if not claims:
        return ValidationResult(
            valid=False,
            claims=[],
            reason="No claims detected.",
        )

    # --------------------------------
    # 3. Check claim support
    # --------------------------------

    results: list[ClaimResult] = [
        match_claim(
            claim,
            context,
        )
        for claim in claims
    ]

    unsupported = [
        result
        for result in results
        if not result.supported
    ]

    if unsupported:
        return ValidationResult(
            valid=False,
            claims=results,
            reason="One or more claims lack sufficient evidence.",
        )

    return ValidationResult(
        valid=True,
        claims=results,
        reason="All claims are supported and citations are valid.",
    )