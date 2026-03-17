---
name: project-snapshot
description: Collect and display a compact project snapshot — branch, commits, structure, tests, and open issues.
allowed-tools: Bash(git:*), Bash(python:*), mcp__github__list_issues
---
Collect and display a compact project snapshot:

1. Current git branch and status (`git branch --show-current`, `git status --short`)
2. Last 5 commits (`git log --oneline -5`)
3. Project structure (top 2 levels, excluding __pycache__, .git, venv)
4. Test count and status (`python -m pytest tests/ --tb=no -q`)
5. Open GitHub issues (use GitHub MCP if available)

Format the output as a compact markdown report. Keep it under 50 lines.
