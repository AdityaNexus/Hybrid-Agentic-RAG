from src.context.models import BuiltContext

SYSTEM_PROMPT = """
You are a grounded question-answering system.

Answer the user's question using ONLY the supplied evidence.

Rules:
- Do not invent facts.
- Do not use outside knowledge.
- If the evidence is insufficient, say that the available evidence
  does not contain enough information to answer.
- Do not treat the conversation history as factual evidence.
- Keep the answer concise and directly answer the question.
- When making a factual claim, include the relevant evidence number
  such as [Evidence 1].
"""

def build_generation_prompt(
        context: BuiltContext,
)->str:
    parts : list[str] = []

    if context.history:
        parts.append("CONVERSATION HISTORY:")

        for message in context.history:
            parts.append(message)
    parts.append("\nEVIDENCE:")

    if context.evidence:
        for index , item in enumerate(context.evidence , start = 1):
            parts.append(
                f"[Evidence {index}]"
                f"Source: {item.source}\n"
                f"{item.text}"
            )
    else:
        parts.append("No evidence available.")


    parts.append(

        f"\nQUESTION:\n{context.query}"
    )
    return "\n\n".join(parts)