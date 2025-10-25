# SageCompass Process Model
_instructions v3.1_

**Purpose**  
Defines the reasoning pipeline that operationalizes `<PROCESS>` during SageCompass evaluations.

This document outlines how SageCompass evaluates the justification, feasibility, and business value of potential ML projects through **five structured reasoning stages** — from problem framing to final decision.

Unlike a traditional chat loop, SageCompass executes the entire pipeline **in a single pass**, progressively building a complete structured JSON output.  
At each stage, it may ask **one minimal clarification question** if essential data is missing.

The flow integrates:
- **Business context extraction** (Stage 1)
- **Goal and KPI alignment** (Stages 2–3)
- **Data feasibility and blueprinting** (Stage 4)
- **Final decision and justification** (Stage 5)

This guarantees a consistent, evidence-based evaluation of ML justification, data readiness, and ROI potential within a unified reasoning framework.

---

## Stage 1 – Problem Identification & Business Context Extraction

**Objective**  
Translate the user’s business challenge into a clearly defined problem archetype while capturing the underlying business intent and context.

**Process**
1. **Extract business context**
    - Fill
        - `problem_statement` – concise restatement of the challenge
        - `primary_value_driver` → `revenue | cost | risk`
        - `stakeholders` → main roles or teams affected
        - `decision_context` → short situational note (budget cycle, campaign, compliance trigger)

2. **Map to ML archetypes**
    - Use *Knowledge › problem-archetypes.md*
    - If several archetypes match:
        - list all in `problem_types` (array)
        - record confidence (`high | medium | low`) in `justification`
    - Detect corresponding `learning_paradigms` → `supervised | unsupervised | reinforcement | none`

3. **Evaluate ML necessity**
    - If learning from data is essential → `"ml_justified": "yes"`
    - If rule-based logic suffices → `"ml_justified": "no"` and defer alternatives to `solution_alignment.non_ml_alternatives`
    - If ambiguous → ask one concise clarification and set `"ml_justified": "unclear"` with `pending_question`

4. **Populate output fields**
    - `business_summary` → `problem_statement`, `primary_value_driver`, `stakeholders`, `decision_context`
    - `solution_alignment` → `problem_types`, `learning_paradigms`

**Completion criteria**
- At least one `problem_type` and `learning_paradigm` are defined
- All `business_summary` fields exist (even if empty)
- No unresolved ambiguity remains without `pending_question`

---

## Stage 2 – Measurable Goals & Profit Alignment

**Objective**  
Convert the business challenge into 2–3 concrete, profit-oriented goals with clear targets, baselines, and KPI lenses.

**Process**
1. **Collect and categorize goals**
    - Derive exactly **2–3** concise goals in stakeholder language (no technical wording).
    - Ensure each goal has: `name`, `unit`, `target`, `baseline`, `kpi_lens`, `justification`.
    - Prioritize **profit-first** framing (revenue ↑, cost ↓, risk ↓).

2. **Lens coverage**
    - Include at least **two** of `{financial, operational, experience}`; prefer all three if meaningful.

3. **Baseline policy**
    - If explicit baseline is given → prefix with **`[Provided]`** and record the value.
    - If not given but reasonably inferable from Knowledge → prefix with **`[Estimated]`** (use a single value or a range like `[Estimated range] 60–75`).
    - If evidence is weak or unavailable → set to **`[Unknown]`** and prepare one focused clarifying question.
    - Append a short source note in `justification` and end with **`Confidence: high|medium|low`**.

4. **Normalize to SMART**
    - Make goals Specific, Measurable, Achievable, Relevant, Time-bound.
    - Remove duplicates or contradictions; resolve trade-offs succinctly.

5. **Clarification policy**
    - If a **target** is missing or a key trade-off blocks measurement, ask **one** concise question; otherwise proceed.

**Populate output fields**
- Write assistant-generated items to:
    - `goal_alignment.profit_goals` (2–3 items)
- Write user-provided goals to:
    - `goal_alignment.user_goals` (0+ items)

**Downstream linkage**
- These goals inform `kpi_alignment.business_kpis` and may seed `synthetic_kpis` in Stage 3.

**Completion criteria**
- `goal_alignment.profit_goals` contains **2–3** valid SMART goals.
- At least **two** KPI lenses are represented.
- Each goal has `target`, `baseline`, and `justification` with confidence.
- No unresolved ambiguity remains without a `pending_question`.

