"""Node factory exports for SageCompass graphs.

This module exposes all node factories following the DI-first pattern.
Each factory returns a NodeWithRuntime callable that can be registered
with LangGraph's StateGraph.

Pattern:
    All nodes are created via `make_node_*` factories that accept
    injected dependencies (agents, tools, config) and return closures
    capturing those dependencies. This ensures:
    - No import-time construction
    - Full testability via dependency injection
    - Explicit wiring in graph composition

Node Categories:
    - Supervisors: Global routing (supervisor), phase routing (phase_supervisor)
    - Preflight: Guardrails check, ambiguity detection/resolution
    - Phase Nodes: Problem framing, context retrieval, etc.

Example:
    >>> from app.nodes import make_node_problem_framing
    >>> from app.agents.problem_framing.agent import build_agent
    >>> node = make_node_problem_framing(agent=build_agent())
    >>> graph.add_node("problem_framing", node)
"""

from __future__ import annotations

from app.nodes.ambiguity_clarification import make_node_ambiguity_clarification
from app.nodes.ambiguity_clarification_external import (
    make_node_ambiguity_clarification_external,
)
from app.nodes.ambiguity_scan import make_node_ambiguity_scan
from app.nodes.ambiguity_supervisor import make_node_ambiguity_supervisor
from app.nodes.gating_guardrails import make_node_guardrails_check
from app.nodes.phase_supervisor import make_node_phase_supervisor
from app.nodes.problem_framing import make_node_problem_framing
from app.nodes.retrieve_context import make_node_retrieve_context
from app.nodes.supervisor import make_node_supervisor

__all__ = [
    "make_node_ambiguity_clarification",
    "make_node_ambiguity_clarification_external",
    "make_node_ambiguity_scan",
    "make_node_ambiguity_supervisor",
    "make_node_guardrails_check",
    "make_node_phase_supervisor",
    "make_node_problem_framing",
    "make_node_retrieve_context",
    "make_node_supervisor",
]
