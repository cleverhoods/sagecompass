# SageCompass – Metrics Library
_instructions v3.0_

Defines business and technical success criteria for evaluating ML and non-ML project value.  
Each archetype lists **primary business KPIs**, **synthetic KPI templates**, and **supporting technical metrics**.  
All values are indicative and may be estimated or tagged `[Unverified]` during reasoning.

---

## 1. Classification
**Business Goal:** Automate or improve accuracy of categorical decisions.

**Primary Business KPIs**
- Percentage of manual decisions automated (%)
- Processing time per case reduction (%)
- Operational cost per decision reduction (%)
- Accuracy of business-critical decisions (%)
- False alert or complaint rate reduction (%)
- Compliance adherence improvement (%)
- Throughput per analyst increase (%)
- SLA adherence improvement (%)

**Synthetic KPI Templates**
| Name | Formula | Unit | Purpose |
|------|----------|------|---------|
| Cost Savings from Automation | cases_automated × avg_cost_per_case | currency | financial_projection |
| Analyst Productivity Index | throughput_after / throughput_before | index | scaling_projection |
| Complaint Avoidance Ratio | 1 - (false_alert_rate_after / false_alert_rate_before) | % | data_quality_proxy |

**Supporting Technical Metrics**
Accuracy, Precision, Recall, F1, ROC-AUC

---

## 2. Regression
**Business Goal:** Predict numeric outcomes to optimize efficiency, planning, or cost.

**Primary Business KPIs**
- Forecast deviation from target reduction (%)
- Resource allocation efficiency increase (%)
- Cost forecast error reduction (%)
- Operational waste reduction (%)
- SLA breach rate reduction (%)
- Unit cost per output reduction (%)
- Planning cycle time reduction (%)
- Profit margin stability increase (%)

**Synthetic KPI Templates**
| Name | Formula | Unit | Purpose |
|------|----------|------|---------|
| Forecast Value Gain | (baseline_error − model_error) × avg_financial_impact_per_unit | currency | financial_projection |
| Planning Efficiency Ratio | planned_output / resource_spent | index | illustrative |

**Supporting Technical Metrics**
MAE, RMSE, R², MAPE

---

## 3. Forecasting
**Business Goal:** Anticipate future demand or events to guide proactive decisions.

**Primary Business KPIs**
- Demand–supply mismatch reduction (%)
- Stockout frequency reduction (%)
- Inventory waste reduction (%)
- Forecast-driven profit uplift (%)
- Schedule adherence improvement (%)
- Production overcapacity reduction (%)
- Revenue volatility reduction (%)
- Planning accuracy improvement (%)

**Synthetic KPI Templates**
| Name | Formula | Unit | Purpose |
|------|----------|------|---------|
| Expected Profit Uplift | (forecast_accuracy − baseline_accuracy) × avg_margin_per_unit × volume | currency | financial_projection |
| Inventory Stability Score | 1 − (stockout_rate + overcapacity_rate) | index | kpi_bridge |

**Supporting Technical Metrics**
MAPE, RMSE, Forecast Bias

---

## 4. Ranking
**Business Goal:** Optimize ordering or prioritization (search, leads, or task queues).

**Primary Business KPIs**
- Click-through rate (CTR) increase (%)
- Time-to-first-relevant-result reduction (seconds)
- Conversion rate increase (%)
- Lead qualification accuracy increase (%)
- Search abandonment rate reduction (%)
- User satisfaction rating increase (%)
- Average rank position improvement
- Manual re-sorting actions reduction (%)

**Synthetic KPI Templates**
| Name | Formula | Unit | Purpose |
|------|----------|------|---------|
| Engagement Gain | (ctr_after − ctr_before) × users | % | financial_projection |
| Ranking Efficiency | relevant_at_topK / total_relevant | score | benchmark_alignment |

**Supporting Technical Metrics**
NDCG@K, MAP@K, Precision@K

---

## 5. Recommendation
**Business Goal:** Personalize experiences to increase engagement, retention, or sales.

**Primary Business KPIs**
- CTR increase (%)
- CVR increase (%)
- Average order value increase (%)
- Customer retention rate increase (%)
- Cross-sell or upsell rate increase (%)
- Session engagement duration increase (%)
- Churn rate reduction (%)
- Customer satisfaction increase (%)

