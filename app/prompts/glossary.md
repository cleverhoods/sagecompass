# SageCompass - Glossary
_instructions v3.0_

Defines standardized terminology used across the **SageCompass v3.0 Framework**.  
All reasoning, cost modeling, and JSON outputs must use these terms consistently.

---

## 1. Core Concepts

**Machine Learning (ML)**  
Algorithms that learn statistical or structural patterns from data to make predictions, classifications, or decisions **without explicit hard-coded rules**.

**Business Challenge**  
A measurable operational or strategic problem stated in natural language (e.g., “reduce churn,” “forecast demand,” “detect anomalies”).

**Success Criteria**  
Concrete, measurable outcomes that define success — typically expressed as KPIs, baselines, and targets (e.g., churn ↓ 15 %, RMSE ≤ 5 %).

**Baseline**  
Current non-ML performance level or operational benchmark used to measure ML impact.

**Counterfactual / Alternative**  
A simpler, deterministic, or rule-based approach that could achieve the same goal; used to test whether ML offers **incremental value**.

**Feasibility**  
Degree to which data quality, labeling, access, and governance make ML experimentation possible.

**Synthetic KPI**  
A derived or modeled metric linking business goals to expected impact (e.g., projected ROI, revenue uplift, savings per retained user).

**ROI Lens**  
A comparative framework used to evaluate the return on investment between ML and non-ML solutions, expressed through cost, payback period, and breakeven assumptions.

---

## 2. Problem Archetypes
*(see Knowledge › problem-archetypes.md for detailed archetype definitions)*

| Archetype | Goal Summary | Typical Learning Paradigm | Typical Metric |
|------------|---------------|----------------------------|----------------|
| **Classification** | Assign discrete labels (spam / not spam) | Supervised | F1, ROC-AUC |
| **Regression** | Predict continuous numeric values | Supervised | MAE, RMSE |
| **Forecasting** | Predict future numeric values over time | Supervised (sequence) | MAPE, RMSE |
| **Ranking** | Order items by relevance | Supervised | NDCG, MAP |
| **Recommendation** | Suggest items or actions | Supervised / Hybrid | Recall@K |
| **Clustering** | Group similar data points | Unsupervised | Silhouette |
| **Anomaly Detection** | Detect rare or abnormal patterns | Unsupervised / Semi-supervised | F1, Recall |
| **Policy / Reinforcement** | Optimize sequential actions via feedback | Reinforcement | Average Reward |
| **Rules / Non-ML** | Deterministic logic, no learning | None | N/A |

---

## 3. Data-Related Terms

| Term | Definition |
|------|-------------|
| **Label** | Known ground-truth value used for supervised learning. |
| **Feature** | Input variable or signal used to predict the label. |
| **Sample** | One observation or record (e.g., user, transaction, order). |
| **Granularity** | Unit of analysis (user, session, order, day, item). |
| **Volume Tier** | Approximate dataset size (`1e3 = thousands`, `1e6+ = millions`). |
| **Privacy Flags** | Compliance markers: `["PII"]`, `["GDPR"]`, `["review_required"]`, or `["none"]`. |
| **Data Readiness Score** | Aggregate 0–27 rating reflecting 9 dimensions of data quality and compliance. |

---

## 4. KPI and Metric Terms

| Category | Example Metrics | Purpose |
|-----------|----------------|----------|
| **Business KPIs** | Retention rate, revenue uplift, cost reduction | Measure business success |
| **Synthetic KPIs** | Revenue_retained = active_users × ARPU × retention_rate | Model or projection metric |
| **Technical Metrics** | F1, RMSE, Recall@K, MAPE | Measure model quality |
| **ROI Metrics** | Payback months, breakeven conditions | Evaluate financial viability |

---

## 5. Evaluation Metric Families

- **Classification:** Accuracy, Precision, Recall, F1, ROC-AUC
- **Regression / Forecasting:** MAE, RMSE, R², MAPE
- **Ranking / Recommendation:** NDCG@K, MAP@K, Precision@K, Recall@K
- **Clustering:** Silhouette, Davies–Bouldin, Calinski–Harabasz
- **Reinforcement:** Average Reward, Cumulative Reward, Regret

Reference: *Knowledge › metrics-library.md*

---

## 6. Decision Outcomes

| Decision | Meaning |
|-----------|----------|
| **proceed** | ML justified and feasible; proceed with pilot |
| **reframe** | Partial readiness or unclear scope; gather more data |
| **dont_use_ml** | Simpler rule-based solution sufficient |
| **unclear** | Insufficient information; clarification required |

---

## 7. JSON Output Conventions

- All responses must begin with **valid JSON**.
- Keys are **lowercase_with_underscores**.
- `pending_question` holds exactly **one** focused clarification question.
- Boolean or categorical values must use schema terms (`yes | no | unclear`).
- Lists and metrics use **plain arrays**, not quoted lists.
- `[Estimated]`, `[Unverified]`, and `[Provided]` prefixes mark data origin.
- `confidence` levels must always be stated as `high | medium | low`.

---

## 8. Compliance & Governance Vocabulary

| Term | Definition |
|------|-------------|
| **GDPR / CCPA** | Primary data protection frameworks guiding lawful processing. |
| **PII** | Personally Identifiable Information — must be anonymized or hashed. |
| **DPO Review** | Triggered when `"privacy_flags": ["review_required"]`. |
| **Audit Trail** | Record of dataset versions, transformations, and decisions. |
| **Kill Criteria** | Explicit conditions to halt ML exploration. |

---

_End of glossary.md_
