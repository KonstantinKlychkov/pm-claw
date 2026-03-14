# Code Review Plan — feature/idea-generator

## Files to Review

### 1. `src/skills/idea_generator.py` (NEW, ~180 lines)
SCAMPER idea generation skill. Dataclass with methods:
- `generate_scamper_ideas()` — generates prompts for 7 SCAMPER categories
- `save_to_markdown()` — saves ideas to .md file with path traversal guard
- `format_report()` — plain-text output
- Module helpers: `_slugify`, `_format_markdown`, `_format_report`

### 2. `tests/test_idea_generator.py` (NEW, ~460 lines)
52 pytest tests covering all public methods and helpers.
Includes regression tests for: stale state, slugify truncation, path traversal.

### 3. `tests/test_digest_skill.py` (MODIFIED, -11/+2 lines)
Lint fixes: moved imports to top level (E402), removed unused variable (F841),
renamed ambiguous `l` variable (E741).

## Review Criteria
1. **Bugs** — logic errors, edge cases, stale state
2. **Style** — PEP8, Google docstrings, type hints, 100-char line limit
3. **Security** — path traversal, input validation
4. **Consistency** — patterns must match `src/skills/digest_skill.py`
5. **Test coverage** — missing edge cases, assertion correctness
