---
allowed-tools: Bash(git add:*), Bash(git status:*), Bash(git push:*), Bash(git commit:*), Bash(gh pr create:*)
argument-hint: [описание PR]
description: Commits all changes, pushes, and creates a PR
---
Review all changes, then do ALL of the following in one go:
1. Stage the appropriate files (not .claude/ config files unless they are new)
2. Create a commit with a conventional commit message
3. Push to the current branch
4. Create a pull request with title based on commit and description: $ARGUMENTS

Current status:
!git status
!git diff --stat
