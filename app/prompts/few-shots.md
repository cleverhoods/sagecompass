# SageCompass – Few-Shot Examples
_instructions v3.0_

These examples demonstrate how SageCompass v3.0 executes the **five-stage reasoning pipeline** and produces structured outputs in full JSON format.  
Each example illustrates a different decision outcome: **proceed**, **reframe**, and **dont_use_ml**.

---

## Example 1 – Proceed (ML justified, feasible)

**Input:**  
Predict which subscription users are likely to churn within 30 days.

**Reasoning Summary (Stages 1–5)**
- **Stage 1:** Problem identified as *classification*, supervised learning.
- **Stage 2:** Goals – reduce churn and improve retention ROI.
- **Stage 3:** KPIs – churn rate ↓, retention uplift %, synthetic KPI = projected monthly revenue retention.
- **Stage 4:** Data readiness score 22 (Ready). Features: user activity, plan tier, ticket count, tenure, region.
- **Stage 5:** Decision: Proceed — clear business value and data sufficiency.

**Expected Output:**
```json
{
  "business_summary": {
    "problem_statement": "Predict which users will churn in the next 30 days.",
    "primary_value_driver": "revenue",
    "stakeholders": ["marketing", "product"],
    "decision_context": "retention campaign planning"
  },
  "goal_alignment": {
    "profit_goals": [
      {
        "name": "reduce churn-related revenue loss",
        "unit": "%",
        "target": "≥10",
        "baseline": "[Estimated] 5–7",
        "kpi_lens": "financial",
        "justification": "Based on prior retention benchmarks. Confidence: medium"
      }
    ],
    "user_goals": [
      {
        "name": "improve customer retention satisfaction",
        "unit": "%",
        "target": "≥80",
        "baseline": "[Estimated] 72",
        "kpi_lens": "experience",
        "justification": "Derived from support survey data. Confidence: medium"
      }
    ]
  },
  "kpi_alignment": {
    "business_kpis": [
      {
        "name": "retention_rate",
        "description": "Share of users retained over 30 days",
        "unit": "%",
        "target": "≥90",
        "baseline": "[Estimated] 84",
        "direction": "increase",
        "timeframe": "monthly",
        "kpi_lens": "financial",
        "source": "metrics_library",
        "confidence": "high",
        "justification": "Industry standard benchmark"
      }
    ],
    "synthetic_kpis": [
      {
        "name": "revenue_retained",
        "formula": "active_users * ARPU * retention_rate",
        "expected_range": "$100k–$150k/mo",
        "unit": "currency",
        "derived_from": ["retention_rate"],
        "purpose": "financial_projection",
        "justification": "Derived to estimate monetary impact"
      }
    ],
    "technical_metrics": [
      {
        "name": "f1_score",
        "description": "Harmonic mean of precision and recall for churn classification",
        "metric_type": "classification",
        "unit": "score",
        "target": "≥0.85",
        "baseline": "[Unknown]",
        "direction": "increase",
        "dataset_split": "validation",
        "evaluation_frequency": "per_run",
        "kpi_link": ["retention_rate"],
        "confidence": "medium",
        "justification": "Standard metric for imbalanced churn tasks"
      }
    ]
  },
  "solution_alignment": {
    "problem_types": ["classification"],
    "learning_paradigms": ["supervised"],
    "baseline_definition": "manual retention playbook",
    "ml_recommendations": [
      {
        "approach": "churn classification + uplift modeling",
        "why": "directly predicts churn probability and intervention effect"
      }
    ],
    "non_ml_alternatives": ["rule_based segmentation", "email triggers"]
  },
  "data_blueprint": {
    "example_dataset": {
      "features": ["user_id", "plan_tier", "tenure_days", "rfm_scores", "ticket_count_30d", "region"],
      "label": "churned_30d (0/1)",
      "sample_size": "1e4",
      "time_span": "months",
      "granularity": "user",
      "notes": "avoid leakage from post-churn activity"
    },
    "data_profile": {
      "labels": "yes",
      "samples_order": "1e4",
      "time_span": "months",
      "granularity": "user",
      "privacy_flags": ["GDPR"],
      "data_readiness_score": 22
    }
  },
  "costs": {
    "ml_path": {
      "one_time": {"infra_setup": "$4k–$8k", "training_run": "$1k–$3k"},
      "monthly": {"compute": "$200–$400", "monitoring": "$100"},
      "people": {"build_fte": "0.6", "maint_fte": "0.2"},
      "assumptions": ["[Estimated] small-scale deployment"]
    },
    "non_ml_path": {
      "one_time": {"automation_rules": "$2k–$3k"},
      "monthly": {"compute": "$50–$150"},
      "people": {"engineer_fte": "0.1"},
      "assumptions": ["manual targeting baseline"]
    },
    "roi_lens": {
      "payback_months": "3–6",
      "breakeven_conditions": "retain ≥200 users @ €5/mo margin"
    }
  },
  "pilot_plan": {
    "duration_weeks": 4,
    "design": "A/B test: ML vs rule-based targeting",
    "metrics": ["retention_rate", "churn_rate"],
    "decision_gate": "Proceed if retention uplift ≥1.2pp"
  },
  "go_no_go": {
    "ml_justified": "yes",
    "decision": "proceed",
    "kill_criteria": ["no uplift after 4 weeks"],
    "stage_status": {
      "stage1_problem": "ok",
      "stage2_goals": "ok",
      "stage3_metrics": "ok",
      "stage4_feasibility": "ok"
    },
    "pending_question": ""
  }
}
```

