# Agent Asset Migration Conventions

## Sources

- AGENTS.md: open Markdown format for coding-agent instructions; no required fields.
- Codex: reads AGENTS.md and supports global/project layering.
- Claude Code: discovers skills in `.claude/skills` and `~/.claude/skills`.
- Pi: supports the Agent Skills standard and `.agents/skills`.
- Atlassian TWG: writes canonical skills to `~/.agents/skills` and copies to vendor directories when needed.

## Canonical Ownership

Use these paths as the durable source of truth:

```text
AGENTS.md
.agents/
  skills/
  commands/
  subagents/
  hooks/
  templates/
  references/
```

Asset mapping:

```text
vendor commands            -> .agents/commands/
vendor hooks               -> .agents/hooks/
vendor agents/subagents    -> .agents/subagents/
vendor templates           -> .agents/templates/
vendor references/resources -> .agents/references/
```

Treat vendor directories as adapters:

```text
.claude/
.codex/
.pi/
.hermes/
.cursor/
.gemini/
.github/
```

## AGENTS.md Format

AGENTS.md is Markdown only. Do not add YAML frontmatter. Keep it concise enough to remain useful when loaded into agent context.

Recommended sections:

```md
# AGENTS.md

## Project Overview

## Build And Test

## Architecture Notes

## Code Style

## Testing Policy

## Security And Safety

## Agent Asset Layout

## PR Or Commit Guidance
```

Use nested `AGENTS.md` files in monorepos when subprojects have different commands or conventions.

## Skill Format

Use this minimum portable format:

```md
---
name: example-skill
description: What the skill does. Use when the user asks for specific matching tasks or contexts.
---

# Example Skill

## Workflow
```

Rules:

- Skill directory name must match `name`.
- Use lowercase letters, digits, and hyphens.
- Put trigger conditions in `description`.
- Use `scripts/` for deterministic automation.
- Use `references/` for optional docs.
- Use `assets/` for files copied into outputs.

## Migration Policy

Default to reversible operations:

- Create reports before writes.
- Preserve source vendor files unless the user asks for cleanup.
- Copy vendor assets without rewriting their contents on the first pass.
- Prefer shims for instruction files.
- Prefer symlinks for skills when supported; otherwise copy with provenance markers.
- Never silently overwrite non-generated files.
