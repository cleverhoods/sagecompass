from __future__ import annotations

from langgraph.graph import StateGraph, END

from app.state import PipelineState
from app.nodes.problem_framing import node_pf
from app.nodes.business_goals import node_bg
from app.nodes.eligibility import node_ea
from app.nodes.kpi import node_kpi
from app.nodes.solution_design import node_sda
from app.nodes.rag import node_rag
from app.nodes.cost_estimation import node_cea
from app.nodes.output_formatter import node_html
from app.nodes.supervisor import node_supervisor


# --- Build the graph (supergraph) -------------------------------------------------

graph = StateGraph(PipelineState)

# Worker / agent nodes
graph.add_node("problem_framing", node_pf)
graph.add_node("rag", node_rag)                    # RAG node
graph.add_node("business_goals", node_bg)
graph.add_node("eligibility", node_ea)
graph.add_node("kpi", node_kpi)
graph.add_node("solution_design", node_sda)
graph.add_node("cost_estimation", node_cea)
graph.add_node("output_formatter", node_html)

# Supervisor / router node (pure code, returns Command(goto=...))
graph.add_node("supervisor", node_supervisor)

# Entry point: supervisor decides what to run first based on state
graph.set_entry_point("supervisor")

# After each worker node, control returns to the supervisor
graph.add_edge("problem_framing", "supervisor")
graph.add_edge("rag", "supervisor")               # <-- missing edge added
graph.add_edge("business_goals", "supervisor")
graph.add_edge("eligibility", "supervisor")
graph.add_edge("kpi", "supervisor")
graph.add_edge("solution_design", "supervisor")
graph.add_edge("cost_estimation", "supervisor")

# Final node: output_formatter → END
graph.add_edge("output_formatter", END)

# Compile the app
app = graph.compile()


def run_pipeline(raw_text: str) -> PipelineState:
    """
    Convenience helper to run the full graph on a single user query.

    The initial state only needs 'raw_text'; all other fields are populated
    by the agents and nodes along the graph.
    """
    initial_state: PipelineState = {"raw_text": raw_text}
    final_state: PipelineState = app.invoke(initial_state)
    return final_state


__all__ = ["app", "run_pipeline"]
