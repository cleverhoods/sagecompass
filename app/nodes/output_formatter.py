from __future__ import annotations

from html import escape
from typing import List

from app.state import PipelineState
from app.utils.logger import log
from app.models import (
    ProblemFrame,
    BusinessGoal,
    EligibilityResult,
    KPIItem,
    SolutionDesign,
    CostEstimate,
)

NodeReturn = PipelineState


def _safe_list(items) -> List[str]:
    return items or []


def _badge_for_category(cat: str) -> tuple[str, str]:
    """
    Map eligibility.category to (label, css_class).
    """
    mapping = {
        "core_ai_problem": ("Core AI problem", "badge-core"),
        "ai_useful_but_not_core": ("AI useful", "badge-useful"),
        "not_really_ai": ("Not really AI", "badge-nonai"),
        "unclear_need_more_info": ("Unclear", "badge-unclear"),
    }
    return mapping.get(cat, (escape(cat), "badge-unclear"))


def _render_problem_frame(pf: ProblemFrame | None) -> str:
    if pf is None:
        return "<p>No problem framing available.</p>"

    actors_html = "\n".join(f"<li>{escape(a)}</li>" for a in _safe_list(pf.actors))
    pain_html = "\n".join(f"<li>{escape(p)}</li>" for p in _safe_list(pf.current_pain))
    constraints_html = "\n".join(
        f"<li>{escape(c)}</li>" for c in _safe_list(pf.constraints)
    )
    ambiguities_html = "\n".join(
        f"<li>{escape(a.item)}</li>" for a in _safe_list(pf.ambiguity_flags)
    )

    return f"""
<section class="section" id="section-1">
  <h2>1. Problem framing</h2>
  <p><strong>Business domain:</strong> {escape(pf.business_domain)}<br>
  <strong>Primary outcome:</strong> {escape(pf.primary_outcome)}</p>
  <div class="grid-2">
    <div>
      <h4>Actors</h4>
      <ul>
        {actors_html}
      </ul>
    </div>
    <div>
      <h4>Current pain</h4>
      <ul>
        {pain_html}
      </ul>
    </div>
  </div>
  <div class="grid-2">
    <div>
      <h4>Constraints</h4>
      <ul>
        {constraints_html}
      </ul>
    </div>
    <div>
      <h4>Ambiguity flags</h4>
      <ul>
        {ambiguities_html or "<li>None explicitly noted.</li>"}
      </ul>
    </div>
  </div>
</section>
"""


def _render_goals(goals: List[BusinessGoal]) -> str:
    if not goals:
        return """
<section class="section" id="section-2">
  <h2>2. Business goals</h2>
  <p>No goals identified.</p>
</section>
"""

    rows = []
    for g in goals:
        pct = max(0.0, min(1.0, g.weight)) * 100.0
        rows.append(
            f"""
      <tr>
        <td>{escape(g.subject)}</td>
        <td>{escape(g.direction)}</td>
        <td>{g.weight:.2f} ({pct:.0f}%)</td>
        <td><div class="bar-container"><div class="bar-fill bar-weight" style="width:{pct:.0f}%;"></div></div></td>
      </tr>
    """
        )

    rows_html = "\n".join(rows)

    return f"""
<section class="section" id="section-2">
  <h2>2. Business goals</h2>
  <table>
    <thead>
      <tr><th>Subject</th><th>Direction</th><th>Weight</th><th>Weight (visual)</th></tr>
    </thead>
    <tbody>
      {rows_html}
    </tbody>
  </table>
</section>
"""


def _render_eligibility(elig: EligibilityResult | None) -> str:
    if elig is None:
        return """
<section class="section" id="section-3">
  <h2>3. AI eligibility</h2>
  <p>No eligibility assessment available.</p>
</section>
"""

    label, badge_class = _badge_for_category(elig.category)
    conf_pct = max(0.0, min(1.0, elig.confidence)) * 100.0

    reasons_html = "\n".join(
        f"<li>{escape(r)}</li>" for r in _safe_list(elig.ai_opportunities)
    )
    missing_html = "\n".join(
        f"<li>{escape(q)}</li>" for q in _safe_list(elig.required_clarifications)
    )

    return f"""
<section class="section" id="section-3">
  <h2>3. AI eligibility</h2>
  <p>Category: {escape(elig.category)} <span class="badge {badge_class}">{escape(label)}</span></p>
  <div class="score" style="margin-bottom:1em;">
    <span>{elig.confidence:.2f}</span>
    <div class="bar-container" style="height:14px; width: 70%;">
      <div class="bar-fill bar-confidence" style="width:{conf_pct:.0f}%;"></div>
    </div>
  </div>
  <div class="grid-2">
    <div>
      <h4>Reasons / AI opportunities</h4>
      <ul>
        {reasons_html or "<li>No explicit AI opportunities listed.</li>"}
      </ul>
    </div>
    <div>
      <h4>Missing information</h4>
      <ul>
        {missing_html or "<li>No specific clarifications recorded.</li>"}
      </ul>
    </div>
  </div>
</section>
"""


