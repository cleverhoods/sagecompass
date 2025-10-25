# SageCompass – Problem Archetypes
_instructions v2.2_

Defines common machine learning problem types, their business manifestations, and common misapplications.  
SageCompass uses this reference to map natural-language challenges into correct ML archetypes, detect false positives, and reduce unnecessary ML usage.

---

## 1. Classification

**Goal:**  
Assign discrete labels or categories to inputs based on observed examples.

**Learning Paradigm:**  
Supervised

**Typical Metrics:**  
Accuracy, Precision, Recall, F1, ROC-AUC, Log-loss

**Business Cues (Good Fit):**
- Detect whether a transaction is fraudulent or legitimate.
- Classify tickets or messages by topic or intent.
- Determine whether a part is defective.
- Identify which customers are likely to churn.
- Categorize sentiment (positive, neutral, negative).

**Good Examples:**
- Email spam detection
- Customer churn prediction
- Product defect detection from image data
- Sentiment classification on reviews

**Bad Examples:**
- “Calculate total revenue per month.” → numeric output → regression
- “Sort customers alphabetically.” → deterministic rule → not ML

---

## 2. Regression

**Goal:**  
Predict continuous numeric outcomes based on input features.

**Learning Paradigm:**  
Supervised

**Typical Metrics:**  
MAE, RMSE, R², MAPE

**Business Cues (Good Fit):**
- Estimate delivery time or cost
- Predict monthly sales or revenue
- Forecast customer lifetime value
- Estimate house prices
- Predict time to resolve a support ticket

**Good Examples:**
- Forecasting revenue by region
- Predicting housing prices
- Estimating repair time from service logs
- Predicting loan amount recovery rate

**Bad Examples:**
- “Predict if a customer will churn.” → classification
- “Group customers by behavior.” → clustering

---

## 3. Forecasting (Time-Series Regression)

**Goal:**  
Predict future numeric values from temporally ordered historical data.

**Learning Paradigm:**  
Supervised (sequence modeling)

**Typical Metrics:**  
MAE, RMSE, MAPE, SMAPE, seasonal error

**Business Cues (Good Fit):**
- Forecast next month’s demand or traffic
- Predict daily sales or web visits
- Estimate electricity or energy consumption
- Forecast inventory or staffing needs
- Predict patient admissions per week

**Good Examples:**
- Demand forecasting for retail products
- Power consumption prediction
- Stock level forecasting
- Predicting call-center volume by day

**Bad Examples:**
- “Classify transactions as fraudulent or not.” → classification
- “Segment users by behavior.” → clustering

---

## 4. Ranking

**Goal:**  
Order or prioritize items based on relevance or importance.

**Learning Paradigm:**  
Supervised (pointwise or pairwise)

**Typical Metrics:**  
NDCG, MAP, Precision@K, Recall@K

**Business Cues (Good Fit):**
- Show the most relevant products or articles first
- Prioritize leads for sales follow-up
- Rank job candidates or suppliers
- Order support tickets by urgency
- Optimize content recommendations by relevance score

**Good Examples:**
- Search engine results ranking
- Prioritizing leads in CRM systems
- Ranking articles for personalization

**Bad Examples:**
- “Predict customer churn probability.” → classification
- “Calculate average time to resolve.” → regression

---

## 5. Recommendation

**Goal:**  
Suggest items, actions, or content likely to interest a user based on behavior or similarity.

**Learning Paradigm:**  
Supervised or hybrid (collaborative + content-based)

**Typical Metrics:**  
Precision@K, Recall@K, Hit Rate, Coverage, Diversity, MAP

**Business Cues (Good Fit):**
- Recommend products or content to users
- Suggest next best action or offer
- Generate personalized playlists or bundles
- Help users discover related items
- Provide content tailored to behavior

**Good Examples:**
- Product recommendations in e-commerce
- Movie or music recommender systems
- Personalized news or blog feeds

**Bad Examples:**
- “Predict total sales next month.” → regression
- “Segment customers into groups.” → clustering

---

## 6. Clustering

**Goal:**  
Group similar data points together without predefined labels.

**Learning Paradigm:**  
Unsupervised

**Typical Metrics:**  
Silhouette Score, Davies–Bouldin Index, Calinski–Harabasz Score

**Business Cues (Good Fit):**
- Segment customers by behavior or demographics
- Group products by similarity or purchase pattern
- Discover hidden patterns in survey responses
- Group users by app activity
- Cluster log events by type

**Good Examples:**
- Customer segmentation for marketing
- Grouping similar products
- Detecting behavior clusters in analytics data

**Bad Examples:**
- “Predict next week’s demand.” → forecasting
- “Classify reviews as positive or negative.” → classification

---

## 7. Anomaly Detection

**Goal:**  
Identify rare, unexpected, or abnormal patterns compared to typical data behavior.

**Learning Paradigm:**  
Unsupervised or semi-supervised

**Typical Metrics:**  
Precision, Recall, F1, False Positive Rate, ROC-AUC

**Business Cues (Good Fit):**
- Detect fraudulent transactions or account activity
- Identify defective products in production
- Detect abnormal system performance
- Spot security breaches or intrusion attempts
- Detect unexpected sensor readings

**Good Examples:**
- Credit card fraud detection
- Network intrusion detection
- Equipment failure detection

**Bad Examples:**
- “Group users by preference.” → clustering
- “Predict sales for next quarter.” → forecasting

---

## 8. Policy / Reinforcement Learning

**Goal:**  
Learn and optimize actions through trial, feedback, or simulated environments.

**Learning Paradigm:**  
Reinforcement

**Typical Metrics:**  
Cumulative Reward, Average Reward, Regret, Success Rate

**Business Cues (Good Fit):**
- Continuously optimize decisions or strategies
- Adapt to user feedback over time
- Balance exploration and exploitation
- Automate sequential decision-making
- Train an agent to interact with an environment

**Good Examples:**
- Dynamic pricing optimization
- Ad bidding strategy learning
- Game-playing agents
- Robotic control tasks

**Bad Examples:**
- “Predict customer churn once.” → classification
- “Cluster customers.” → unsupervised static grouping

---

## 9. Rules / Non-ML

**Goal:**  
Use deterministic or statistical logic to achieve predictable output without learning.

**Learning Paradigm:**  
None (explicit rules)

**Typical Metrics:**  
None (logic-driven)

**Business Cues (Good Fit):**
- “If X then Y” workflows
- Threshold or rule-based decisions
- Simple aggregations or filters
- Counting, summing, sorting
- Business rules that don’t require adaptation

**Good Examples:**
- Alert if sales drop below a threshold
- Count users by region
- Trigger email if status = "inactive"

**Bad Examples:**
- “Predict future demand using if-statements.” → forecasting
- “Use threshold to detect sentiment.” → classification required

---

## How SageCompass Uses This

- When user input matches **Business Cues**, assign `problem_type` and infer `learning_paradigm`.
- Compare intent: if it resembles **Bad Examples**, return `"problem_type": "rules"` and `"ml_justified": "no"`.
- If multiple archetypes match, ask one clarifying question.
- If none match, return `"problem_type": "unknown"` and `"ml_justified": "unclear"`.
- Always prefer the simplest approach that fulfills measurable KPIs.

---

_End of problem-archetypes.md_
