# SageCompass – Problem Archetypes
_instructions v3.0_

Defines standardized ML problem families with explicit guidance for business fit, expected data, and common misapplications.  
SageCompass uses this reference to classify business challenges, recommend the correct ML archetype, and detect when a rule-based or simpler method is more appropriate.

---

## 1. Classification

**Goal:**  
Assign discrete labels or categories to inputs based on observed examples.

**Learning Paradigm:**  
Supervised

**Typical Metrics:**  
Accuracy, Precision, Recall, F1, ROC-AUC, Log-loss

**Business Cues (Good Fit):**
- Detect fraudulent vs. legitimate transactions
- Identify which customers are likely to churn
- Categorize text tickets or messages by topic
- Determine defective products or quality issues
- Classify sentiment (positive / neutral / negative)

**Good Examples:**
- Email spam detection
- Customer churn prediction
- Product defect detection from image data
- Sentiment classification on reviews

**Bad Examples:**
- “Calculate total revenue per month.” → numeric output → regression
- “Sort customers alphabetically.” → deterministic → not ML

**Expected Data**
| Aspect | Requirement |
|---------|-------------|
| Label | categorical (binary or multiclass) |
| Features | encoded categorical and numeric predictors |
| Granularity | one record per entity (user, transaction, case) |
| Sample size | ≥ 10 000 for binary, ≥ 50 000 for multiclass |

**Recommended Technical Metrics:** Accuracy, Recall, F1, ROC-AUC  
**Common Business KPIs:** decision accuracy, automation rate, cost per error  
**Non-ML Alternatives:** rule filters, lookup tables, threshold logic

---

## 2. Regression

**Goal:**  
Predict continuous numeric outcomes from structured inputs.

**Learning Paradigm:**  
Supervised

**Typical Metrics:**  
MAE, RMSE, R², MAPE

**Business Cues (Good Fit):**
- Estimate delivery time or cost
- Predict monthly sales or revenue
- Forecast customer lifetime value
- Estimate housing or asset prices

**Good Examples:**
- Forecasting regional revenue
- Predicting housing prices
- Estimating repair time from logs

**Bad Examples:**
- “Predict if a customer will churn.” → classification
- “Group customers by behavior.” → clustering

**Expected Data**
| Aspect | Requirement |
|---------|-------------|
| Label | continuous numeric |
| Features | historical, contextual, or operational variables |
| Granularity | one record per event or entity |
| Sample size | ≥ 10 000 |

**Recommended Technical Metrics:** MAE, RMSE, R²  
**Common Business KPIs:** forecast deviation, cost prediction accuracy, efficiency gain  
**Non-ML Alternatives:** spreadsheet regression, linear rules, heuristic formulas

---

## 3. Forecasting (Time-Series Regression)

**Goal:**  
Predict future numeric values from temporally ordered historical data.

**Learning Paradigm:**  
Supervised (sequence modeling)

**Typical Metrics:**  
MAE, RMSE, MAPE, SMAPE, Forecast Bias

**Business Cues (Good Fit):**
- Forecast next month’s demand or traffic
- Predict daily sales or web visits
- Estimate energy consumption or production
- Forecast staffing or call-center volume

**Good Examples:**
- Demand forecasting for retail
- Power consumption prediction
- Stock level forecasting

**Bad Examples:**
- “Classify transactions as fraudulent.” → classification
- “Segment users by behavior.” → clustering

**Expected Data**
| Aspect | Requirement |
|---------|-------------|
| Label | numeric, indexed by time |
| Features | lagged variables, seasonality, external signals |
| Granularity | hourly, daily, weekly, or monthly |
| Sample size | ≥ 24–36 time points per series |

**Recommended Technical Metrics:** MAPE, RMSE  
**Common Business KPIs:** forecast accuracy, inventory waste reduction, revenue volatility decrease  
**Non-ML Alternatives:** moving average, ARIMA, exponential smoothing

---

## 4. Ranking

**Goal:**  
Order or prioritize items based on predicted relevance or importance.

**Learning Paradigm:**  
Supervised (pointwise or pairwise)

**Typical Metrics:**  
NDCG@K, MAP@K, Precision@K

**Business Cues (Good Fit):**
- Show the most relevant results first
- Prioritize leads or candidates
- Rank support tickets by urgency
- Optimize recommendation relevance

**Good Examples:**
- Search-result ranking
- Lead prioritization in CRM
- Ranking articles for personalization

**Bad Examples:**
- “Predict churn probability.” → classification
- “Compute average handle time.” → regression

**Expected Data**
| Aspect | Requirement |
|---------|-------------|
| Label | ordinal or binary relevance |
| Features | user/query context + item attributes |
| Granularity | record per item-query pair |
| Sample size | ≥ 100 000 pairs typical |

**Recommended Technical Metrics:** NDCG@K, MAP@K  
**Common Business KPIs:** CTR, conversion uplift, satisfaction index  
**Non-ML Alternatives:** static weighting, manual sorting rules

---

## 5. Recommendation

**Goal:**  
Suggest items or content likely to interest a user.

**Learning Paradigm:**  
Supervised or hybrid (collaborative + content)

**Typical Metrics:**  
Precision@K, Recall@K, Hit Rate, Coverage, Diversity

**Business Cues (Good Fit):**
- Recommend products, offers, or content
- Suggest next best action
- Personalize feeds or playlists

