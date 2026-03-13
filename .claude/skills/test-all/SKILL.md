---
name: test-all
description: Runs all tests and linting checks. Use when the user mentions testing, checking, or validating code.
allowed-tools: Bash(pytest:*), Bash(ruff:*)
---
Run the full quality check:

1. Run linter: `ruff check .`
2. Run all tests: `pytest tests/ -v`
3. Report results in this format:

## Quality Report
- 🔍 Linter: [PASS/FAIL] — [details]
- ✅ Tests: [X passed / Y failed] — [details]
- 📊 Summary: [READY / NEEDS FIXES]

If anything fails, suggest specific fixes.
