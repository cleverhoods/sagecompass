# app/subgraphs/agentic_rag.py
from __future__ import annotations

import textwrap
from typing import TypedDict

from langgraph.graph import StateGraph, END
from typing_extensions import Literal

from app.utils.logger import log
from app.utils.provider_config import ProviderFactory
from app.services.vector_store import VectorStoreService


class RAGState(TypedDict, total=False):
    query: str
    phase: str               # e.g. "problem_framing", "business_goals", "kpi", ...
    context: str             # final context chosen by the graph
    source: str              # label of the retriever used
    is_relevant: str         # "Yes" or "No"
    iteration_count: int     # guard for infinite loops


# --- LLM helpers -------------------------------------------------------------

def _get_router_llm():
    instance, _params = ProviderFactory.for_agent("rag_router")
    return instance


def _get_relevance_llm():
    instance, _params = ProviderFactory.for_agent("rag_relevance")
    return instance


router_llm = _get_router_llm()
relevance_llm = _get_relevance_llm()


# --- Nodes -------------------------------------------------------------------

def router(state: RAGState) -> RAGState:
    """
    Decide which retrieval source to use for this query+phase.

    For now we support three labels:
    - "Retrieve_Strategy"  : internal strategy / business docs
    - "Retrieve_Tech"      : tech / data / architecture docs
    - "Web_Search"         : fallback to external search (stub for now)
    """
    query = state["query"]
    phase = state.get("phase", "general")

    prompt = textwrap.dedent(f"""
        You are a routing agent for SageCompass.

        Decide which knowledge source is most appropriate to start from.

        Options:
        - Retrieve_Strategy : use internal strategy / OKR / business context docs.
        - Retrieve_Tech     : use internal tech / data / architecture docs.
        - Web_Search        : use external web search (if internal docs are unlikely to help).

        Consider:
        - If the question is about business goals, value, stakeholders, org context
          or constraints, prefer Retrieve_Strategy.
        - If the question is about systems, data availability, integrations,
          pipelines or technical feasibility, prefer Retrieve_Tech.
        - If the question is clearly about very external information (news,
          regulations in a specific country, very recent events, etc.),
          use Web_Search.

        Current phase: "{phase}"
        User query: "{query}"

        Respond with EXACTLY one of:
        - Retrieve_Strategy
        - Retrieve_Tech
        - Web_Search
    """)

    decision = router_llm.invoke(prompt).content.strip()
    # Defensive cleanup
    if "Retrieve_Strategy" in decision:
        label = "Retrieve_Strategy"
    elif "Retrieve_Tech" in decision:
        label = "Retrieve_Tech"
    elif "Web_Search" in decision:
        label = "Web_Search"
    else:
        # Fallback: prefer internal docs
        label = "Retrieve_Strategy"

    state["source"] = label
    log("rag.router", {"phase": phase, "query": query[:120], "decision": label})
    return state


def route_decision(state: RAGState) -> Literal[
    "Retrieve_Strategy", "Retrieve_Tech", "Web_Search"
]:
    # We rely on router() having set state["source"] to one of these.
    src = state.get("source", "Retrieve_Strategy")
    return src  # must match keys in add_conditional_edges


def retrieve_strategy(state: RAGState) -> RAGState:
    """
    Retrieve from 'strategy' side of the knowledge base.

    For now we just use phase + suffix; you can later map this to a dedicated
    collection or metadata filter in your vector store.
    """
    query = state["query"]
    phase = state.get("phase", "general")

    # e.g. you might ingest strategy docs with phase="business_goals_strategy"
    phase_key = f"{phase}_strategy"
    context = VectorStoreService.search(
        phase=phase_key,
        query=query,
        k=6,
    )
    state["context"] = context
    state["source"] = "StrategyDocs"

    log("rag.retrieve_strategy", {"phase_key": phase_key, "len": len(context or "")})
    return state


def retrieve_tech(state: RAGState) -> RAGState:
    """
    Retrieve from 'tech' side of the knowledge base.
    """
    query = state["query"]
    phase = state.get("phase", "general")

    phase_key = f"{phase}_tech"

    context = VectorStoreService.search(
        phase=phase_key,
        query=query,
        k=6,
    )
    state["context"] = context
    state["source"] = "TechDocs"

    log("rag.retrieve_tech", {"phase_key": phase_key, "len": len(context or "")})
    return state


def web_search(state: RAGState) -> RAGState:
    """
    Placeholder for external web search.

    For now, just leave context empty or a stub. Later you can plug in a
    proper search service.
    """
    query = state["query"]
    phase = state.get("phase", "general")

    # TODO: integrate real web search here
    context = f"[Web search is not yet implemented in SageCompass. Query would be: {query!r}, phase={phase!r}]"

    state["context"] = context
    state["source"] = "WebSearchStub"

    log("rag.web_search.stub", {"query": query[:120], "phase": phase})
    return state

