---
audience: agent
covers: []
reviewed: 2026-06-01
review_interval: 30d
---

# Domain Docs

How engineering skills should consume this repo's domain documentation when exploring the codebase.

## Before exploring, read these

- `CONTEXT.md` at the repo root, if present.
- `docs/adr/` for ADRs that touch the area being changed, if present.

If these files do not exist, proceed silently. Do not flag their absence or create them unless the user asks or a docs-oriented skill requires it.

## File structure

Single-context repo:

```text
/
|-- CONTEXT.md
|-- docs/adr/
|   |-- 0001-example.md
|-- scripts/
|-- references/
|-- SKILL.md
```

## Use the repo vocabulary

This repo packages a single Agent Skill, `migrate-agent-assets`, and a deterministic Python migrator. Prefer these terms consistently:

- **source repo**: this publishable skill package.
- **installed skill**: a copy under `.agents/skills/`, `~/.agents/skills/`, or `~/.codex/skills/`.
- **canonical layout**: `AGENTS.md` plus `.agents/` in a target repository.
- **vendor adapter**: tool-specific files such as `CLAUDE.md`, `.claude/`, `.codex/`, `.cursor/`, `.gemini/`, `.pi/`, or `.hermes/`.

If output contradicts a future ADR, surface the conflict explicitly rather than silently overriding it.
