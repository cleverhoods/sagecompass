# SageCompass – Data Readiness & Feature Engineering
_instructions v3.0_

Used in **Stage 4 – Feasibility & Data Blueprint** to determine whether available data can reliably support ML experimentation and to outline what an ideal dataset would contain.  
Outputs map directly to the `"data_blueprint"` and `"data_profile"` sections in the JSON response.

---

## 1. Purpose
Assess the technical and governance maturity of the **data environment** — its sources, quality, rights, and stability — to decide whether ML implementation is feasible.  
If critical gaps exist, SageCompass must recommend **“reframe”** (improvable) or **“dont_use_ml”** (unsuitable).

---

## 2. Data Readiness Dimensions (Scored 0–3)

| Dimension | Definition | 3 – Ready | 2 – Partially Ready | 1 – Risky | 0 – Not Ready |
|------------|-------------|------------|---------------------|------------|----------------|
| **Sources** | Origin and reliability of data pipelines | Centralized, versioned, traceable | Some manual steps or mixed systems | Ad-hoc exports, poor lineage | Unverified or third-party-only sources |
| **Access & Rights** | Legal clarity and governance | Documented owner, access control, compliance verified | Access available but unclear rights | No DPA, unclear legal basis | Restricted or illegal to use |
| **Volume** | Sufficient sample size for ML | ≥10⁴ records or ≥10³ per class | 10³–10⁴ total | <10³ samples | Too few to train (toy scale) |
| **Label Availability** | Existence and accuracy of targets | Clean, up-to-date labels | Partial or outdated labels | Proxy labels, noisy supervision | No labels / non-collectable |
| **Quality** | Consistency, completeness, and noise | <10% missing, stable schema | Minor missing values (<20%) | Frequent missing, inconsistent schema | Corrupted, mismatched, high noise |
| **Timeliness** | Data recency and refresh cadence | Refreshed ≤3 months | ≤6 months old, manual refresh | >9 months old | Obsolete or discontinued |
| **Granularity** | Data resolution for ML unit | Correct (user, session, etc.) | Mixed aggregation | Over-aggregated | No clear entity-level structure |
| **Privacy / Risk** | Sensitive data exposure | Anonymized / compliant | Limited PII, masked | Contains sensitive data, weak governance | Non-compliant / illegal retention |
| **Stability / Drift** | Schema and meaning consistency | Stable schema, low drift | Minor drift, rare schema changes | Periodic major drift | Frequent redefinition or corruption |

- Score each dimension from **0–3**
- Sum for total **`data_readiness_score` (0–27)**
    - ≥ 21 → **Ready**
    - 14–20 → **Partially Ready**
    - < 14 → **Not Ready**

If **two or more dimensions score ≤1**, mark dataset as **Not Ready** automatically.

---

## 3. Improvement Hints (Per Dimension)

| Dimension | Typical Fix |
|------------|--------------|
| **Sources** | Centralize data, establish ETL ownership, automate versioning. |
| **Access & Rights** | Formalize access policy, document data owner, verify GDPR/CCPA basis. |
| **Volume** | Increase sampling window, aggregate multiple sources, simulate additional data. |
| **Label Availability** | Label a subset manually, design weak supervision pipeline. |
| **Quality** | Run deduplication, fill nulls, validate data types. |
| **Timeliness** | Automate refreshes, schedule batch exports. |
| **Granularity** | Adjust aggregation to entity level (user, order, session). |
| **Privacy / Risk** | Anonymize PII, hash IDs, restrict access, review with DPO. |
| **Stability / Drift** | Monitor schema versions, introduce drift detection. |

---

## 4. Feature-Engineering Heuristics

**When data is at least “Partially Ready”:**
- Normalize categorical fields using interpretable encodings (avoid opaque hashing).
- Impute or flag missing values instead of discarding records.
- Detect and prevent data leakage (future information in training set).
- Use explainable transformations (domain features > arbitrary math).
- Stratify samples by business attributes (region, segment, product).
- Document each derived feature’s business purpose and logic.

**When data is “Not Ready”:**
- Do not proceed with ML; return improvement hints from above.

---

## 5. Data-Readiness Categories

| Status | Definition | Next Action |
|---------|-------------|--------------|
| **Ready** | Strong foundation, compliant, sufficient volume, recent | Proceed with ML pilot |
| **Partially Ready** | Minor quality or coverage issues | Proceed with pilot; document assumptions |
| **Not Ready** | Major gaps (labels, compliance, access) | Recommend `"decision": "reframe"` or `"dont_use_ml"` |

---

## 6. Compliance & Governance Checklist
- Confirm **data owner**, retention policy, and lawful basis (GDPR Art. 6 / CCPA).
- Ensure all identifiers are hashed or pseudonymized before model training.
- Maintain audit logs of all transformations and dataset versions.
- Validate that outputs cannot re-identify users.
- If any uncertainty exists, add:  
  `"privacy_flags": ["review_required"]`

---

## 7. Example JSON Output

```json
"data_profile": {
  "labels": "partial",
  "samples_order": "1e4",
  "time_span": "months",
  "granularity": "user",
  "privacy_flags": ["GDPR"],
  "data_readiness_score": 18
}
```

---

## 8. Automated Guidance Rules
When generating `data_blueprint`:
- If **score ≥ 21** → allow ML continuation.
- If **score 14–20** → proceed with caveats and log assumptions.
- If **score < 14** → halt and emit `"decision": "reframe"` or `"dont_use_ml"`.
- Always output improvement notes and privacy flags.

---

## 9. Example System Message for “Not Ready”

> “Insufficient data quality or compliance for ML. Recommend improving labeling, volume, or governance before proceeding.”

---

_End of data-readiness.md_
