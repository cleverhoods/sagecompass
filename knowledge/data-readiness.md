# SageCompass – Data Readiness & Feature Engineering
_instructions v1.2_

## 1. Purpose
Provide a structured checklist for assessing whether available data supports an ML solution.  
Used mainly in **Stage 4 – Feasibility & Data Check**.

---

## 2. Data Readiness Dimensions

| Dimension | Key Questions | Red-Flag Conditions |
|------------|---------------|--------------------|
| **Sources** | Where does the data originate? Are systems stable and documented? | Unverified or manual data exports |
| **Access** | Do we have legal and technical rights to use it? | Restricted, third-party, or manual approval required |
| **Volume** | Rough order of magnitude (10³ – 10⁶ + samples). Enough per prediction unit? | Fewer than ~1 000 samples or extreme class imbalance |
| **Quality** | Missing values, duplicates, noise, drift? | > 20 % missing, inconsistent schema, unresolved outliers |
| **Labels** | Are reliable outcome labels available? | Missing or proxy labels only |
| **Timeliness** | How recent is the data? How often refreshed? | Stale > 12 months or no update schedule |
| **Granularity** | At what level (user, session, order, day…)? | Aggregated beyond useful level |
| **Privacy / Risk** | Contains PII, sensitive categories, GDPR issues? | Non-compliant or un-anonymized PII |

If two or more dimensions fail, flag dataset as **Not Ready**.

---

## 3. Feature-Engineering Guidelines
- **Encoding:** Normalize categorical variables → one-hot or embeddings.
- **Missing data:** Impute or flag; never drop critical entities silently.
- **Scaling:** Standardize numeric features if gradient-based models planned.
- **Derived features:** Prefer domain-explainable transformations.
- **Data leakage:** Ensure future information isn’t present in training features.
- **Sampling:** Stratify splits by key business dimensions (region, customer tier, etc.).

---

## 4. Data-Readiness Categories

| Status | Description | Next Action |
|---------|--------------|-------------|
| **Ready** | All dimensions acceptable. | Proceed with pilot design. |
| **Partially Ready** | Minor issues (e.g., missing labels, small imbalance). | Mitigate during pilot (re-label, augment). |
| **Not Ready** | Major gaps (no labels, insufficient samples). | Halt ML; improve data pipeline first. |

---

## 5. Compliance & Governance Checklist
- Verify data owner and retention policy.
- Document purpose and lawful basis (GDPR Art. 6).
- Remove or hash direct identifiers before modeling.
- Maintain audit log of data access and transformations.
- Ensure model output cannot re-identify individuals.

---

## 6. Example Evaluation Output

```json
"data_profile": {
  "labels": "partial",
  "samples_order": "1e4",
  "time_span": "months",
  "granularity": "order",
  "privacy_flags": ["GDPR"]
}
```

_End of data-readiness.md_