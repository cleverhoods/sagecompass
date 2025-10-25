# SageCompass – Metrics Library
_instructions v1.2_

## 1. Purpose
Provide reusable templates of measurable KPIs and success metrics that SageCompass can reference when defining or validating business goals for ML projects.  
All metrics must tie to business value, not just model performance.

---

## 2. KPI Categories and Examples

| Category | Example Metric | Unit | Business Interpretation |
|-----------|----------------|------|--------------------------|
| **Revenue Growth** | Conversion Rate | % | Share of users completing a purchase or action. |
| | Average Order Value | USD | Mean transaction value. |
| **Customer Retention** | Churn Rate | % | Percentage of users lost in a given period (lower = better). |
| | Customer Lifetime Value (CLV) | USD | Predicted long-term revenue per customer. |
| **Operational Efficiency** | Average Handling Time | seconds | Speed of service delivery or task completion. |
| | First Contact Resolution | % | Share of cases resolved on first attempt. |
| **Risk & Fraud** | False-Positive Rate | % | Fraction of normal items incorrectly flagged. |
| | Fraud Detection Recall | % | Coverage of actual fraud cases. |
| **Quality & Accuracy** | Prediction Accuracy | % | Share of correct model predictions. |
| | Mean Absolute Error (MAE) | numeric | Average difference between predictions and actuals. |
| **Cost Reduction** | Cost per Transaction | USD | Operational cost for one successful process. |
| | Automation Rate | % | Portion of tasks handled automatically. |
| **Engagement & Personalization** | Click-Through Rate (CTR) | % | Ratio of clicks to impressions. |
| | Recommendation Uptake | % | Users accepting recommended item/action. |
| **Forecasting / Planning** | Forecast Error (MAPE) | % | Mean absolute percentage error of forecast. |
| | Demand Coverage | % | Fraction of demand met without overstock. |

---

## 3. Supporting Metrics (Model-Level, for context only)

| Type | Example | Unit | Notes |
|------|----------|------|-------|
| **Classification** | Precision, Recall, F1-Score | % | Use with balanced datasets. |
| **Regression** | RMSE, MAE, R² | numeric | Evaluate continuous predictions. |
| **Ranking / Recommendation** | NDCG, Hit Rate | % | Quality of ordered recommendations. |
| **Anomaly Detection** | Detection Rate, False Alarm Rate | % | Trade-off between recall and noise. |

> These are diagnostic, not business metrics; they support technical validation only.

---

## 4. How SageCompass Uses This Library
- Suggests 3–6 KPIs matching the user’s problem type and goals.
- Keeps metrics **business-oriented first**, **model-oriented second**.
- When in doubt, prioritize metrics affecting cost, revenue, or risk.
- For each KPI, include:
    - `name` – short readable label
    - `unit` – measure of quantity
    - `target` – numeric or directional goal (↑ or ↓)

---

## 5. Example KPI JSON Structure
```json
"business_kpis": [
  {"name": "churn_rate", "unit": "%", "target": "≤10"},
  {"name": "customer_lifetime_value", "unit": "USD", "target": "≥500"},
  {"name": "support_response_time", "unit": "seconds", "target": "≤30"}
]
```

---

## 6. Notes
- Keep KPIs **stable and comparable** across pilots.
- Avoid vanity metrics (e.g., “model accuracy > 99%”) without business linkage.
- Each KPI should map to an actionable decision or measurable impact.
- When defining targets, prefer **relative improvements** (e.g., “reduce churn by 15%”) instead of arbitrary absolutes.
- Reassess KPI validity after every pilot — outdated metrics can misrepresent business success.

---

_End of metrics-library.md_
