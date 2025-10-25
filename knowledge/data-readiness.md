# SageCompass – Data Readiness & Feature Engineering
_instructions v2.2_

Used in **Stage 4 – Feasibility & Data Check** to evaluate whether available data can reliably support ML experimentation.  
Outputs map directly to the `"data_profile"` field in the JSON response.

---

## 1. Purpose
Assess whether the **data environment** (collection, quality, rights, and relevance) is strong enough to justify ML use.  
If serious gaps exist, SageCompass must recommend **“Reframe”** or **“Don’t use ML.”**

---

## 2. Data Readiness Dimensions

| Dimension | Key Questions | Healthy Indicators | Red Flags |
|------------|---------------|--------------------|------------|
| **Sources** | Where does the data originate? Are systems stable, traceable, and owned? | Centralized, versioned, consistent across time | Manual exports, ad hoc or third-party sources |
| **Access & Rights** | Are usage rights clear? Any compliance blockers? | Documented owner + legal basis (GDPR, CCPA) | Unverified access, unclear ownership |
| **Volume** | Enough samples per prediction target? | ≥ 10³ per label class or ≥ 10⁴ total records | < 1 000 total samples or extreme imbalance |
| **Label Availability** | Are ground-truth labels accurate and current? | Verified or easily collectible | Missing, proxy, or outdated labels |
| **Quality** | How much is missing or inconsistent? | < 10 % missing, consistent schema | > 20 % missing, drift, duplicates, noise |
| **Timeliness** | Is the data recent and refreshed regularly? | Updated ≤ 3 months old | Stale > 12 months, no refresh plan |
| **Granularity** | At what level is data collected (user, event, session…)? | Sufficiently detailed per learning unit | Over-aggregated or misaligned |
| **Privacy / Risk** | Any PII or sensitive categories? | Properly anonymized / compliant | Unmasked PII, sensitive attributes |
| **Stability / Drift** | Has meaning of data changed over time? | Stationary patterns, consistent encoding | High concept drift or schema churn |

If **2+ dimensions** fail, mark dataset as **Not Ready**.

---

## 3. Quantitative Scoring
Each dimension can be scored from 0–3:

| Score | Interpretation |
|--------|----------------|
| **3 – Ready** | Meets all requirements |
| **2 – Partially Ready** | Minor issues; acceptable for pilot |
| **1 – Risky** | Serious concern; mitigation needed |
| **0 – Not Ready** | Blocker; ML not advised |

Total possible: 27
- ≥ 21 → **Ready**
- 14–20 → **Partially Ready**
- < 14 → **Not Ready**

Optional JSON field:
```json
"data_readiness_score": 18
```

---

## 4. Feature-Engineering Heuristics
- Normalize categorical features with interpretable encodings (avoid opaque hashing).
- Impute missing values or flag them explicitly.
- Avoid data leakage (future information in training set).
- Prefer domain-explainable transformations.
- Stratify samples by key business attributes (region, segment, product).
- Document every derived feature and its business meaning.

---

## 5. Data-Readiness Categories

| Status | Description | Next Action |
|---------|--------------|-------------|
| **Ready** | Strong foundation; proceed to pilot. | Continue with ML evaluation. |
| **Partially Ready** | Minor gaps (small imbalance, recent drift). | Mitigate in pilot; log assumptions. |
| **Not Ready** | Major issues (no labels, insufficient data, compliance risk). | Halt ML; improve data pipeline first. |

---

## 6. Compliance & Governance Checklist
- Confirm data owner and retention policy.
- Document lawful basis (GDPR Art. 6 / CCPA).
- Anonymize or hash identifiers before training.
- Maintain audit trail for all data transformations.
- Validate that model output cannot re-identify users.
- If uncertain, flag `"privacy_flags": ["review_required"]`.

---

## 7. Example JSON Output

```json
"data_profile": {
  "labels": "partial",
  "samples_order": "1e4",
  "time_span": "months",
  "granularity": "order",
  "privacy_flags": ["GDPR"],
  "data_readiness_score": 18
}
```

---

## 8. Risk Recommendations
If **Not Ready**, SageCompass should output:
> “Insufficient data quality or compliance for ML. Recommend improving labeling, sampling, or governance before proceeding.”

---

_End of data-readiness.md_
