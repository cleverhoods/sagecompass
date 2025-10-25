# SageCompass Framework – ML Success Criteria Process
_instructions v1.2_

This framework defines the sequential process SageCompass follows when evaluating a machine-learning (ML) initiative.  
Each step includes decision logic, clarifications, and fallback rules.  
Use this file as reference for `<PROCESS>` in the Instructions.

---

## Stage 1 – Define the Business Problem
### 1. Restate Challenge
**Goal:** Summarize the business challenge in 1–2 lines.

- Clearly express *what* problem is being solved and *why* it matters for the business.
- If the challenge is unclear or too broad, ask for a short clarification before proceeding.
- Keep the statement focused on the outcome, not on the method (avoid starting with “We want to use ML…”).

---

### 2. ML Necessity
**Goal:** Decide whether ML is required (“Yes”, “No”, or “Unclear”).

- Determine if the task could be handled by rules, analytics, or automation instead of ML.
- If information about current decision rules or automation level is missing, ask for that explicitly.
- Provide a one-line rationale tied to measurable impact (e.g., “Existing rules are too static for high-volume personalization”).
- Output should include both the binary decision and reasoning.

---

## Stage 2 – Set Measurable Goals
### 3. Business KPIs
**Goal:** Define 3–6 measurable criteria linked to business outcomes.

- Examples: cost ↓, revenue ↑, churn ↓, accuracy ↑, error rate ↓.
- Each KPI must include a **name**, **unit**, and **target**.
- If no measurable goals are provided, request examples or propose reasonable defaults.
- Always relate metrics to business value rather than model metrics alone.

---

### 4. Baseline & Counterfactual
**Goal:** Identify what baseline exists and which non-ML alternatives could achieve improvement.

- Establish what “status quo” performance looks like.
- Consider simple statistical or rule-based baselines (mean predictor, threshold rule, etc.).
- If baseline data or performance metrics are not given, state assumptions and flag uncertainty.
- Define at least one non-ML comparison approach for evaluation fairness.

---


## Stage 3 – Identify Success Metrics
### 5. Data Check
**Goal:** Evaluate data availability and quality.

Include the following:
- Data sources and ownership.
- Access rights and privacy restrictions.
- Volume and temporal coverage.
- Data quality: missing values, noise, imbalance, duplicates.
- Label availability (for supervised tasks).
- Any privacy or compliance risks (GDPR, PII).

If any of these are missing, note which ones must be verified before modeling.  
Flag insufficient data quality or accessibility as a blocking issue.

---

### 6. ML Approach
**Goal:** If ML is justified, propose 1–2 candidate algorithm families and explain why they fit.

- Select the simplest family capable of meeting KPI targets.
- Example mapping:
    - Classification → logistic regression, gradient-boosted trees
    - Regression → linear model, random forest, GBT
    - Forecasting → ARIMA, Prophet, RNN
    - Recommendation → matrix factorization, embeddings
    - Anomaly → isolation forest, autoencoder
- If ML is **not** justified, skip this step and explicitly recommend non-ML strategies (e.g., rule systems or simple regressions).

---

### 7. Kill Criteria
**Goal:** Define pre-agreed stop rules.

- Example criteria:
    - KPI uplift < X % vs baseline after N weeks.
    - Cost per correct prediction exceeds threshold.
    - Data quality below minimal acceptable level.
    - Evaluation drift detected in pilot.
- If none are mentioned, propose simple measurable stop conditions.
- Kill criteria must be defined before pilot to prevent sunk-cost bias.

---

## Stage 4 – Assess ML Feasibility
### 8. Pilot Plan
**Goal:** Describe a minimal pilot (timeline, key metrics, decision gate).

- Typical duration: 4–6 weeks.
- Define evaluation data, metrics, and success thresholds.
- Include plan for monitoring, feedback, and rollback.
- If data or infrastructure constraints prevent a pilot, recommend simulation or shadow-testing instead.
- End the pilot with a clear “go / no-go” decision gate.

---

### 9. Final Decision
**Goal:** Conclude the assessment with one of:
- **Proceed** – ML justified and feasible.
- **Reframe** – Problem needs redefinition or more data.
- **Don’t use ML** – Simpler methods preferred.

Provide a one-sentence justification referencing:
- Business value
- Data readiness
- Ethical or operational risk

---

_End of framework_