**Good Examples:**
- Product recommendations in e-commerce
- Movie or music recommendation
- Personalized news feeds

**Bad Examples:**
- “Predict total sales next month.” → regression
- “Segment customers.” → clustering

**Expected Data**
| Aspect | Requirement |
|---------|-------------|
| Label | implicit or explicit user-item interactions |
| Features | user profile, item attributes, interaction context |
| Granularity | user-item pair |
| Sample size | ≥ 1 000 000 interactions recommended |

**Recommended Technical Metrics:** Recall@K, NDCG@K  
**Common Business KPIs:** CTR, CVR, average order value, retention uplift  
**Non-ML Alternatives:** popularity ranking, manual cross-sell rules

---

## 6. Clustering

**Goal:**  
Group similar entities without predefined labels.

**Learning Paradigm:**  
Unsupervised

**Typical Metrics:**  
Silhouette Score, Davies–Bouldin Index, Calinski–Harabasz Score

**Business Cues (Good Fit):**
- Segment customers by behavior or demographics
- Group products by similarity or pattern
- Discover hidden patterns in survey or event data

**Good Examples:**
- Customer segmentation for marketing
- Product similarity grouping
- Behavior clustering in analytics

**Bad Examples:**
- “Predict next week’s demand.” → forecasting
- “Classify reviews by sentiment.” → classification

**Expected Data**
| Aspect | Requirement |
|---------|-------------|
| Label | none |
| Features | numeric or encoded categorical features |
| Granularity | one record per entity |
| Sample size | ≥ 5 000 typical |

**Recommended Technical Metrics:** Silhouette Score  
**Common Business KPIs:** campaign ROI by segment, conversion uplift  
**Non-ML Alternatives:** manual grouping, rule-based segmentation

---

## 7. Anomaly Detection

**Goal:**  
Detect rare or abnormal patterns compared to normal data behavior.

**Learning Paradigm:**  
Unsupervised or semi-supervised

**Typical Metrics:**  
Precision, Recall, F1, False-Positive Rate, ROC-AUC

**Business Cues (Good Fit):**
- Detect fraud or abnormal transactions
- Identify defective products or outliers
- Monitor systems for irregular performance

**Good Examples:**
- Credit-card fraud detection
- Network intrusion detection
- Equipment failure detection

**Bad Examples:**
- “Group users by preference.” → clustering
- “Predict sales next quarter.” → forecasting

**Expected Data**
| Aspect | Requirement |
|---------|-------------|
| Label | optional (few positive cases) |
| Features | numeric signals, logs, sensor data |
| Granularity | per transaction or time window |
| Sample size | highly unbalanced, need large normal set |

**Recommended Technical Metrics:** F1, ROC-AUC  
**Common Business KPIs:** fraud loss reduction, detection latency improvement  
**Non-ML Alternatives:** rule thresholds, control charts

---

## 8. Policy / Reinforcement Learning

**Goal:**  
Learn and optimize actions through feedback and iterative interaction.

**Learning Paradigm:**  
Reinforcement

**Typical Metrics:**  
Cumulative Reward, Average Reward, Regret, Success Rate

**Business Cues (Good Fit):**
- Continuous optimization of dynamic decisions
- Strategy learning from feedback
- Sequential automation of control processes

**Good Examples:**
- Dynamic pricing optimization
- Ad bidding strategy learning
- Robotic control agent training

**Bad Examples:**
- “Predict churn once.” → classification
- “Cluster customers.” → unsupervised grouping

**Expected Data**
| Aspect | Requirement |
|---------|-------------|
| Label | reward signal per action |
| Features | state, action, reward, next-state tuples |
| Granularity | per timestep or episode |
| Sample size | ≥ 10 000 episodes minimum |

**Recommended Technical Metrics:** Average Reward, Regret  
**Common Business KPIs:** ROI improvement, cost per action reduction  
**Non-ML Alternatives:** heuristic policies, static decision tables

---

## 9. Rules / Non-ML

**Goal:**  
Execute deterministic logic for predictable outcomes without learning.

**Learning Paradigm:**  
None (explicit logic)

**Typical Metrics:**  
None (logic-based)

**Business Cues (Good Fit):**
- Threshold or condition-based automation
- Counting, filtering, or aggregating
- Static workflows with fixed decisions

**Good Examples:**
- Alert if sales drop below a threshold
- Count users by region
- Trigger email when status = “inactive”

**Bad Examples:**
- “Predict future demand with if-statements.” → forecasting
- “Detect sentiment using keyword threshold only.” → classification needed

**Expected Data**
| Aspect | Requirement |
|---------|-------------|
| Label | N/A |
| Features | N/A |
| Granularity | per rule trigger |
| Sample size | irrelevant |

**Recommended Technical Metrics:** None  
**Common Business KPIs:** rule uptime, latency, override frequency  
**Non-ML Alternatives:** same category (rules themselves)

---

## How SageCompass Uses This

- Match **Business Cues** to infer `problem_type` and `learning_paradigm`.
- Use **Expected Data** and **Typical Metrics** for Stage 3 and Stage 4 reasoning.
- When user text resembles **Bad Examples**, set `"ml_justified": "no"` and recommend a simpler approach.
- If multiple fits are detected, include all in `solution_alignment.problem_types` with confidence values.
- Prefer the **simplest method** that achieves measurable business KPIs.

---

_End of problem-archetypes.md_
