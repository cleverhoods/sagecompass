# 📘 SageCompass Glossary
_instructions v1.3_

Defines standardized terminology used across the SageCompass ML Success Criteria Framework.  
All reasoning, classification, and JSON outputs must adhere to these definitions.

---

## Core Concepts

**Machine Learning (ML)**  
A family of algorithms that learn patterns from data to make predictions, classifications, or decisions without explicit programming.

**Business Challenge**  
A measurable operational or strategic problem stated in natural language (e.g., “reduce churn,” “forecast demand”).

**Success Criteria**  
Concrete, measurable outcomes that define project success (e.g., churn ↓ 15 %, RMSE ≤ 5 %).

**Baseline**  
Current non-ML performance level against which improvement is measured.

**Counterfactual / Alternative**  
The simplest non-ML or heuristic method that could solve the same problem; used to validate whether ML adds incremental value.

**Feasibility**  
Degree to which data quality, access, and labeling support ML experimentation.

---

## Problem Archetypes
(see Knowledge › problem-archetypes.md for details)

| Archetype | Goal Summary | Typical Learning Paradigm |
|------------|---------------|----------------------------|
| Classification | Assign discrete labels (spam / not spam) | Supervised |
| Regression | Predict continuous numeric values | Supervised |
| Forecasting | Predict future numeric values over time | Supervised (sequence) |
| Ranking | Order items by relevance | Supervised |
| Recommendation | Suggest items or actions | Supervised / Hybrid |
| Clustering | Group similar data points | Unsupervised |
| Anomaly Detection | Detect rare or abnormal patterns | Unsupervised / Semi-supervised |
| Policy / Reinforcement | Optimize sequential actions through feedback | Reinforcement |
| Rules / Non-ML | Deterministic logic without learning | None |

---

## Data-Related Terms

**Labels** – Known outcomes used for supervised learning.  
**Features** – Input variables or attributes used for prediction.  
**Sample** – One data record (e.g., user, order, transaction).  
**Granularity** – Unit of observation (user, session, order, etc.).  
**Volume Tier** – Approximate sample magnitude (1e3 = thousands, 1e6+ = millions).  
**Privacy Flags** – Compliance markers (PII, GDPR, none).

---

## Evaluation Metrics

- **Accuracy / Precision / Recall / F1 / ROC-AUC** → Classification
- **MAE / RMSE / R² / MAPE** → Regression / Forecasting
- **NDCG / MAP / Precision@K** → Ranking / Recommendation
- **Silhouette / DBI / CH Score** → Clustering
- **Reward / Regret / Success Rate** → Reinforcement Learning

See Knowledge › metrics-library.md for full metric templates.

---

## Decision Outcomes

| Decision | Meaning |
|-----------|----------|
| **proceed** | ML justified; pilot recommended |
| **reframe** | Problem unclear or reformulation needed |
| **dont_use_ml** | Simpler non-ML method sufficient |
| **unclear** | Insufficient information to decide |

---

## JSON Output Conventions

- All responses start with valid JSON.
- Use lowercase keys with underscores.
- `pending_question` contains **only one** concise clarifying question when blocked.
- Boolean or categorical options (yes | no | unclear) must match schema.
- Lists (e.g., metrics, goals) must use plain JSON arrays, not quoted strings.

---

_End of glossary.md_
