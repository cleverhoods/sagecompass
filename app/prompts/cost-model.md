# Sagecompass - Cost model
_instructions v3.0_

**Purpose**  
Defines the default cost estimation framework for Stage 5 reasoning within SageCompass.  
This document enables consistent cost and ROI evaluation for both ML and non-ML solution paths.

---

## 1. Cost Dimensions

Each cost output is grouped into **one_time**, **monthly**, and **people** components.  
All numeric ranges are **order-of-magnitude estimates** and must be labeled `[Unverified]` unless the user provides concrete data.

| Category | Description | Typical Unit |
|-----------|--------------|---------------|
| one_time  | Initial setup and project start costs | USD / EUR / local currency |
| monthly   | Ongoing operational costs | per month |
| people    | Internal or contracted human effort | Full-Time Equivalent (FTE) |

---

## 2. Default ML Path Ranges

| Component | Low | High | Notes |
|------------|-----|------|-------|
| **infra_setup** | \$3 000 | \$8 000 | Cloud provisioning, CI/CD, data pipelines |
| **data_labeling** | \$2 000 | \$10 000 | Manual or semi-automated annotation |
| **training_run** | \$1 000 | \$5 000 | Initial training, hyper-parameter tuning |
| **compute** | \$200 / mo | \$1 500 / mo | Batch or online inference workloads |
| **monitoring** | \$100 / mo | \$300 / mo | Model drift, performance dashboards |
| **storage** | \$50 / mo | \$200 / mo | Data + artifact retention |
| **build_fte** | 0.5 | 1.5 | DS / MLE / MLOps during build |
| **maint_fte** | 0.2 | 0.5 | Long-term upkeep |

---

## 3. Default Non-ML Path Ranges

| Component | Low | High | Notes |
|------------|-----|------|-------|
| **automation_rules** | \$1 000 | \$5 000 | Heuristic or rule-based automation |
| **dashboards** | \$500 | \$2 000 | BI or reporting setup |
| **compute** | \$50 / mo | \$150 / mo | Lightweight jobs or scripts |
| **monitoring** | \$20 / mo | \$50 / mo | Basic uptime / alerting |
| **engineer_fte** | 0.1 | 0.3 | Analyst / backend developer time |

---

## 4. ROI & Payback Estimation

**Purpose:** translate costs and expected KPI impact into a simple financial projection.

| Field | Meaning | Calculation |
|-------|----------|-------------|
| **payback_months** | Estimated months to recover one-time + build costs | `total_one_time / (monthly_gain − monthly_cost)` |
| **breakeven_conditions** | KPI thresholds required to achieve ROI | Example: *retain ≥ 200 users @ €5 margin per month* |

All numeric results must include `[Unverified]` unless derived from user-provided data.

---

## 5. Scaling Factors

| Factor | Multiplier | Condition |
|---------|-------------|------------|
| **data_volume** | × 1.2 per 10× increase in samples | impacts compute + storage |
| **model_complexity** | × 1.3 for deep learning models | adds compute + training costs |
| **real_time_requirements** | × 1.4 | adds infra + monitoring costs |
| **multi_region_deployment** | × 1.5 | adds infra + people overhead |
| **regulatory_compliance** | × 1.2 | adds governance + audit costs |

These multipliers apply proportionally to relevant cost fields during reasoning.

---

## 6. Currency & Localization

- Default display unit: `currency` (symbol preserved from user input if known).
- All cost outputs remain **ranges** (`low–high`) not point values.
- Currency conversion or inflation adjustment is **not performed automatically**.
- Local markets may override base tables via an org-specific extension file.

---

## 7. Example Cost Profiles by Archetype

### Classification / Prediction
- Moderate training costs, low inference costs
- Typical total: **\$15 000–\$25 000 setup**, **\$500–\$900 monthly**

### Forecasting / Regression
- Slightly higher compute & storage (temporal data)
- Typical total: **\$20 000–\$30 000 setup**, **\$600–\$1 000 monthly**

### NLP / Text Analysis
- Heavy preprocessing + GPU training
- Typical total: **\$25 000–\$40 000 setup**, **\$1 000–\$2 000 monthly**

---

## 8. Output Rules

When emitting costs to JSON:
1. Always include the `[Unverified]` tag for inferred values.
2. Express all FTEs as decimals (e.g., 0.3 = 30 % of a full-time person).
3. Never show totals without context — costs must remain decomposed.
4. Round currency to the nearest 100 unit for readability.
5. If insufficient information is available, emit:
   ```
   "assumptions": ["[Unverified]", "Insufficient data for detailed estimate"]
   ```

---

## 9. Example ROI Lens Output

```json
"roi_lens": {
  "payback_months": "[Unverified] 4–6",
  "breakeven_conditions": "retain ≥250 users @ €5/mo margin"
}
```

---

_End of cost-modal.md_