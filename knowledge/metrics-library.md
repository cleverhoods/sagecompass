# SageCompass – Metrics Library (Business-Focused)
_instructions v2.1_

Defines business-level success criteria for evaluating ML project value.  
Each archetype lists **primary business KPIs** (stakeholder-facing) and **supporting technical metrics** (internal validation).

---

## 1. Classification
**Business Goal:** Automate or improve accuracy of categorical decisions.

**Primary Business KPIs:**
- Percentage of manual decisions automated
- Processing time per case reduction (%)
- Operational cost per decision reduction (%)
- Accuracy of business-critical decisions (%)
- False alert or complaint rate reduction (%)
- Compliance adherence improvement (%)
- Throughput per analyst increase (%)
- SLA adherence improvement (%)

**Supporting Technical Metrics:**  
Accuracy, Precision, Recall, F1, ROC-AUC

---

## 2. Regression
**Business Goal:** Predict numeric outcomes to optimize efficiency, planning, or cost.

**Primary Business KPIs:**
- Forecast deviation from target reduction (%)
- Resource allocation efficiency increase (%)
- Cost forecast error reduction (%)
- Operational waste reduction (%)
- SLA breach rate reduction (%)
- Unit cost per output reduction (%)
- Planning cycle time reduction (%)
- Profit margin stability increase (%)

**Supporting Technical Metrics:**  
MAE, RMSE, R², MAPE

---

## 3. Forecasting
**Business Goal:** Anticipate future demand or events to guide proactive decisions.

**Primary Business KPIs:**
- Demand-supply mismatch reduction (%)
- Stockout frequency reduction (%)
- Inventory waste reduction (%)
- Forecast-driven profit uplift (%)
- Schedule adherence improvement (%)
- Production overcapacity reduction (%)
- Revenue volatility reduction (%)
- Planning accuracy improvement (%)

**Supporting Technical Metrics:**  
MAPE, RMSE, Forecast Bias

---

## 4. Ranking
**Business Goal:** Optimize ordering or prioritization (search, leads, or task queues).

**Primary Business KPIs:**
- Click-through rate (CTR) increase (%)
- Time-to-first-relevant-result reduction (seconds)
- Conversion rate increase (%)
- Lead qualification accuracy increase (%)
- Search abandonment rate reduction (%)
- User satisfaction rating increase (%)
- Average rank position of relevant items improvement
- Manual re-sorting actions reduction (%)

**Supporting Technical Metrics:**  
NDCG@K, MAP@K, Precision@K

---

## 5. Recommendation
**Business Goal:** Personalize experiences to increase engagement, retention, or sales.

**Primary Business KPIs:**
- Click-through rate (CTR) increase (%)
- Conversion rate (CVR) increase (%)
- Average order value increase (%)
- Customer retention rate increase (%)
- Cross-sell or upsell rate increase (%)
- Session engagement duration increase (%)
- Churn rate reduction (%)
- Customer satisfaction (survey %) increase (%)

**Supporting Technical Metrics:**  
Recall@K, MAP@K, NDCG@K

---

## 6. Clustering
**Business Goal:** Identify meaningful groups to drive marketing, targeting, or optimization.

**Primary Business KPIs:**
- Segment-driven campaign ROI increase (%)
- Response rate within key segments increase (%)
- Retention uplift within top segments (%)
- Revenue per segment increase (%)
- Targeting cost reduction (%)
- Conversion uplift from personalization (%)
- CLV per segment increase (%)
- Time-to-deploy targeted actions reduction (%)

**Supporting Technical Metrics:**  
Silhouette Score, Davies–Bouldin Index, Calinski–Harabasz Score

---

## 7. Anomaly Detection
**Business Goal:** Detect and mitigate rare or high-risk events early.

**Primary Business KPIs:**
- Fraud loss reduction (%)
- Detection latency reduction (hours or transactions)
- False-positive handling cost reduction (%)
- Incidents prevented per month (#)
- Compliance violation rate reduction (%)
- Time-to-response reduction (%)
- System reliability uptime increase (%)
- Customer trust and complaint rate improvement (%)

**Supporting Technical Metrics:**  
Precision, Recall, F1, Detection Latency

---

## 8. Policy / Reinforcement Learning
**Business Goal:** Continuously optimize operational or strategic decisions through feedback.

**Primary Business KPIs:**
- ROI improvement versus baseline (%)
- Operational cost per action reduction (%)
- Reward gain per iteration increase (%)
- Policy convergence time (weeks)
- Efficiency per decision increase (%)
- Human intervention frequency reduction (%)
- Long-term performance gain (%)
- Decision automation coverage increase (%)

**Supporting Technical Metrics:**  
Average Reward, Regret, Success Rate

---

## 9. Rules / Non-ML
**Business Goal:** Achieve efficiency and transparency through deterministic automation.

**Primary Business KPIs:**
- Rule execution success rate (%)
- Policy compliance rate (%)
- Manual override frequency reduction (%)
- Average rule latency (ms)
- Rule coverage completeness (%)
- Maintenance cost reduction (%)
- Workflow uptime increase (%)
- Business exception handling time reduction (%)

**Supporting Technical Metrics:**  
None required

---

## 10. Guidance
- Always include at least one KPI from each dimension:
    - Financial — revenue increase, cost reduction, ROI improvement
    - Operational — speed increase, accuracy improvement, efficiency improvement
    - Experience — satisfaction increase, complaints reduction, retention increase
- Quantify all goals relative to current baselines.
- Technical metrics validate feasibility, not value.
- Non-ML baselines must use comparable business KPIs.
- Each pilot decision should cite three to six of these metrics.

---

_End of metrics-library.md_
