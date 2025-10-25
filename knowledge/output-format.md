# SageCompass – Output Format Specification
_instructions v3.0_

Defines the canonical JSON schema emitted by SageCompass. The first line of any model response must be valid JSON matching this structure.

```json
{
  "business_summary": {
    "problem_statement": "",
    "primary_value_driver": "revenue|cost|risk",
    "stakeholders": ["ops", "marketing"],
    "decision_context": ""
  },
  "goal_alignment": {
    "profit_goals": [
      {
        "name": "",
        "unit": "",
        "target": "",
        "baseline": "",
        "kpi_lens": "financial|operational|experience",
        "justification": ""
      }
    ],
    "user_goals": [
      {
        "name": "",
        "unit": "",
        "target": "",
        "baseline": "",
        "kpi_lens": "financial|operational|experience",
        "justification": ""
      }
    ]
  },
  "kpi_alignment": {
    "business_kpis": [
      {
        "name": "",
        "description": "",
        "unit": "%|currency|hours|index|custom",
        "target": "",
        "baseline": "",
        "direction": "increase|decrease|stabilize",
        "timeframe": "weekly|monthly|quarterly|annual|campaign",
        "kpi_lens": "financial|operational|experience",
        "source": "user|metrics_library|synthetic|benchmark",
        "confidence": "high|medium|low",
        "justification": ""
      }
    ],
    "synthetic_kpis": [
      {
        "name": "",
        "formula": "",
        "expected_range": "",
        "unit": "",
        "derived_from": ["business_kpi_name_1", "business_kpi_name_2"],
        "purpose": "financial_projection|illustrative|sensitivity_analysis|scenario_comparison|scaling_projection|benchmark_alignment|data_quality_proxy|kpi_bridge",
        "justification": ""
      }
    ],
    "technical_metrics": [
      {
        "name": "",
        "description": "",
        "metric_type": "classification|regression|forecasting|ranking|clustering|anomaly|reinforcement|custom",
        "unit": "%|score|error|seconds|index|custom",
        "target": "",
        "baseline": "",
        "direction": "increase|decrease",
        "dataset_split": "train|validation|test|production|cross_validation",
        "evaluation_frequency": "per_run|daily|weekly|continuous",
        "kpi_link": [""],
        "confidence": "high|medium|low",
        "justification": ""
      }
    ]
  },
  "solution_alignment": {
    "problem_types": ["classification"],
    "learning_paradigms": ["supervised"],
    "baseline_definition": "current manual retention playbook",
    "ml_recommendations": [
      {
        "approach": "churn classification + uplift targeting",
        "why": "maps KPI (retention ↑) to classification archetype"
      }
    ],
    "non_ml_alternatives": ["rule_based", "heuristics", "bi_dashboard"]
  },
  "data_blueprint": {
    "example_dataset": {
      "features": ["user_id", "plan_tier", "tenure_days", "rfm_scores", "ticket_count_30d", "email_opens_30d"],
      "label": "churned_30d (0/1)",
      "sample_size": "1e4",
      "time_span": "months",
      "granularity": "user",
      "notes": "avoid leakage from post-churn actions; encode categories; stratify by region"
    },
    "data_profile": {
      "labels": "partial",
      "samples_order": "1e4",
      "time_span": "months",
      "granularity": "user",
      "privacy_flags": ["GDPR"],
      "data_readiness_score": 18
    }
  },
  "costs": {
    "ml_path": {
      "one_time": {
        "infra_setup": "$3k–$8k",
        "data_labeling": "$2k–$6k",
        "training_run": "$1k–$3k"
      },
      "monthly": {
        "compute": "$200–$600",
        "monitoring": "$100–$200",
        "storage": "$50–$100"
      },
      "people": {
        "build_fte": "0.7",
        "maint_fte": "0.2"
      },
      "assumptions": ["[Unverified]"]
    },
    "non_ml_path": {
      "one_time": {
        "automation_rules": "$1k–$3k",
        "dashboards": "$0.5k–$2k"
      },
      "monthly": {
        "compute": "$50–$150",
        "monitoring": "$20–$50"
      },
      "people": {
        "engineer_fte": "0.1"
      },
      "assumptions": ["[Unverified]"]
    },
    "roi_lens": {
      "payback_months": "[Unverified] 3–6",
      "breakeven_conditions": "retain ≥200 users @ €5/mo margin"
    }
  },
  "pilot_plan": {
    "duration_weeks": 4,
    "design": "A/B retention playbooks using model vs rules",
    "metrics": ["retention_rate", "savings_per_retained_user"],
    "decision_gate": "Proceed if retention +1.2pp and CAC neutral"
  },
  "go_no_go": {
    "ml_justified": "yes",
    "decision": "proceed",
    "kill_criteria": ["no uplift after 4 weeks", "data leakage found"],
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

_End of output-format.md_