def check_context_relevance(state: RAGState) -> RAGState:
    """
    Ask LLM if the retrieved context is relevant to the query.
    """
    query = state["query"]
    context = state.get("context", "") or ""
    source = state.get("source", "unknown")

    prompt = textwrap.dedent(f"""
        You are a relevance checker.

        Determine whether the given CONTEXT is actually useful to answer
        the USER QUERY.

        CONTEXT (from source={source}):
        ----
        {context}
        ----

        USER QUERY:
        ----
        {query}
        ----

        Respond with EXACTLY one token:
        - Yes   (if this context is clearly relevant and helpful)
        - No    (if this context is mostly noise or off-topic)
    """)

    decision = relevance_llm.invoke(prompt).content.strip()
    if "Yes" in decision:
        label = "Yes"
    elif "No" in decision:
        label = "No"
    else:
        # conservative fallback: accept once we tried something
        label = "Yes"

    state["is_relevant"] = label
    log("rag.relevance", {"source": source, "decision": label})
    return state


MAX_ITER = 3  # or 4, but keep it small

def relevance_decision(state: RAGState) -> str:
    """
    Decide whether to move on to Augment/Generate or loop back to Web_SearchStub.
    Includes a safety cap to avoid infinite recursion.
    """

    # Short-circuit: if we're already in WebSearchStub land, don't loop forever.
    # After the *first* relevance check for WebSearchStub, we accept the answer.
    if state.get("source") == "WebSearchStub":
        return "Yes"

    current = state.get("iteration_count", 0)
    current += 1
    state["iteration_count"] = current

    if current >= MAX_ITER:
        # Safety valve: stop looping, accept current context as "relevant enough"
        from app.utils.logger import log
        log(
            "rag.relevance.max_iterations",
            {"source": state.get("source"), "iteration_count": current},
        )
        return "Yes"

    # Default behaviour: follow the LLM's judgement
    return state.get("is_relevant", "Yes")


def build_context(state: RAGState) -> RAGState:
    """
    Optional normalization step.

    For now we leave state["context"] as-is, but you could:
    - trim to a max length
    - add markers around sections
    - or summarise the context
    """
    ctx = (state.get("context") or "").strip()
    if len(ctx) > 8000:
        ctx = ctx[:8000] + "\n\n[Truncated context]"
    state["context"] = ctx
    log("rag.build_context", {"final_len": len(ctx)})
    return state


# --- Build and compile the RAG graph ----------------------------------------

def build_agentic_rag_graph():
    graph = StateGraph(RAGState)

    graph.add_node("Router", router)
    graph.add_node("Retrieve_Strategy", retrieve_strategy)
    graph.add_node("Retrieve_Tech", retrieve_tech)
    graph.add_node("Web_Search", web_search)
    graph.add_node("Relevance_Checker", check_context_relevance)
    graph.add_node("Build_Context", build_context)

    # Entry
    graph.set_entry_point("Router")

    # Route based on router decision
    graph.add_conditional_edges(
        "Router",
        route_decision,
        {
            "Retrieve_Strategy": "Retrieve_Strategy",
            "Retrieve_Tech": "Retrieve_Tech",
            "Web_Search": "Web_Search",
        },
    )

    # Retrieval → relevance checker
    graph.add_edge("Retrieve_Strategy", "Relevance_Checker")
    graph.add_edge("Retrieve_Tech", "Relevance_Checker")
    graph.add_edge("Web_Search", "Relevance_Checker")

    # Relevance checker either accepts or falls back to Web_Search
    graph.add_conditional_edges(
        "Relevance_Checker",
        relevance_decision,
        {
            "Yes": "Build_Context",  # or "BuildPrompt" / "Generate" depending on your names
            "No": "Web_Search",
        },
    )

    # Build_Context → END
    graph.add_edge("Build_Context", END)

    return graph.compile()


agentic_rag_graph = build_agentic_rag_graph()


# --- Helper API for the rest of SageCompass ---------------------------------

def run_agentic_rag(query: str, phase: str = "general") -> tuple[str, str]:
    """
    Convenience helper:
    - Runs the agentic RAG graph for a given query+phase.
    - Returns (context, source_label).
    """
    initial_state: RAGState = {
        "query": query,
        "phase": phase,
        "iteration_count": 0,
    }
    final_state = agentic_rag_graph.invoke(initial_state)
    context = final_state.get("context", "") or ""
    source = final_state.get("source", "unknown")

    return context, source
