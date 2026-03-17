# PM Claw — OpenClaw Agent

## Overview
Personal AI assistant for Product Managers.
Built as an OpenClaw skill set with Telegram integration.
Collects news digests, conducts mini-research, generates product ideas,
and sends scheduled briefings.

## Stack
- Python 3.12
- OpenClaw framework
- Telegram Bot API (python-telegram-bot)
- pytest for testing
- ruff for linting

## Project Structure
- src/           — main application code
- src/skills/    — OpenClaw skills (each skill = .md description + .py logic)
  - digest_skill.py — RSS feed digest collection and formatting
  - idea_generator.py — SCAMPER-based product idea generation
- src/config/    — configuration and settings
- tests/         — pytest test files
- docs/          — project documentation
- docs/ideas/    — generated idea files (markdown, auto-created by IdeaGeneratorSkill)

## Commands
- Run: `python src/main.py`
- Test: `pytest tests/ -v`
- Lint: `ruff check .`
- Format: `ruff format .`

## Code Conventions
- Python 3.12, follow PEP8
- Docstrings: Google style
- Type hints: always
- Imports: stdlib → third-party → local, no wildcards
- File names: snake_case
- Max line length: 100

## Git Conventions
- Commit messages: conventional format (feat:, fix:, docs:, test:, chore:)
- Commits in English
- Never auto-commit without confirmation
- Branch naming: feature/, fix/, docs/

## OpenClaw Specifics
- Skills in src/skills/ follow OpenClaw skill format
- Each skill: frontmatter YAML + markdown body
- Agent workspace config in src/config/
- AGENTS.md will define agent personality and behavior

## Testing Rules
- Every new feature must have tests
- Test files: test_<module>.py
- Use pytest fixtures, not setUp/tearDown
- Aim for 80%+ coverage on core logic

## Custom Commands
- /test-all — run linter + tests, show quality report
- /digest-test — manual test of DigestSkill with real RSS feeds
- /commit-push-pr [description] — commit, push, and create PR in one step

## MCP Servers
- GitHub MCP — issue management, PR workflows (local scope, token not committed)
- Context7 — up-to-date library documentation (user scope)