def _render_kpis(kpis: List[KPIItem]) -> str:
    if not kpis:
        return """
<section class="section" id="section-4">
  <h2>4. KPIs</h2>
  <p>No KPIs defined.</p>
</section>
"""

    rows = []
    for k in kpis:
        rows.append(
            f"""
      <tr>
        <td>{escape(k.subject)}</td>
        <td>{escape(k.direction)}</td>
        <td>{escape(k.indicator)}</td>
        <td>{escape(k.scope)}</td>
      </tr>
    """
        )

    rows_html = "\n".join(rows)

    return f"""
<section class="section" id="section-4">
  <h2>4. KPIs</h2>
  <table>
    <thead>
      <tr><th>Subject</th><th>Direction</th><th>Indicator</th><th>Scope</th></tr>
    </thead>
    <tbody>
      {rows_html}
    </tbody>
  </table>
</section>
"""


def _render_solution_design(sd: SolutionDesign | None, cost_estimates: List[CostEstimate]) -> str:
    if sd is None or not sd.options:
        return """
<section class="section" id="section-5">
  <h2>5. Solution options and recommendation</h2>
  <p>No solution options generated.</p>
</section>
"""

    recommended_id = sd.recommended_option_id
    cost_index = {ce.option_id: ce for ce in cost_estimates}

    option_cards = []
    for opt in sd.options:
        is_recommended = recommended_id is not None and opt.id == recommended_id
        recommended_badge = (
            '<span class="badge badge-recommended">Recommended</span>' if is_recommended else ""
        )
        card_class = "option-card recommended" if is_recommended else "option-card"

        comps_html = "\n".join(
            f"<li>{escape(c)}</li>" for c in _safe_list(opt.main_components)
        )
        data_req_html = "\n".join(
            f"<li>{escape(d)}</li>" for d in _safe_list(opt.data_requirements)
        )
        integr_html = "\n".join(
            f"<li>{escape(i)}</li>" for i in _safe_list(opt.integration_points)
        )
        impact_html = "\n".join(
            f"<li>{escape(ch)}</li>" for ch in _safe_list(opt.change_impact)
        )

        fit_pct = max(0.0, min(1.0, opt.fit_score)) * 100.0
        cx_pct = max(0.0, min(1.0, opt.complexity_score)) * 100.0

        card = f"""
  <div class="{card_class}">
    <div class="option-header">
      {escape(opt.id)} <span class="badge badge-kind">{escape(opt.kind)}</span>{recommended_badge}
    </div>
    <p class="option-paragraph"><strong>Summary:</strong> {escape(opt.summary)}</p>
    <p class="option-paragraph"><strong>How it uses AI:</strong> {escape(opt.how_it_uses_ai)}</p>
    <div class="two-col-lists">
      <div>
        <h4>Main components</h4>
        <ul>{comps_html}</ul>
      </div>
      <div>
        <h4>Data requirements</h4>
        <ul>{data_req_html}</ul>
      </div>
    </div>
    <div class="two-col-lists">
      <div>
        <h4>Integration points</h4>
        <ul>{integr_html}</ul>
      </div>
      <div>
        <h4>Change impact</h4>
        <ul>{impact_html}</ul>
      </div>
    </div>
    <div class="score">
      <span>Fit: {opt.fit_score:.2f}</span>
      <div class="bar-container"><div class="bar-fill bar-fit" style="width:{fit_pct:.0f}%;"></div></div>
    </div>
    <div class="score">
      <span>Complexity: {opt.complexity_score:.2f}</span>
      <div class="bar-container"><div class="bar-fill bar-complexity" style="width:{cx_pct:.0f}%;"></div></div>
    </div>
  </div>
"""
        option_cards.append(card)

    cards_html = "\n".join(option_cards)
    rationale_html = "\n".join(f"<li>{escape(r)}</li>" for r in _safe_list(sd.rationale))

    # Cost table (summary per option if available)
    cost_rows = []
    for opt in sd.options:
        ce = cost_index.get(opt.id)
        if ce is None:
            continue
        unc_pct = max(0.0, min(1.0, ce.uncertainty)) * 100.0
        cost_rows.append(
            f"""
      <tr{' class="highlighted"' if opt.id == recommended_id else ''}>
        <td>{escape(opt.id)}{' <span class="badge badge-recommended">Recommended</span>' if opt.id == recommended_id else ''}</td>
        <td>{ce.effort_person_months.min:.1f}–{ce.effort_person_months.max:.1f}</td>
        <td>{ce.calendar_time_months.min:.1f}–{ce.calendar_time_months.max:.1f}</td>
        <td>{ce.capex_ballpark.min:.0f}–{ce.capex_ballpark.max:.0f}</td>
        <td>{ce.opex_ballpark.min:.0f}–{ce.opex_ballpark.max:.0f}</td>
        <td>
          {ce.uncertainty:.2f}
          <div class="bar-container" style="width: 100px; display: inline-block; vertical-align: middle; margin-left: 8px;">
            <div class="bar-fill bar-uncertainty" style="width:{unc_pct:.0f}%; height:14px;"></div>
          </div>
        </td>
      </tr>
    """
        )

    cost_html = ""
    if cost_rows:
        cost_html = f"""
<section class="section" id="section-6">
  <h2>6. Cost &amp; effort estimates</h2>
  <table class="cost-table">
    <thead>
      <tr><th>Option</th><th>Effort (person-months)</th><th>Calendar time (months)</th><th>CAPEX</th><th>OPEX</th><th>Uncertainty</th></tr>
    </thead>
    <tbody>
      {''.join(cost_rows)}
    </tbody>
  </table>
  <p class="muted">Note: Ranges are approximate and driven by integration, data, and change-management factors.</p>
</section>
"""

    return f"""
<section class="section" id="section-5">
  <h2>5. Solution options and recommendation{' <span class="badge badge-recommended">Recommended: ' + escape(recommended_id) + '</span>' if recommended_id else ''}</h2>
  {cards_html}
  <h3>Rationale for recommendation</h3>
  <ul>
    {rationale_html or "<li>No detailed rationale recorded.</li>"}
  </ul>
</section>
{cost_html}
"""