---

## Example 2 – Reframe (Partial readiness)

**Input:**  
Forecast quarterly equipment failure probability using limited maintenance logs.

**Reasoning Summary (Stages 1–5)**
- **Stage 1:** Archetype detected: *forecasting*, supervised learning.
- **Stage 2:** Business goals defined, but unclear baseline.
- **Stage 3:** KPIs mapped to uptime and maintenance costs.
- **Stage 4:** Data readiness = 16 → Partially Ready (missing labels, irregular timestamps).
- **Stage 5:** Decision: Reframe – data insufficient for accurate forecasting.

**Expected Output:**
```json
{
  "business_summary": {
    "problem_statement": "Forecast machine failure likelihood to reduce downtime costs.",
    "primary_value_driver": "cost",
    "stakeholders": ["operations", "maintenance"],
    "decision_context": "preventive maintenance planning"
  },
  "solution_alignment": {
    "problem_types": ["forecasting"],
    "learning_paradigms": ["supervised"],
    "baseline_definition": "manual inspection schedule",
    "ml_recommendations": [
      {"approach": "time-series regression with lag features", "why": "uses historical failure data for trend prediction"}
    ],
    "non_ml_alternatives": ["scheduled inspections", "threshold alerts"]
  },
  "data_blueprint": {
    "example_dataset": {
      "features": ["machine_id", "temperature_avg", "vibration_level", "maintenance_hours"],
      "label": "failure_within_90d (0/1)",
      "sample_size": "1e3",
      "time_span": "years",
      "granularity": "machine",
      "notes": "missing timestamps, incomplete logs"
    },
    "data_profile": {
      "labels": "partial",
      "samples_order": "1e3",
      "time_span": "years",
      "granularity": "machine",
      "privacy_flags": ["none"],
      "data_readiness_score": 16
    }
  },
  "go_no_go": {
    "ml_justified": "yes",
    "decision": "reframe",
    "kill_criteria": ["insufficient labeled failures"],
    "stage_status": {
      "stage1_problem": "ok",
      "stage2_goals": "ok",
      "stage3_metrics": "ok",
      "stage4_feasibility": "partial"
    },
    "pending_question": "Can more historical failure labels be collected for model training?"
  }
}
```

---

## Example 3 – Dont Use ML (Rule-based better)

**Input:**  
Send reminder emails when invoices are overdue by more than 14 days.

**Reasoning Summary (Stages 1–5)**
- **Stage 1:** Detected rule-based automation; no learning required.
- **Stage 2–4:** KPIs deterministic, no data variance or pattern learning needed.
- **Stage 5:** Decision: Dont Use ML – explicit rules solve it completely.

**Expected Output:**
```json
{
  "business_summary": {
    "problem_statement": "Send reminder emails for invoices overdue >14 days.",
    "primary_value_driver": "cost",
    "stakeholders": ["finance", "operations"],
    "decision_context": "billing automation"
  },
  "solution_alignment": {
    "problem_types": ["rules"],
    "learning_paradigms": ["none"],
    "baseline_definition": "manual invoice checks",
    "ml_recommendations": [],
    "non_ml_alternatives": ["scheduled job", "CRM workflow automation"]
  },
  "go_no_go": {
    "ml_justified": "no",
    "decision": "dont_use_ml",
    "kill_criteria": [],
    "stage_status": {
      "stage1_problem": "ok",
      "stage2_goals": "ok",
      "stage3_metrics": "n/a",
      "stage4_feasibility": "irrelevant"
    },
    "pending_question": ""
  }
}
```

---

_End of few-shots.md_
