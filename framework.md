# SageCompass – ML Success Criteria Framework (v1.0)

## 1. Purpose
This framework provides a structured approach to decide whether a business challenge
requires Machine Learning (ML), and—if yes—how to measure its success in business terms.
It is used during project intake, scoping, and feasibility evaluation.

---

## 2. When ML is *Not* Needed
Skip ML if the challenge:
- Can be solved with fixed rules, look-ups, or deterministic logic.
- Has low data variability or very few data points.
- Requires high interpretability with strict business logic.
- Needs guaranteed outcomes over probabilistic ones.
- Would cost more to build and maintain an ML system than to use heuristics.

Typical examples: thresholds, routing rules, template matching, inventory reorder triggers.

---

## 3. When ML *Adds Value*
ML becomes justified when:
- The system must learn complex, nonlinear relationships from data.
- Inputs are numerous, noisy, or high-dimensional.
- There is measurable business benefit from improved prediction or ranking accuracy.
- Manual rules are too costly to maintain or perform poorly at scale.

Common patterns:
- Forecasting demand, churn, sales, or capacity.
- Ranking, recommendation, classification, or anomaly detection.
- NLP or image understanding tasks that exceed human rule design.

---

## 4. Success Criteria (Business KPIs)
Tie every ML goal to one or more measurable business outcomes.
Examples:

| KPI Type | Example Metric | Unit | Typical Target |
|-----------|----------------|------|----------------|
| Efficiency | Avg. handling time | seconds | ↓ 20 % |
| Revenue | Conversion rate | % | ↑ 5 % |
| Retention | Churn rate | % | ↓ 10 % |
| Quality | False-positive rate | % | ↓ 30 % |
| Cost | Cost per prediction | HUF / USD | ↓ 15 % |

If no KPI exists, define one before modeling.

---

## 5. Baselines and Counterfactuals
Always compare against a clear reference:
- Current manual or rule-based system.
- Simple statistical baseline (mean, moving average, linear regression).
- Vendor or industry benchmark if internal data is unavailable.

Improvement claims are valid only when measured *relative* to this baseline.

---

## 6. Data Readiness Checklist
| Dimension | Example Questions |
|------------|------------------|
| **Sources** | What systems or sensors provide data? |
| **Access** | Is data accessible with proper authorization? |
| **Volume** | Are there enough samples per prediction unit? |
| **Quality** | Missing values, noise, duplicates? |
| **Labels** | Are outcome labels present and reliable? |
| **Timeliness** | Is data recent enough to reflect reality? |
| **Privacy** | Any PII, GDPR, or compliance constraints? |

If ≥ 2 of these dimensions are unknown or weak, flag data as *not ready*.

---

## 7. Appropriate ML Approach (if justified)
Select the simplest family that can meet the KPI.

| Problem Type | Typical Approach | Notes |
|---------------|-----------------|-------|
| Tabular regression/classification | Gradient-boosted trees, logistic regression | Fast, interpretable |
| Time-series forecasting | ARIMA, Prophet, XGBoost, RNN | Needs temporal validation |
| NLP | Transformer encoder models | Requires text preprocessing |
| Computer vision | CNN or pretrained encoder | Compute-intensive |
| Recommendation | Matrix factorization, embeddings | Needs user-item data |

Always prefer simpler models when they meet the goal within error tolerance.

---

## 8. Kill Criteria
Define before training:
- KPI uplift < X % after N weeks.
- Cost per correct prediction > target threshold.
- Data quality below minimum acceptable level.
- Model drift detected in production metrics.

Stop or re-scope if any condition is met.

---

## 9. Pilot Plan Template
**Goal:** Validate business impact in a small, safe experiment.  
**Duration:** 4–6 weeks typical.  
**Steps:**
1. Prepare data subset.
2. Train baseline + ML candidate.
3. Compare results on hold-out or A/B test.
4. Report KPI delta with confidence interval.
5. Decision gate: Proceed / Reframe / Stop.

---

## 10. Ethical & Operational Considerations
- Monitor bias, fairness, and data drift continuously.
- Keep humans in the loop for critical decisions.
- Document data sources, metrics, and model assumptions.
- Treat every ML output as probabilistic, not authoritative.

---

_Last updated: 2025-10-25 (v1.0)_