def _html_shell(title: str, subtitle: str, body: str) -> str:
    # CSS copied/adapted from your sample report for consistency.
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<title>{escape(title)}</title>
<style>
  body {{
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Oxygen, Ubuntu, Cantarell, "Open Sans", "Helvetica Neue", sans-serif;
    background-color: #f0f0f0;
    margin: 0;
    padding: 20px 0 40px 0;
    color: #222;
  }}
  .container {{
    max-width: 1000px;
    margin: 0 auto;
    padding: 0 20px;
  }}
  h1 {{
    text-align: center;
    margin-bottom: 0.2em;
  }}
  h2 {{
    border-bottom: 2px solid #ddd;
    padding-bottom: 0.3em;
    margin-top: 1.8em;
    margin-bottom: 0.6em;
    font-weight: 600;
    font-size: 1.3em;
  }}
  .subtitle {{
    text-align: center;
    font-style: italic;
    color: #555;
    margin-top: 0;
    margin-bottom: 1.5em;
  }}
  .section {{
    background: white;
    border: 1px solid #ddd;
    border-radius: 6px;
    padding: 20px 25px 25px 25px;
    margin-bottom: 1.8em;
    box-shadow: 0 1px 3px rgba(0,0,0,0.07);
  }}
  .highlight {{
    background-color: #fff9db;
    border-left: 6px solid #f7d154;
    padding: 15px 20px;
    font-weight: 600;
    font-size: 1.1em;
    line-height: 1.4em;
    color: #5a4a00;
    border-radius: 4px;
  }}
  ul {{
    margin-top: 0.3em;
    margin-bottom: 0.8em;
    padding-left: 1.2em;
  }}
  ul li {{
    margin-bottom: 0.3em;
  }}
  .grid-2 {{
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 30px 40px;
    margin-bottom: 1.2em;
  }}
  table {{
    width: 100%;
    border-collapse: collapse;
    margin-top: 0.6em;
    margin-bottom: 0.8em;
  }}
  th, td {{
    border-bottom: 1px solid #ddd;
    padding: 8px 10px;
    text-align: left;
    vertical-align: middle;
  }}
  th {{
    background-color: #f7f7f7;
    font-weight: 600;
  }}
  .badge {{
    display: inline-block;
    font-size: 0.75em;
    font-weight: 700;
    padding: 3px 9px;
    border-radius: 12px;
    color: white;
    vertical-align: middle;
    margin-left: 8px;
    user-select: none;
  }}
  .badge-core {{
    background-color: #2a9d8f;
  }}
  .badge-useful {{
    background-color: #0077cc;
  }}
  .badge-nonai {{
    background-color: #d62828;
  }}
  .badge-unclear {{
    background-color: #6c757d;
  }}
  .badge-kind {{
    background-color: #555;
    font-weight: 600;
    font-size: 0.7em;
    padding: 2px 7px;
    margin-left: 6px;
  }}
  .badge-recommended {{
    background-color: #e76f51;
    font-weight: 700;
    font-size: 0.75em;
    padding: 3px 8px;
    margin-left: 10px;
  }}
  .bar-container {{
    background-color: #eee;
    border-radius: 8px;
    height: 14px;
    width: 100%;
    overflow: hidden;
    vertical-align: middle;
  }}
  .bar-fill {{
    height: 100%;
    border-radius: 8px 0 0 8px;
  }}
  .bar-weight {{
    background-color: #2a9d8f;
  }}
  .bar-confidence {{
    background-color: #2a9d8f;
  }}
  .bar-fit {{
    background-color: #2a9d8f;
  }}
  .bar-complexity {{
    background-color: #f4a261;
  }}
  .bar-uncertainty {{
    background-color: #d62828;
  }}
  .score {{
    display: flex;
    align-items: center;
    gap: 10px;
    margin-top: 0.3em;
    margin-bottom: 0.8em;
  }}
  .score > span {{
    min-width: 50px;
    font-weight: 600;
  }}
  .score .bar-container {{
    flex-grow: 1;
  }}
  .muted {{
    color: #666;
    font-size: 0.9em;
    margin-top: 0.8em;
  }}
  .option-card {{
    border: 1px solid #ccc;
    border-radius: 8px;
    padding: 15px 20px;
    margin-bottom: 1.2em;
    background-color: #fafafa;
  }}
  .option-card.recommended {{
    border-color: #e76f51;
    background-color: #fff4f1;
  }}
  .option-header {{
    font-weight: 700;
    font-size: 1.1em;
    margin-bottom: 0.3em;
  }}
  .option-paragraph {{
    margin-top: 0.3em;
    margin-bottom: 0.8em;
  }}
  .two-col-lists {{
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 20px 40px;
    margin-bottom: 1em;
  }}
  .two-col-lists > div > h4 {{
    margin-bottom: 0.3em;
    font-weight: 600;
    font-size: 1em;
  }}
  .two-col-lists ul {{
    margin-bottom: 0;
  }}
  .cost-table tr.highlighted {{
    background-color: #fff4f1;
  }}
  @media (max-width: 700px) {{
    .grid-2, .two-col-lists {{
      grid-template-columns: 1fr;
    }}
  }}
