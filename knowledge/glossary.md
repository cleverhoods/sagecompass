# SageCompass – Glossary
_instructions v1.2_

This glossary defines the key terms, acronyms, and conceptual anchors used throughout SageCompass reasoning.  
It ensures consistent interpretation across the ML Success Criteria framework.

---

## 1. Business and Process Terms

| Term | Definition |
|------|-------------|
| **Business Challenge** | The practical, measurable problem the organization aims to solve (e.g., reducing churn, optimizing pricing). |
| **Baseline** | The current or simplest non-ML method used for comparison (e.g., rule-based system, historical average). |
| **Counterfactual** | A “what-if” alternative used to measure ML uplift against the baseline. |
| **KPI (Key Performance Indicator)** | A quantifiable measure of success tied to business outcomes (e.g., conversion rate, error rate). |
| **Pilot** | A small, time-bounded test deployment used to evaluate ML impact before full rollout. |
| **Kill Criteria** | Pre-agreed stop conditions indicating when to halt a project that underperforms expectations. |
| **Decision Gate** | The point at which leadership decides whether to proceed, reframe, or stop the ML initiative. |
| **Success Criteria** | Combined definition of measurable goals, expected impact, and thresholds for declaring an ML effort successful. |

---

## 2. Data and Modeling Terms

| Term | Definition |
|------|-------------|
| **Feature** | An input variable used by an ML model for learning patterns. |
| **Label** | The known target value used in supervised learning (e.g., “churned” vs. “retained”). |
| **Granularity** | The level at which data is collected or aggregated (e.g., user, transaction, day). |
| **Data Leakage** | Occurs when information from the future or the target variable influences the training set, causing overfitting. |
| **Imbalance** | A situation where one class or outcome occurs far more frequently than others, biasing model results. |
| **Data Drift** | Change in the statistical distribution of input data over time. |
| **Model Drift** | Degradation of model performance due to evolving real-world data or conditions. |
| **Data Readiness** | The overall fitness of data for ML use, considering quality, labeling, and compliance. |

---

## 3. Machine Learning Paradigms

| Paradigm | Description |
|-----------|--------------|
| **Supervised Learning** | Model learns from labeled examples to predict known outcomes (e.g., classification, regression). |
| **Unsupervised Learning** | Model identifies structure or patterns without labels (e.g., clustering, dimensionality reduction). |
| **Reinforcement Learning** | Model learns via trial and reward signals through interaction with an environment. |
| **None (Rule-Based)** | Traditional algorithmic or heuristic approach, without learning from data. |

---

## 4. Common Problem Types

| Type | Description |
|------|-------------|
| **Classification** | Predicting discrete categories (e.g., spam/not spam). |
| **Regression** | Predicting continuous values (e.g., sales forecast). |
| **Forecasting** | Predicting future outcomes based on time series data. |
| **Recommendation** | Suggesting items or actions tailored to users. |
| **Anomaly Detection** | Identifying unusual or suspicious patterns. |
| **Clustering** | Grouping similar data points without labels. |
| **Ranking** | Ordering items by predicted relevance or likelihood. |
| **Policy Optimization** | Learning strategies or actions that maximize cumulative reward. |
| **Rules / Analytics** | Non-ML baselines such as heuristics, scoring systems, or if/then logic. |

---

## 5. Output JSON Fields (Quick Reference)

| Field | Meaning |
|--------|----------|
| `needs_ml` | “yes”, “no”, or “unclear” — whether ML is justified. |
| `problem_type` | Type of task (classification, regression, etc.). |
| `learning_paradigm` | Supervised, unsupervised, reinforcement, or none. |
| `business_kpis` | List of measurable KPIs tied to business outcomes. |
| `data_profile` | Summary of dataset readiness, volume, and privacy flags. |
| `ml_recommendations` | Suggested model families or algorithms. |
| `kill_criteria` | Rules for terminating unsuccessful pilots. |
| `decision` | Final recommendation: proceed, reframe, or don’t use ML. |

---

## 6. Ethical and Governance Notes
- **Fairness:** Avoid models that amplify social or demographic bias.
- **Transparency:** Ensure stakeholders understand decision logic.
- **Accountability:** Business owners must approve deployment, not the model alone.
- **Compliance:** All data use must follow applicable privacy and security laws.

---

_End of glossary.md_
