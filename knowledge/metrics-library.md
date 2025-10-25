# 💼 SageCompass Metrics Library (Business-Focused)
_instructions v1.3_

Defines **business-level success criteria** for evaluating ML project value.  
Each archetype lists **primary business KPIs (stakeholder-facing)** and **supporting technical metrics (internal validation)**.

---

## 1. Classification
**Business Goal:** Automate or improve accuracy of categorical decisions (e.g., fraud, defect, triage).

**Primary Business KPIs:**
- % of manual decisions automated
- Processing time per case ↓ (%)
- Operational cost per decision ↓ (%)
- Accuracy of business-critical decisions (%)
- False alerts / complaint rate ↓ (%)
- Compliance adherence ↑ (%)
- Throughput per analyst ↑ (%)
- SLA adherence improvement (%)

**Supporting Technical Metrics:** Accuracy, Precision, Recall, F1, ROC-AUC

---

## 2. Regression
**Business Goal:** Predict numeric outcomes to optimize efficiency, planning, or cost.

**Primary Business KPIs:**
- Forecast deviation from target ↓ (%)
- Resource allocation efficiency ↑ (%)
- Cost forecast error ↓ (%)
- Operational waste ↓ (%)
- SLA breach rate ↓ (%)
- Unit cost per output ↓ (%)
- Planning cycle time ↓ (%)
- Profit margin stability ↑ (%)

**Supporting Technical Metrics:** MAE, RMSE, R², MAPE

---

## 3. Forecasting
**Business Goal:** Anticipate future demand or events to guide proactive decisions.

**Primary Business KPIs:**
- Demand-supply mismatch ↓ (%)
- Stockout frequency ↓ (%)
- Inventory waste ↓ (%)
- Forecast-driven profit uplift (Δ %)
- Schedule adherence ↑ (%)
- Production overcapacity ↓ (%)
- Revenue volatility ↓ (%)
- Planning accuracy improvement (%)

**Supporting Technical Metrics:** MAPE, RMSE, Forecast bias

---

## 4. Ranking
**Business Goal:** Optimize ordering or prioritization (e.g., search, leads, task queues).

**Primary Business KPIs:**
- Click-through rate (CTR) ↑ (%)
- Time-to-first-relevant-result ↓ (s)
- Conversion rate ↑ (%)
- Lead qualification accuracy ↑ (%)
- Search abandonment rate ↓ (%)
- User satisfaction rating ↑ (%)
- Average rank position of relevant items ↑
- Manual re-sorting actions ↓ (%)

**Supporting Technical Metrics:** NDCG@K, MAP@K, Precision@K

---

## 5. Recommendation
**Business Goal:** Personalize experiences to increase engagement, retention, or sales.

**Primary Business KPIs:**
- CTR ↑ (%)
- CVR ↑ (%)
- Average order value ↑ (%)
- Customer retention rate ↑ (%)
- Cross-sell / upsell rate ↑ (%)
- Session engagement duration ↑ (%)
- Churn rate ↓ (%)
- Customer satisfaction (survey %) ↑

**Supporting Technical Metrics:** Recall@K, MAP@K, NDCG@K

---

## 6. Clustering
**Business Goal:** Identify meaningful groups to drive marketing, targeting, or optimization.

**Primary Business KPIs:**
- Segment-driven campaign ROI ↑ (%)
- Response rate within key segments ↑ (%)
- Retention uplift within top segments (%)
- Revenue per segment ↑ (%)
- Targeting cost ↓ (%)
- Conversion uplift from personalization (%)
- CLV per segment ↑ (%)
- Time-to-deploy targeted actions ↓ (%)

**Supporting Technical Metrics:** Silhouette Score, DBI, CH Score

---

## 7. Anomaly Detection
**Business Goal:** Detect and mitigate rare or high-risk events early.

**Primary Business KPIs:**
- Fraud loss ↓ (%)
- Detection latency ↓ (hours / transactions)
- False-positive handling cost ↓ (%)
- Incidents prevented (# / month)
- Compliance violation rate ↓ (%)
- Time-to-response ↓ (%)
- System reliability uptime ↑ (%)
- Customer trust / complaint rate ↓ (%)

**Supporting Technical Metrics:** Precision, Recall, F1, Detection latency

---

## 8. Policy / Reinforcement Learning
**Business Goal:** Continuously optimize operational or strategic decisions through feedback.

**Primary Business KPIs:**
- ROI improvement vs baseline (%)
- Operational cost per action ↓ (%)
- Reward gain per iteration ↑ (%)
- Policy convergence time (weeks)
- Efficiency per decision ↑ (%)
- Human intervention frequency ↓ (%)
- Long-term performance gain (%)
- Decision automation coverage ↑ (%)

**Supporting Technical Metrics:** Average Reward, Regret, Success Rate

---

## 9. Rules / Non-ML
**Business Goal:** Achieve efficiency and transparency through deterministic automation.

**Primary Business KPIs:**
- Rule execution success rate (%)
- Policy compliance rate (%)
- Manual override frequency ↓ (%)
- Average rule latency (ms)
- Rule coverage completeness (%)
- Maintenance cost ↓ (%)
- Workflow uptime ↑ (%)
- Business exception handling time ↓ (%)

**Supporting Technical Metrics:** None required

---

## 10. Guidance
- Always include **at least one KPI** from each dimension:
    - 💰 Financial — revenue ↑, cost ↓, ROI ↑
    - ⚙️ Operational — speed ↑, accuracy ↑, efficiency ↑
    - 👥 Experience — satisfaction ↑, complaints ↓, retention ↑
- Quantify all goals relative to current baselines.
- Technical metrics validate feasibility, not value.
- Non-ML baselines must use comparable business KPIs.
- Each pilot decision should cite 3–6 of these metrics.

---

_End of metrics-library.md_