**Synthetic KPI Templates**
| Name | Formula | Unit | Purpose |
|------|----------|------|---------|
| Expected Revenue Uplift | (cvr_after − cvr_before) × avg_order_value × impressions | currency | financial_projection |
| Retention-Driven ROI | retention_gain × avg_margin_per_user | currency | kpi_bridge |
| Personalization Index | engagement_time_after / engagement_time_before | index | illustrative |

**Supporting Technical Metrics**
Recall@K, MAP@K, NDCG@K

---

## 6. Clustering
**Business Goal:** Identify meaningful groups to drive marketing, targeting, or optimization.

**Primary Business KPIs**
- Segment-driven campaign ROI increase (%)
- Response rate within key segments increase (%)
- Retention uplift within top segments (%)
- Revenue per segment increase (%)
- Targeting cost reduction (%)
- Conversion uplift from personalization (%)
- CLV per segment increase (%)
- Time-to-deploy targeted actions reduction (%)

**Synthetic KPI Templates**
| Name | Formula | Unit | Purpose |
|------|----------|------|---------|
| Segment ROI Gain | (campaign_roi_after − campaign_roi_before) | currency | financial_projection |
| Targeting Efficiency | response_rate_top_segment / avg_response_rate | index | benchmark_alignment |

**Supporting Technical Metrics**
Silhouette Score, Davies–Bouldin Index, Calinski–Harabasz Score

---

## 7. Anomaly Detection
**Business Goal:** Detect and mitigate rare or high-risk events early.

**Primary Business KPIs**
- Fraud loss reduction (%)
- Detection latency reduction (hours)
- False-positive handling cost reduction (%)
- Incidents prevented per month (#)
- Compliance violation rate reduction (%)
- Time-to-response reduction (%)
- System uptime increase (%)
- Complaint rate improvement (%)

**Synthetic KPI Templates**
| Name | Formula | Unit | Purpose |
|------|----------|------|---------|
| Loss Avoidance Value | incidents_prevented × avg_loss_per_incident | currency | financial_projection |
| Detection Benefit Ratio | (baseline_latency / model_latency) | index | illustrative |

**Supporting Technical Metrics**
Precision, Recall, F1, Detection Latency

---

## 8. Policy / Reinforcement Learning
**Business Goal:** Continuously optimize operational or strategic decisions through feedback.

**Primary Business KPIs**
- ROI improvement vs baseline (%)
- Operational cost per action reduction (%)
- Reward gain per iteration increase (%)
- Policy convergence time (weeks)
- Efficiency per decision increase (%)
- Human intervention frequency reduction (%)
- Long-term performance gain (%)
- Decision automation coverage increase (%)

**Synthetic KPI Templates**
| Name | Formula | Unit | Purpose |
|------|----------|------|---------|
| Reward Improvement Index | reward_after / reward_before | index | scaling_projection |
| Policy Efficiency Gain | (cost_per_action_baseline − cost_per_action_new) / cost_per_action_baseline | % | financial_projection |

**Supporting Technical Metrics**
Average Reward, Regret, Success Rate

---

## 9. Rules / Non-ML
**Business Goal:** Achieve efficiency and transparency through deterministic automation.

**Primary Business KPIs**
- Rule execution success rate (%)
- Policy compliance rate (%)
- Manual override frequency reduction (%)
- Average rule latency (ms)
- Rule coverage completeness (%)
- Maintenance cost reduction (%)
- Workflow uptime increase (%)
- Exception handling time reduction (%)

**Synthetic KPI Templates**
| Name | Formula | Unit | Purpose |
|------|----------|------|---------|
| Automation ROI | (manual_hours_saved × hourly_cost) − maintenance_cost | currency | financial_projection |
| Stability Index | rule_failures / total_rules | index | data_quality_proxy |

**Supporting Technical Metrics**
None required

---

## 10. KPI Lens Mapping
Each evaluation should cover at least one KPI from each dimension:
- **Financial** → revenue increase, cost reduction, ROI improvement
- **Operational** → speed, accuracy, efficiency gains
- **Experience** → satisfaction, retention, complaint reduction

All goals must be **quantified vs baseline**.  
Technical metrics validate feasibility, not value.  
Synthetic KPIs connect technical improvement to measurable impact.

---

_End of metrics-library.md_
