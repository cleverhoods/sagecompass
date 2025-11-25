# app/orchestrator.py
from __future__ import annotations

from typing import Any, Dict, Generator, Tuple

from app.graph import run_pipeline
from app.utils.logger import log


class SageCompass:
    """
    Orchestrator that wraps the LangGraph pipeline.

    From the outside, it still exposes the same .ask(question, context) API
    that your UI calls, but internally it delegates to run_pipeline().
    """

    def __init__(self, pipeline=None):
        # 'pipeline' is kept only for backwards compatibility / logging.
        self.pipeline = pipeline or [
            "problem_framing",
            "atomic_business_goals",
            "eligibility",
            "kpi",
            "solution_design",
            "cost_estimation",
        ]
        self.state: Dict[str, Any] = {"context": {}, "trace": []}

    def ask(self, question: str, context: dict | None = None) -> Dict[str, Any]:
        """
        Run the full LangGraph pipeline on the given question (non-streaming).
        """
        self.state = {"context": context or {}, "trace": []}

        log("orchestrator.pipeline.start", {"question": question, "mode": "sync"})

        # Run the LangGraph app in one shot
        graph_state = run_pipeline(question)

        # Flatten key parts of graph_state into self.state for easier UI access

        if "problem_frame" in graph_state:
            self.state["problem_frame"] = graph_state["problem_frame"]

        if "business_goals" in graph_state:
            self.state["business_goals"] = graph_state["business_goals"]

        if "eligibility" in graph_state:
            self.state["eligibility"] = graph_state["eligibility"]

        if "kpis" in graph_state:
            self.state["kpis"] = graph_state["kpis"]

        if "solution_design" in graph_state:
            self.state["solution_design"] = graph_state["solution_design"]

        if "cost_estimates" in graph_state:
            self.state["cost_estimates"] = graph_state["cost_estimates"]

        if "final_recommendation" in graph_state:
            self.state["final_recommendation"] = graph_state["final_recommendation"]

        # HTML report from output_formatter
        if "html_report" in graph_state:
            # The node stores the raw string under 'html_report'
            self.state["html_report"] = graph_state["html_report"]

        # Keep the full raw PipelineState as well
        self.state["graph_state"] = graph_state

        self.state["trace"].append(
            {
                "stage": "langgraph_pipeline",
                "result": {
                    "eligibility": graph_state.get("eligibility"),
                    "solution_design": graph_state.get("solution_design"),
                    "cost_estimates": graph_state.get("cost_estimates"),
                },
            }
        )

        log("orchestrator.pipeline.complete", {"agents": self.pipeline, "mode": "sync"})

        return self.state

    def ask_stream(
        self,
        question: str,
        context: dict | None = None,
    ) -> Generator[Tuple[str, Any], None, None]:
        """
        Streaming version of ask().

        Yields (label, value) tuples as each node finishes, in roughly
        the logical order of the pipeline.
        """
        # Local import to avoid any circular issues
        from app.graph import app as graph_app
        from app.state import PipelineState

        log(
            "orchestrator.pipeline.start",
            {"question": question, "mode": "stream"},
        )

        initial_state: PipelineState = {"raw_text": question}
        if context:
            initial_state["context"] = context

        # Track which keys we have already emitted
        seen_keys = set()

        # Ordered mapping from PipelineState keys to human labels
        sections = [
            ("problem_frame", "PROBLEM FRAME"),
            ("business_goals", "BUSINESS GOALS"),
            ("eligibility", "ELIGIBILITY"),
            ("kpis", "KPIs"),
            ("solution_design", "SOLUTION DESIGN"),
            ("cost_estimates", "COST ESTIMATES"),
            ("final_recommendation", "FINAL RECOMMENDATION"),
            ("html_report", "HTML REPORT"),
        ]

        # Stream pipeline values
        for state in graph_app.stream(initial_state, stream_mode="values"):
            # state is a PipelineState (dict-like)
            for key, label in sections:
                if key in state and key not in seen_keys:
                    seen_keys.add(key)
                    value = state[key]

                    log(
                        "orchestrator.stream.section",
                        {"section": key, "label": label},
                    )

                    # Yield to Gradio (or any other UI)
                    yield label, value

        log(
            "orchestrator.pipeline.complete",
            {"mode": "stream", "sections": list(seen_keys)},
        )
