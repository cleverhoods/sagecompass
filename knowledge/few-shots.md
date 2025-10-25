# SageCompass – Few-Shot Examples
_instructions v2.1_

These examples show how SageCompass applies the ML Success Criteria Framework to different business challenges.  
Each example includes concise input and valid structured JSON output.

---

## Example 1 – Classification
**Input:**  
Detect whether customer reviews are positive, neutral, or negative.

**Expected Output:**
```json
{
  "needs_ml": "yes",
  "problem_type": "classification",
  "learning_paradigm": "supervised",
  "business_kpis": [{"name": "sentiment_accuracy", "unit": "%", "target": "≥90"}],
  "ml_recommendations": [{"approach": "text classification (fine-tuned BERT)", "why": "learns sentiment patterns from labeled data"}],
  "decision": "proceed"
}
```

---

## Example 2 – Regression
**Input:**  
Predict the delivery time of each order based on distance and traffic.

**Expected Output:**
```json
{
  "needs_ml": "yes",
  "problem_type": "regression",
  "learning_paradigm": "supervised",
  "business_kpis": [{"name": "delivery_time_mae", "unit": "minutes", "target": "≤5"}],
  "ml_recommendations": [{"approach": "gradient-boosted regression", "why": "handles nonlinear numeric relationships"}],
  "decision": "proceed"
}
```

---

## Example 3 – Forecasting
**Input:**  
Forecast next month’s hotel occupancy.

**Expected Output:**
```json
{
  "needs_ml": "yes",
  "problem_type": "forecasting",
  "learning_paradigm": "supervised",
  "business_kpis": [{"name": "occupancy_forecast_error", "unit": "%", "target": "≤10"}],
  "ml_recommendations": [{"approach": "time-series regression (ARIMA or Prophet)", "why": "captures temporal and seasonal trends"}],
  "decision": "proceed"
}
```

---

## Example 4 – Recommendation
**Input:**  
Recommend products based on a user’s browsing and purchase history.

**Expected Output:**
```json
{
  "needs_ml": "yes",
  "problem_type": "recommendation",
  "learning_paradigm": "supervised",
  "business_kpis": [{"name": "click_through_rate", "unit": "%", "target": "≥15"}],
  "ml_recommendations": [{"approach": "collaborative filtering", "why": "learns similarity patterns across users and items"}],
  "decision": "proceed"
}
```

---

## Example 5 – Clustering
**Input:**  
Group customers by behavior to create targeted marketing campaigns.

**Expected Output:**
```json
{
  "needs_ml": "yes",
  "problem_type": "clustering",
  "learning_paradigm": "unsupervised",
  "business_kpis": [{"name": "segment_actionability", "unit": "qualitative", "target": "high"}],
  "ml_recommendations": [{"approach": "k-means clustering", "why": "discovers natural customer groups without labels"}],
  "decision": "proceed"
}
```

---

## Example 6 – Anomaly Detection
**Input:**  
Detect fraudulent transactions in the payment system.

**Expected Output:**
```json
{
  "needs_ml": "yes",
  "problem_type": "anomaly",
  "learning_paradigm": "unsupervised",
  "business_kpis": [{"name": "fraud_detection_f1", "unit": "score", "target": "≥0.85"}],
  "ml_recommendations": [{"approach": "isolation forest", "why": "detects outliers with minimal assumptions"}],
  "decision": "proceed"
}
```

---

## Example 7 – Reinforcement Learning
**Input:**  
Continuously optimize ad bidding to maximize return while staying within budget.

**Expected Output:**
```json
{
  "needs_ml": "yes",
  "problem_type": "policy",
  "learning_paradigm": "reinforcement",
  "business_kpis": [{"name": "average_reward", "unit": "USD", "target": "≥1.2x baseline"}],
  "ml_recommendations": [{"approach": "reinforcement learning (Q-learning or PPO)", "why": "optimizes sequential decisions under feedback"}],
  "decision": "proceed"
}
```

---

## Example 8 – Non-ML Case
**Input:**  
Send an email to every inactive user.

**Expected Output:**
```json
{
  "needs_ml": "no",
  "problem_type": "rules",
  "learning_paradigm": "none",
  "decision": "dont_use_ml"
}
```

---

## Example 9 – Ambiguous Request
**Input:**  
Use AI to improve our customer service.

**Expected Output:**
```json
{
  "needs_ml": "unclear",
  "problem_type": "unknown",
  "pending_question": "What specific outcome in customer service are you trying to improve (e.g., response time, ticket routing, satisfaction)?"
}
```

---

## Example 10 – Bad-Fit Case
**Input:**  
Predict next month’s sales using if-else rules.

**Expected Output:**
```json
{
  "needs_ml": "no",
  "problem_type": "rules",
  "learning_paradigm": "none",
  "decision": "dont_use_ml",
  "pending_question": "Do you intend to predict future numeric values or just apply fixed thresholds?"
}
```

---

_End of few-shots.md_
