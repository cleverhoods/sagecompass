# Architecture Principles Assessment Format

> Reusable format for assessing codebase compliance against architectural principles.
>
> **Usage:** "Run an architecture principles assessment based on `[path/to/principles.md]` with `docs/architecture-assessment-format.md`"

---

## Scoring Scale

| Score | Level | Description |
|-------|-------|-------------|
| 1 | Poor | Severe violations, no adherence |
| 3 | Standard | Basic compliance, significant gaps |
| 5 | Advanced | Good compliance, minor gaps |
| 7 | High | Strong compliance, well-implemented |
| 9 | Enterprise | Near-complete compliance, production-ready |
| 10 | Exceptional | Full compliance, exemplary implementation |

---

## Compliance Status Labels

| Status | Meaning | Typical Score |
|--------|---------|---------------|
| **FULL** | Complete adherence, no violations | 9-10 |
| **PARTIAL** | Mostly compliant, some gaps | 6-8 |
| **MINIMAL** | Basic compliance, significant gaps | 3-5 |
| **NONE** | No compliance or not implemented | 1-2 |

---

## Assessment Methodology

### Phase 1: Explore Each Grade
For each grade in the principles document (e.g., Standard, Advanced, Production, Enterprise):

1. **Read the principle requirements** from the source document
2. **Search the codebase** for evidence of compliance:
   - Check directory structures
   - Examine code patterns and imports
   - Review test coverage
   - Inspect configuration files
3. **Document findings** for each principle:
   - Compliance status (FULL/PARTIAL/MINIMAL/NONE)
   - Evidence (specific files, line numbers, patterns)
   - Issues (gaps, violations, missing implementations)

### Phase 2: Score Each Principle
Assign a score (1-10) based on:
- Compliance status
- Severity of gaps
- Impact on system quality
- Presence of automated enforcement (tests, linting)

### Phase 3: Compile Report
Generate the final report with:
- Grade-by-grade scoring tables
- Overall weighted average
- Key findings (strengths and gaps)
- Prioritized recommendations

---

## Output Format

### Per-Principle Assessment Table

```markdown
| # | Principle | Status | Score | Notes |
|---|-----------|--------|-------|-------|
| 1 | [Name] | FULL/PARTIAL/MINIMAL/NONE | X/10 | [Brief note] |
```

### Grade Summary

```markdown
**[Grade Name] Score: X.X/10** (Average of principles)
```

### Overall Summary Table

```markdown
| Grade | Principles | Weight | Score | Level |
|-------|------------|--------|-------|-------|
| Standard | X | XX% | X.X/10 | [Level] |
| Advanced | X | XX% | X.X/10 | [Level] |
| Production | X | XX% | X.X/10 | [Level] |
| Enterprise | X | XX% | X.X/10 | [Level] |
| **OVERALL** | **XX** | **100%** | **X.X/10** | **[Level]** |
```

**Weighting:** Grades are weighted proportionally to their principle count.

### Key Findings Section

```markdown
### Exceptional Strengths (Score 10)
- [Bullet list of perfect-score principles]

### Areas Requiring Attention

| Priority | Principle | Current | Target | Gap |
|----------|-----------|---------|--------|-----|
| HIGH/MEDIUM/LOW | #X [Name] | X | X | [Description] |
```

### Recommendations Section
Prioritized list of improvements:
1. **Critical**: Must fix for production readiness
2. **Important**: Should fix for quality
3. **Nice-to-have**: Improvements for excellence

### Final Assessment Box

```
╔══════════════════════════════════════════════════════════════╗
║                                                              ║
║   [COMPONENT] OVERALL SCORE: X.X / 10                        ║
║                                                              ║
║   Level: [LEVEL]                                             ║
║                                                              ║
║   |----|----|----|----|----|----|----|----|----|----|        ║
║   0    1    2    3    4    5    6    7    8    9    10       ║
║   ▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▲         ║
║        Poor   Std    Adv    High      Enterprise             ║
║                                                              ║
║   [2-3 sentence summary]                                     ║
║                                                              ║
╚══════════════════════════════════════════════════════════════╝
```

**Scale visualization guide:**
- Scale runs 0-10 with 5 levels: Poor (1-2), Standard (3-4), Advanced (5-6), High (7-8), Enterprise (9-10)
- Fill `▓` blocks proportionally (e.g., 9.9 = 49 filled blocks out of 50)
- Place `▲` marker at score position
- Use `░` for unfilled portion

---

## Assessment Checklist

Before finalizing the assessment, verify:

- [ ] All principles in the source document are assessed
- [ ] Each principle has: status, score, evidence, issues
- [ ] Grade averages are calculated correctly
- [ ] The overall score is the average of grade scores
- [ ] Key strengths are highlighted
- [ ] Gaps are prioritized (HIGH/MEDIUM/LOW)
- [ ] Recommendations are actionable
- [ ] The final summary reflects the overall assessment

---

## Example Usage

**User prompt:**
```
Run an architecture principles assessment based on
`docs/langgraph-python-architecture-principles.md` with
`docs/architecture-assessment-format.md`
```

**Expected behavior:**
1. Read the principles document to understand criteria
2. Explore the target codebase (inferred from principles or specified)
3. Assess each principle using the methodology above
4. Generate the report in the specified format
5. Provide actionable recommendations

---

## Customization

### Adjusting the Scale
Modify the scoring scale table to match your organization's standards.

### Adding Grades
If your principles document has different grades, assess each grade separately and include in the summary.

### Weighting
By default, grades are weighted **proportionally to their principle count**:

```markdown
| Grade | Principles | Weight | Score | Weighted |
|-------|------------|--------|-------|----------|
| Standard | 13 | 28% | 9.3 | 2.60 |
| Advanced | 10 | 22% | 10.0 | 2.20 |
| Production | 13 | 28% | 9.5 | 2.66 |
| Enterprise | 10 | 22% | 9.5 | 2.09 |
| **OVERALL** | 46 | 100% | | **9.55** |
```

**To calculate weights:** `weight = principles_in_grade / total_principles × 100%`
