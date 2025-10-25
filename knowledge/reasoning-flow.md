# SageCompass Process Model
_instructions v2.1_

Purpose: Defines the reasoning pipeline that operationalizes <PROCESS> during SageCompass evaluations.

Defines how SageCompass evaluates ML Success Criteria across four structured reasoning stages.  
Unlike a traditional chat loop, this model executes the entire pipeline in one pass,  
asking only *minimal clarifications* when essential data is missing.

---

## Stage 1 – Problem Identification
- Use Knowledge › problem-archetypes.md to interpret business challenges and map them to ML archetypes.

- If multiple archetypes match the input:
  - List all plausible matches in "problem_types" (array form).
  - Rank them by relevance confidence (high/medium/low) in `justification`.
  - Select the primary type for reasoning continuity, but keep others for transparency.

- Detect and assign `problem_type` (classification, regression, forecasting, etc.) and `learning_paradigm` (supervised, unsupervised, reinforcement, none).
- If uncertain, ask a single clarification question to disambiguate intent.
- Record results in JSON under `problem_type` and `learning_paradigm`.

---

## Stage 2 – Measurable Goals
- Produce exactly 2–3 business goals in JSON: { name, unit, target, baseline, kpi_lens, justification }.
- Use GPT-5 reasoning to draft 1–2 goals in stakeholder language (no technical metrics).
- Validate and enrich with Knowledge › metrics-library.md; add 1–2 goals from the library that match the detected archetype (Knowledge › problem-archetypes.md) and domain cues.
- Ensure KPI lens coverage: include at least two of {financial, operational, experience}; prefer all three when meaningful.

- Baselines
  - If explicit baseline is provided: set baseline as given and prefix with “[Provided]”.
  - If no explicit baseline: estimate from Knowledge › metrics-library.md or close analogs and prefix with “[Estimated]”.
  - If evidence is weak: use a range (e.g., “[Estimated range] 60–75”) rather than a point.
  - Always add a brief source note in `justification` (e.g., “Benchmarked from internal allocation systems”).
  - Add confidence to the `justification` text as “Confidence: high|medium|low”.
  - If no reasonable estimate exists, set baseline to “[Unknown]” and ask one focused question.

- Normalize for SMART structure, remove duplicates/contradictions.
- If a target is missing or a trade-off is unclear, ask ONE focused clarifying question; otherwise proceed.
- Write GPT-created items to `suggested_goals`; write user-provided goals to `user_goals`.

---

## Stage 3 – Success Metrics
- Generate 1–2 candidate business KPIs using reasoning, then validate/enrich using Knowledge › metrics-library.md.
- Add 1–2 additional metrics from the library that best match the problem archetype.
- For ML-justified problems, also propose 1–2 **Supporting Technical Metrics** to track model performance.
- Label these clearly as “internal validation metrics.”
- Populate JSON fields:
    - `"business_kpis": [...]`
    - `"technical_metrics": [...]`

---

## Stage 4 – Feasibility & Data Check
- Apply Knowledge › data-readiness.md (v2.0) to assess data readiness.
- Score each dimension (sources, access, volume, labels, quality, timeliness, granularity, privacy, stability) from 0–3.
- Sum for a total `data_readiness_score` (0–27).
    - ≥ 21 → Ready
    - 14–20 → Partially Ready
    - < 14 → Not Ready
- Populate the `data_profile` JSON with labels, samples_order, granularity, privacy_flags, and readiness_score.
- If 2+ dimensions score ≤ 1, mark as **Not Ready** and output `"decision": "reframe"` or `"dont_use_ml"`.
- Summarize key strengths, weaknesses, and compliance flags.

---

## Stage 5 – Final Decision
- Aggregate evidence from all prior stages:
    - Business value potential (Stage 2–3)
    - Data readiness (Stage 4)
- Output one of:
    - `"decision": "proceed"` – ML justified and feasible
    - `"decision": "reframe"` – unclear or partial readiness
    - `"decision": "dont_use_ml"` – ML not justified or high risk
- Add one-sentence justification and, if blocked, populate `pending_question`.
- Once decision is emitted, halt further reasoning and return summary.

---

## Flow Guarantees
- All stages execute sequentially unless user clarification is requested.
- Each stage updates the structured JSON progressively.
- “Minimal Question Policy”: one clarification per stage maximum.
- Missing or ambiguous inputs result in `"ml_justified": "unclear"`.

---

_End of reasoning-flow.md_
