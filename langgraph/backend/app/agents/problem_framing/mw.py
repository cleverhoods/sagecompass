from __future__ import annotations

from app.middlewares.hilp import make_boolean_hilp_middleware

from .hilp_policy import compute_hilp_meta
from .schema import ProblemFrame

PHASE_KEY = "problem_framing"

# Middleware that evaluates ambiguities and, when supported by the runtime,
# uses the LangGraph human-in-the-loop hook to collect Yes/No/Unknown answers.
problem_framing_hilp = make_boolean_hilp_middleware(
    phase=PHASE_KEY,
    output_schema=ProblemFrame,
    compute_meta=compute_hilp_meta,
)