</style>
</head>
<body>
<div class="container">
<h1>{escape(title)}</h1>
<p class="subtitle">{escape(subtitle)}</p>
{body}
</div>
</body>
</html>
"""


def node_html(state: PipelineState) -> NodeReturn:
    """
    Pure output formatter node.

    - Reads structured results from the state.
    - Renders a static HTML report (no LLM).
    - Stores the HTML in state["html_report"].
    """
    log("agent.node.start", {"agent": "output_formatter"})

    user_question = state.get("raw_text") or ""
    pf: ProblemFrame | None = state.get("problem_frame")
    goals: list[BusinessGoal] = state.get("business_goals") or []
    elig: EligibilityResult | None = state.get("eligibility")
    kpis: list[KPIItem] = state.get("kpis") or []
    sd: SolutionDesign | None = state.get("solution_design")
    cost_estimates: list[CostEstimate] = state.get("cost_estimates") or []

    # Hero text
    title = "AI Opportunity Assessment Report"
    subtitle = pf.primary_outcome if pf is not None else "AI opportunity assessment"

    section_0 = f"""
<section class="section" id="section-0">
  <h2>0. User question</h2>
  <div class="highlight">{escape(user_question)}</div>
</section>
"""

    html_body = "".join(
        [
            section_0,
            _render_problem_frame(pf),
            _render_goals(goals),
            _render_eligibility(elig),
            _render_kpis(kpis),
            _render_solution_design(sd, cost_estimates),
        ]
    )

    html = _html_shell(title=title, subtitle=subtitle, body=html_body)

    state["html_report"] = html

    log(
        "agent.node.done",
        {
            "agent": "output_formatter",
            "html_length": len(html),
        },
    )

    return state
