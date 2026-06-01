---
audience: agent
covers: []
reviewed: 2026-06-01
review_interval: 30d
---

# Issue tracker: GitHub

Issues and PRDs for this repo live as GitHub issues. Use the `gh` CLI for operations.

## Conventions

- **Create an issue**: `gh issue create --title "..." --body "..."`. Use a heredoc for multi-line bodies.
- **Read an issue**: `gh issue view <number> --comments` and include labels when triaging.
- **List issues**: `gh issue list --state open --json number,title,body,labels,comments` with appropriate filters.
- **Comment on an issue**: `gh issue comment <number> --body "..."`.
- **Apply or remove labels**: `gh issue edit <number> --add-label "..."` or `--remove-label "..."`.
- **Close an issue**: `gh issue close <number> --comment "..."`.

Infer the repo from `git remote -v`; `gh` does this automatically when run inside this clone.

## When a skill says "publish to the issue tracker"

Create a GitHub issue in `schrmm/agent-asset-migrator`.

## When a skill says "fetch the relevant ticket"

Run `gh issue view <number> --comments`.