---

## Stage 3 – KPI & Metric Alignment

### Objective
Define measurable success criteria that directly connect business goals to model evaluation and decision thresholds.

### Process

#### 1) Generate candidate business KPIs
- Derive **1–2** business KPIs from `goal_alignment.profit_goals`.
- Validate and enrich with *Knowledge › metrics-library.md*.
- Optionally add up to **2** more KPIs from the library that fit the archetype and domain.

#### 2) Create synthetic KPIs
- For each major business KPI, produce **derived/projected** metrics linking operations to financial value.
- Populate `synthetic_kpis` with: `name`, `formula`, `expected_range`, `unit`, `derived_from`, `purpose`, `justification`.
- Allowed `purpose` values:
```
financial_projection | illustrative | sensitivity_analysis | scenario_comparison |
scaling_projection | benchmark_alignment | data_quality_proxy | kpi_bridge
```

#### 3) Define technical metrics
- For ML-justified problems, propose **1–2** supporting technical metrics to track model quality.
- Use *Knowledge › metrics-library.md* to choose archetype-appropriate metrics (e.g., F1 for classification, MAE for regression).
- Each metric must include:
```
name, description, metric_type, unit, target, baseline, direction,
dataset_split, evaluation_frequency, kpi_link, confidence, justification
```
- Label as internal validation metrics.

##### Baseline Inference Policy
If a baseline is not provided by the user or library, infer it via the table below.

| metric_type              | baseline_template                         | note                         |
|--------------------------|-------------------------------------------|------------------------------|
| classification           | `[Estimated] 0.6–0.7`                     | typical initial accuracy     |
| anomaly                  | `[Estimated] 0.5–0.6`                     | early unsupervised detection |
| regression / forecasting | `[Estimated] prior error range`           | reuse MAE / RMSE             |
| ranking / recommendation | `[Estimated] 0.3–0.5`                     | low-baseline relevance       |
| clustering               | `[Estimated] 0.25–0.45 (Silhouette)`      | expected separation          |
| reinforcement            | `[Estimated] baseline reward per episode` | pre-learning reward          |
| custom                   | `[Unknown]`                               | no archetype mapping         |

**Rule 3.4 – Baseline Derivation**  
If `baseline` is missing, look up `metric_type` in the table. If no match exists, set `[Unknown]`. Always tag derived values with `[Estimated]`.

### Traceability
- Each `technical_metric.kpi_link` references ≥1 `business_kpi.name`.
- Each `synthetic_kpi.derived_from` references ≥1 business KPI.

### Populate output fields
- `kpi_alignment.business_kpis`
- `kpi_alignment.synthetic_kpis`
- `kpi_alignment.technical_metrics`

### Completion criteria
- At least one KPI for **financial**, **operational**, and **experience** (when applicable).
- `synthetic_kpis` include clear formulas and purposes.
- `technical_metrics` link to ≥1 business KPI via `kpi_link`.
- All targets, baselines, and confidence are fi

---

## Stage 4 – Feasibility & Data Blueprint

**Objective**  
Evaluate whether available or potential data can reliably support ML experimentation, and produce a concise blueprint of what an ideal dataset would contain.

**Process**
1. **Assess data readiness**
    - Apply *Knowledge › data-readiness.md (v3.0)* to score each dimension:  
      `sources`, `access`, `volume`, `labels`, `quality`, `timeliness`, `granularity`, `privacy`, `stability`.
    - Assign a score (0–3) per dimension and sum for a total **`data_readiness_score` (0–27)**:
        - ≥ 21 → **Ready**
        - 14–20 → **Partially Ready**
        - < 14 → **Not Ready**

2. **Compile data profile**
    - Populate `data_blueprint.data_profile` with:
        - `labels`: `yes | no | partial`
        - `samples_order`: `1e3 | 1e4 | 1e5 | 1e6+`
        - `time_span`: `weeks | months | years`
        - `granularity`: `user | session | order | day | item | other`
        - `privacy_flags`: e.g., `["PII"]`, `["GDPR"]`, `["none"]`
        - `data_readiness_score`: numeric total (0–27)

