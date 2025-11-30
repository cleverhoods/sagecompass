# app/test_run.py
from __future__ import annotations

from pprint import pprint

import os, sys
from pathlib import Path
from dotenv import load_dotenv


# --- Ensure project root in sys.path ---
PROJECT_ROOT = os.path.abspath(os.path.dirname(__file__))
if PROJECT_ROOT not in sys.path:
    sys.path.append(PROJECT_ROOT)

# --- Load environment variables ---
base = Path(__file__).resolve().parent
load_dotenv(dotenv_path=base.parent / ".env")

from app.runtime.orchestrator import SageCompass


def run_example():
    compass = SageCompass()

    question = (
        "Could we build a single, agency-wide model that forecasts required "
        "developer capacity per client per sprint based on project history, "
        "tech stack, and ticket complexity, to optimize planning?"
    )

    state = compass.ask(question)

   # print("\n=== FINAL RECOMMENDATION ===")
   # print(state.get("final_recommendation", "<no final_recommendation>"))

    print("\n=== PROBLEM FRAME ===")
    pprint(state.get("problem_frame"))

    print("\n=== BUSINESS GOALS ===")
    pprint(state.get("business_goals"))

    print("\n=== ELIGIBILITY ===")
    pprint(state.get("eligibility"))

    print("\n=== KPIs ===")
    pprint(state.get("kpis"))

    print("\n=== SOLUTION DESIGN ===")
    pprint(state.get("solution_design"))

    print("\n=== COST ESTIMATES ===")
    pprint(state.get("cost_estimates"))


if __name__ == "__main__":
    run_example()
