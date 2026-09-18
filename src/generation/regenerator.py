from src.context.models import BuiltContext
from src.generation.generator import answer
from src.validation.validator import validate_answer


MAX_RETRIES = 1


RETRY_SYSTEM_PROMPT = """
You are a grounded question-answering system.

Your previous answer contained unsupported claims.

Generate a corrected answer using ONLY the supplied evidence.

Rules:
- Remove every unsupported claim.
- Do not add outside knowledge.
- Every factual claim must be supported by the evidence.
- If the evidence is insufficient, clearly say so.
- Keep the answer concise.
"""


def generate_grounded_answer(
    context: BuiltContext,
) -> tuple[str, bool]:

    current_answer = answer(context)

    validation = validate_answer(
        current_answer,
        context,
    )

    if validation.valid:
        return current_answer, True

    # --------------------------------
    # Controlled retry
    # --------------------------------

    for _ in range(MAX_RETRIES):

        unsupported = "\n".join(
            f"- {claim.claim}"
            for claim in validation.claims
            if not claim.supported
        )

        retry_prompt = _build_retry_prompt(
            context,
            current_answer,
            unsupported,
        )

        from src.generation.llm import generate

        current_answer = generate(
            retry_prompt,
            system_prompt=RETRY_SYSTEM_PROMPT,
            temperature=0.0,
            max_tokens=512,
        )

        validation = validate_answer(
            current_answer,
            context,
        )

        if validation.valid:
            return current_answer, True

    return (
        "I don't have enough evidence to answer this reliably.",
        False,
    )


def _build_retry_prompt(
    context: BuiltContext,
    previous_answer: str,
    unsupported_claims: str,
) -> str:

    evidence = "\n\n".join(
        f"[Evidence {index}]\n{item.text}"
        for index, item in enumerate(
            context.evidence,
            start=1,
        )
    )

    return f"""
QUESTION:
{context.query}

EVIDENCE:
{evidence}

PREVIOUS ANSWER:
{previous_answer}

UNSUPPORTED CLAIMS:
{unsupported_claims}

Rewrite the answer using only supported information.
"""