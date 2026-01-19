# Architecture Principles Assessment

Run an architecture principles assessment using the format at `docs/architecture-assessment-format.md`.

## Input
- **Principles file**: $ARGUMENTS (default: `docs/langgraph-python-architecture-principles.md`)
- **Target**: $ARGUMENTS (default: `PROJECT_ROOT/langgraph`)

## Execution

### Phase 1: Explore Each Grade
For each grade in the principles document:
1. Read the principle requirements
2. Search the codebase for evidence of compliance
3. Document findings with status (FULL/PARTIAL/MINIMAL/NONE), evidence, and issues

### Phase 2: Score Each Principle
Assign scores (1–10) based on:
- Compliance status
- Severity of gaps
- Impact on system quality
- Presence of automated enforcement

### Phase 3: Compile Report
Generate the final report with:
- Per-principle assessment tables (by grade)
- Grade summaries with averages
- Overall summary table (weighted by principle count)
- Key findings (strengths and gaps)
- Prioritized recommendations
- Final Assessment Box with a visual scale

## Output Format
Follow the exact format specified in `docs/architecture-assessment-format.md`.