from langgraph.graph import END, START, StateGraph

from src.context.builder import ContextBuilder
from src.generation.generator import answer
from src.generation.llm import generate
from src.generation.prompts import SYSTEM_PROMPT
from src.retrieval.adaptive import AdaptiveRetriever
from src.validation.validator import validate_answer
from src.workflow.components import WorkflowComponents
from src.workflow.state import RAGState


MAX_RETRIES = 1


def preprocess_node(state: RAGState):

    from src.query.preprocessor import preprocess_query

    state["processed_query"] = preprocess_query(
        state["query"]
    )

    return state


def cache_node(
    state: RAGState,
    components: WorkflowComponents,
):

    cached_answer = components.cache_manager.get(
        state["processed_query"].normalized
    )

    if cached_answer is not None:
        state["answer"] = cached_answer
        state["cache_hit"] = True
    else:
        state["cache_hit"] = False

    return state


def cache_write_node(
    state: RAGState,
    components: WorkflowComponents,
):

    components.cache_manager.put(
        state["processed_query"].normalized,
        state["answer"],
    )

    return state


def route_node(state: RAGState):

    from src.query.router import route_query

    state["route"] = route_query(
        state["processed_query"]
    )

    return state


def make_retrieval_node(
    components: WorkflowComponents,
):

    def retrieval_node(state: RAGState):

        state["retrieval"] = (
            components.adaptive_retriever.retrieve(
                state["processed_query"],
                state["route"],
            )
        )

        return state

    return retrieval_node


def context_node(
    state: RAGState,
    components: WorkflowComponents,
):

    retrieval = state["retrieval"]

    history = components.memory.recent(
        max_messages=6
    )

    builder = ContextBuilder()

    context = builder.build(
        query=state["query"],
        evidence=retrieval.evidence,
        history=[
            message.content
            for message in history
        ],
    )

    state["context"] = context

    return state


def generation_node(state: RAGState):

    state["answer"] = answer(
        state["context"]
    )

    state["retry_count"] = 0

    return state


def validation_node(state: RAGState):

    state["validation"] = validate_answer(
        state["answer"],
        state["context"],
    )

    return state


def regeneration_node(state: RAGState):

    previous_answer = state["answer"]

    validation = state["validation"]

    unsupported_claims = [
        result.claim
        for result in validation.claims
        if not result.supported
    ]

    retry_prompt = f"""
Question:
{state["context"].query}

Evidence:
""".strip()

    for index, evidence in enumerate(
        state["context"].evidence,
        start=1,
    ):
        retry_prompt += (
            f"\n\n[Evidence {index}]\n"
            f"Source: {evidence.source}\n"
            f"{evidence.text}"
        )

    retry_prompt += f"""

Previous answer:
{previous_answer}

Unsupported claims:
{unsupported_claims}

Generate a new answer using ONLY the evidence.

Every factual claim must include
a citation such as [Evidence 1].

Do not make unsupported claims.
""".strip()

    state["answer"] = generate(
        retry_prompt,
        system_prompt=SYSTEM_PROMPT,
        temperature=0.0,
        max_tokens=128,
    )

    state["retry_count"] = (
        state.get("retry_count", 0) + 1
    )

    return state


def cache_router(state: RAGState):

    if state.get("cache_hit", False):
        return "cached"

    return "continue"


def validation_router(state: RAGState):

    validation = state["validation"]

    if validation.valid:
        return "valid"

    if state.get("retry_count", 0) < MAX_RETRIES:
        return "retry"

    return "failed"

def memory_write_node(
    state: RAGState,
    components: WorkflowComponents,
):

    components.memory.add(
        "user",
        state["query"],
    )

    components.memory.add(
        "assistant",
        state["answer"],
    )

    return state


def build_graph(
    components: WorkflowComponents,
):

    graph = StateGraph(RAGState)

    # -------------------------
    # Nodes
    # -------------------------

    graph.add_node(
        "preprocess",
        preprocess_node,
    )

    graph.add_node(
        "cache",
        lambda state: cache_node(
            state,
            components,
        ),
    )

    graph.add_node(
        "route",
        route_node,
    )

    graph.add_node(
        "retrieve",
        make_retrieval_node(
            components,
        ),
    )

    graph.add_node(
    "context",
    lambda state: context_node(
        state,
        components,
      ),
   )

    graph.add_node(
        "generate",
        generation_node,
    )

    graph.add_node(
        "validate",
        validation_node,
    )

    graph.add_node(
        "regenerate",
        regeneration_node,
    )

    graph.add_node(
        "cache_write",
        lambda state: cache_write_node(
            state,
            components,
        ),
    )

    graph.add_node(
    "memory_write",
    lambda state: memory_write_node(
        state,
        components,
    ),
)


    # -------------------------
    # Main flow
    # -------------------------

    graph.add_edge(
        START,
        "preprocess",
    )

    graph.add_edge(
        "preprocess",
        "cache",
    )

    # -------------------------
    # Cache decision
    # -------------------------

    graph.add_conditional_edges(
        "cache",
        cache_router,
        {
            "cached": END,
            "continue": "route",
        },
    )

    # -------------------------
    # Retrieval flow
    # -------------------------

    graph.add_edge(
        "route",
        "retrieve",
    )

    graph.add_edge(
        "retrieve",
        "context",
    )

    # -------------------------
    # Generation
    # -------------------------

    graph.add_edge(
        "context",
        "generate",
    )

    graph.add_edge(
        "generate",
        "validate",
    )

    # -------------------------
    # Validation decision
    # -------------------------

    graph.add_conditional_edges(
        "validate",
        validation_router,
        {
            "valid": "cache_write",
            "retry": "regenerate",
            "failed": END,
        },
    )

    # -------------------------
    # Regeneration loop
    # -------------------------

    graph.add_edge(
        "regenerate",
        "validate",
    )

    # -------------------------
    # Successful answer
    # -------------------------
    
    graph.add_edge(
    "memory_write",
    "cache_write",
    )

    graph.add_edge(
        "cache_write",
        END,
    )

    return graph.compile()