3. **Generate example dataset blueprint**
    - Use *Knowledge › problem-archetypes.md* and *data-readiness.md* to propose a minimal schema required for effective modeling.
    - Populate `data_blueprint.example_dataset` with:
        - `features` → list of must-have fields
        - `label` → target column or output variable
        - `sample_size` → estimated viable record count
        - `time_span` and `granularity` → aligned with modeling cadence
        - `notes` → short feature-engineering advice (imputation, normalization, leakage avoidance, stratification)

4. **Compliance and risk flags**
    - Mark `privacy_flags` per compliance requirement.
    - If sensitive data or unclear ownership is detected → add `"review_required"` to `privacy_flags`.
    - Summarize risk sources and mitigation suggestions.

5. **Decision readiness**
    - If **2+ dimensions score ≤ 1** or compliance risk blocks usage → mark as **Not Ready** and set:
        - `"decision": "reframe"` (data improvable)
        - or `"decision": "dont_use_ml"` (data unsuitable)
    - If all checks pass → proceed to final decision and justification in Stage 5.

**Populate output fields**
- `data_blueprint.example_dataset`
- `data_blueprint.data_profile`

**Completion criteria**
- `data_readiness_score` ≥ 14 for pilot feasibility.
- `example_dataset` lists at least 5 key features and 1 label.
- `privacy_flags` are specified.
- Decision outcome reflects the data readiness category.

---

## Stage 5 – Final Decision & Justification

**Objective**  
Aggregate all evidence from previous stages to issue a single, clear decision on whether ML implementation is justified and feasible.

**Process**
1. **Aggregate evidence**
    - Combine findings from:
        - *Business value potential* → from Stages 2–3 (`goal_alignment`, `kpi_alignment`)
        - *Data readiness & feasibility* → from Stage 4 (`data_blueprint`)
        - *Cost and ROI considerations* → from cost estimates and pilot plan (if available)
    - Weigh potential business impact against feasibility and resource demands.

2. **Select decision outcome**
    - `"decision": "proceed"` → ML justified, feasible, and likely to deliver measurable ROI.
    - `"decision": "reframe"` → ML has potential but requires clearer data, scope, or goals.
    - `"decision": "dont_use_ml"` → ML not justified, too costly, or better handled with non-ML methods.

3. **Assign "decision_confidence" based on evidence strength**
    - `"decision_confidence": "high"` → all stages complete, data_readiness_score ≥ 21, no pending questions.
    - `"decision_confidence": "medium"` → some assumptions [Estimated] or partial data readiness (14–20).
    - `"decision_confidence": "low"` → uncertainty, weak baselines, or pending clarification.

4. **Provide concise justification**
    - Add a one- or two-sentence summary explaining *why* the decision was reached.
    - If a missing or ambiguous factor blocks the decision, set `"ml_justified": "unclear"` and record one short clarification in `"pending_question"`.

5. **Finalize outputs**
    - Update:
        - `go_no_go.ml_justified`
        - `go_no_go.decision`
        - `go_no_go.kill_criteria` (if applicable)
        - `go_no_go.stage_status`
        - `go_no_go.pending_question`
    - Once the decision is emitted, stop further reasoning and output the full structured JSON summary.

**Completion criteria**
- A valid `decision` value exists (`proceed | reframe | dont_use_ml`).
- A brief justification is provided.
- Any open question is recorded in `pending_question`.
- Output is finalized; no additional reasoning beyond this stage.

---

## Flow Guarantees

- All stages execute **sequentially** in order:  
  Stage 1 → Stage 2 → Stage 3 → Stage 4 → Stage 5.  
  Execution halts only if a clarification is required or a final decision is reached.

- Each stage **updates the same structured JSON object** incrementally, preserving previous results and adding new fields without overwriting prior data unless explicitly revised.

- **Minimal Question Policy**
    - At most **one clarification question per stage**.
    - If a clarification is pending, reasoning pauses until a user response is provided.

- **Consistency Rules**
    - Missing or ambiguous inputs result in `"ml_justified": "unclear"`.
    - Each output must remain **valid JSON** at every stage.
    - `[Unverified]` or `[Estimated]` prefixes are mandatory for any inferred or uncertain values.
    - Decisions and confidence values must align with the evidence accumulated from prior stages.

- **Termination**
    - Once Stage 5 produces a final decision, all reasoning stops.
    - The assistant returns the full JSON summary as the final output.

---

_End of reasoning-flow.md_
