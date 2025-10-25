# SageCompass – Few-Shot Examples
_instructions v1.2_

These examples illustrate how SageCompass evaluates ML necessity and produces structured JSON output.

---

## Example 1 – Support Response Time

**Input:**  
Evaluate if we need ML to reduce first-response time in support by 30%.

**Expected Output (JSON):**
```json
{
  "needs_ml": "no",
  "business_kpis": [
    { "name": "average_response_time", "unit": "seconds", "target": "≤30" }
  ],
  "decision": "dont_use_ml"
}
```

---

## Example 2 – Sales Forecasting

**Input:**  
Sales forecasting for 12-week horizon with sparse historicals — ML or rules?

**Expected Output (JSON):**
```json
{
  "needs_ml": "yes",
  "ml_recommendations": [
    { "approach": "time-series regression", "why": "captures trend with sparse data" }
  ],
  "decision": "proceed"
}
```

---

_End of examples.md_
