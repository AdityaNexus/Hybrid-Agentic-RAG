from src.context.models import BuiltContext

def build_prompt(
        context : BuiltContext,
)->str:
    parts : list[str] = []

    if context.history:
        parts.append("CONVERSATION")
        parts.append(context.history)

    parts.append("EVIDENCE")
    for index , item in enumerate(context.evidenc , start = 1):
        parts.append(
            f"[Evidence {index}]"
            f"Source: {item.source}\n"
            f"{item.text}"
        )
    parts.append(
        f"\nQUESTION\n{context.query}"
    )
    return "\n\n".join(parts)