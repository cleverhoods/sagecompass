# Local scope: tests

This file is the **primary** instruction surface when editing `tests/**`.

## Scope
- Tests follow two-dimensional structure: `tests/[test_type]/[category]/[mirrored_structure]`
- Test types: unit, integration, e2e
- Test categories: architecture, platform, orchestration
- All test organization rules, naming conventions, priorities, and quality guidelines are defined in `.shared/rules/testing.md`

## Token Efficiency (Critical)
**Before any command:**
Never read files/directories listed in `.claudeignore`. Use exclusion patterns in all search commands. See `.shared/efficient-commands.md` for token-efficient command patterns.

## References
- Backend contract: `../CLAUDE.md`
- System map: `../.shared/sys.yml`
- **Test organization rules:** `../.shared/rules/testing.md`
- Token efficiency: `../.shared/efficient-commands.md`
