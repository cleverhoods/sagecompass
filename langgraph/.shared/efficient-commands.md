# Efficient Command Patterns

Quick reference for token-efficient operations.

## Quick Reference

**Most common exclusion pattern:**
```bash
-not -path "*/__pycache__/*" -not -path "*/.git/*" -not -path "*/.cache/*"
```

**Standard commands:**
```bash
# Find Python files
find . -name "*.py" -type f -not -path "*/__pycache__/*" -not -path "*/.git/*"

# Search with type filter
Grep pattern="<pattern>" path="<path>" type="py" head_limit=50

# Read with limits
Read file_path="<path>" offset=0 limit=50
```

## Session Start Ritual

Read navigation maps BEFORE searching:
1. Read `.shared/sys.yml` (comprehensive path index)
2. Read task-specific map: `platform.yml`, `components.yml`, or `contracts.yml`

## Critical Rules

**Never read .claudeignore files:** Lock files (uv.lock = 468KB), cache directories (__pycache__/), virtual environments, build artifacts.

**Always exclude cache directories:** Use `-not -path "*/__pycache__/*"` in all find commands.

## Purpose-Based Reading (CRITICAL)

Before reading ANY file, ask: **"What is my goal?"**

### Goal: EDIT the file
- Read FULL file without limits (even 300+ lines)
- Why: Edit tool requires it; chunked reading costs more

```bash
Read file_path="app/nodes/problem_framing.py"
```

### Goal: UNDERSTAND structure
- Read first 30-50 lines (imports, class definitions)
- Why: Python files front-load key information

```bash
Read file_path="app/nodes/problem_framing.py" offset=0 limit=50
```

### Goal: FIND specific content
- Step 1: Grep to locate
- Step 2: Read specific section

```bash
Grep pattern="def process_phase" path="app/nodes" output_mode="files_with_matches"
Read file_path="app/nodes/problem_framing.py" offset=45 limit=30
```

### Goal: VERIFY existence
- Use Grep with files_with_matches only

```bash
Grep pattern="PhaseEntry" path="app" output_mode="files_with_matches"
```

## File Size Guidelines

Check size before reading: `du -h filename`

- **< 5KB:** Safe to read entirely
- **5-50KB:** Use offset/limit
- **50-500KB:** Use head/tail only
- **> 500KB:** DO NOT READ (use grep/awk)

**Never read lock files:** uv.lock (468KB), poetry.lock (>100KB), package-lock.json (>1MB)

## Command Examples

### File Search (find/Glob)

**GOOD:**
```bash
find app/platform -name "*.py" -type f -not -path "*/__pycache__/*"
Glob pattern="app/**/*.py"
```

**BAD:**
```bash
find . -name "*.py"              # Includes __pycache__
find . -type f                   # Searches entire repo
ls -R                            # Lists all files recursively
```

### Content Search (Grep)

**GOOD:**
```bash
Grep pattern="import" path="app" type="py"
Grep pattern="def test_" path="tests/unit" output_mode="files_with_matches"
Grep pattern="class" path="app" head_limit=20
```

**BAD:**
```bash
grep -r "import" .               # No exclusions, no limits
Grep pattern="test" output_mode="content"  # No head_limit
```

### File Reading (Read)

**GOOD:**
```bash
Read file_path="app/nodes/problem_framing.py"              # Full file for editing
Read file_path="app/nodes/problem_framing.py" offset=0 limit=50  # Structure only
head -20 pyproject.toml
wc -l filename
```

**BAD:**
```bash
Read file_path="pyproject.toml"  # No limits on large file
Read file_path="uv.lock"         # 468KB lock file
cat pyproject.toml               # Outputs entire file
```

### Directory Listing (ls)

**GOOD:**
```bash
ls -1 app/
find app -maxdepth 2 -type d -not -path "*/__pycache__/*"
find app -name "*.py" -type f -not -path "*/__pycache__/*" | wc -l
test -d app/platform && echo "exists"
```

**BAD:**
```bash
ls -R                            # Recursive (huge output)
find . -type d                   # No depth limit
```

### Test Commands

**GOOD:**
```bash
pytest tests/unit/platform/adapters/test_evidence.py -v
pytest -m architecture -v
pytest --collect-only -q | tail -1
```

**BAD:**
```bash
pytest -vv                       # All tests with full output
pytest --collect-only            # Includes cache
```

### Git Operations

**GOOD:**
```bash
git status --short
git log --oneline -10
git diff --name-only
```

**BAD:**
```bash
git status -uall                 # Full status with untracked
git log                          # Full log
git diff                         # Full diff
```

### Size/Count Operations

**GOOD:**
```bash
find app -name "*.py" -type f -not -path "*/__pycache__/*" | wc -l
du -sh app/
wc -l filename
```

**BAD:**
```bash
ls -R | wc -l                    # Lists all files to count
cat file | wc -l                 # Reads file to count lines
```

## Key Principles

**DO:**
- Exclude `__pycache__/`, `.git/`, `.cache/` in all searches
- Use `head_limit` in Grep commands
- Use `offset/limit` in Read commands
- Check file size before reading
- Use type filters in searches
- Limit depth in recursive operations

**DON'T:**
- Read lock files
- Search cache directories
- Read files without limits
- Use `ls -R`
- Use `pytest --collect-only` without `-q`
- Read cache/build directories
