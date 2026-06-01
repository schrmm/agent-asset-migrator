# Agent Asset Migration Conventions

## Sources

- Agent Skills specification: https://agentskills.io/specification is the primary authority for portable skill format, frontmatter, optional directories, and progressive disclosure.
- skills.sh: https://skills.sh/docs is the installer and discovery ecosystem for publishing, installing, updating, and ranking skills.
- AGENTS.md: open Markdown format for coding-agent instructions; no required fields.
- Codex: reads AGENTS.md and supports global/project layering.
- Claude Code: discovers skills in `.claude/skills` and `~/.claude/skills`.
- Pi: supports the Agent Skills standard and `.agents/skills`.
- Atlassian TWG: writes canonical skills to `~/.agents/skills` and copies to vendor directories when needed.

## Standards Layers

Treat the ecosystem as three separate layers:

- **Agent Skills specification** defines the portable skill package: `SKILL.md` with YAML frontmatter, optional `scripts/`, `references/`, and `assets/`, and progressive disclosure.
- **skills.sh** discovers and installs skills from GitHub, git URLs, and local paths into the target agent directories.
- **Vendor adapters** expose the same durable assets to agent-specific layouts such as `.claude/skills`, `.codex`, `.cursor`, `.gemini`, `.pi`, and `.hermes`.

Do not mix these layers. A repo can be spec-compliant without being optimized for `skills.sh`, and a repo can be installable through `skills.sh` while still needing vendor adapters for specific agents.

## Migration Goal

The migration goal is not to preserve every vendor feature as portable output. The goal is to produce Agent Skills specification-compliant assets and clearly report any vendor-specific behavior that cannot migrate 1:1.

For each non-1:1 asset, document:

- source path
- portability blocker
- migrated output, if any
- adapter-only remainder or manual follow-up
- whether the issue involves semantics, permissions, local paths, secrets, lifecycle hooks, plugin packaging, MCP integration, or agent-specific tool syntax

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

Use the Agent Skills specification as the foundation. A skill is a directory containing `SKILL.md`; optional sibling directories include `scripts/`, `references/`, and `assets/`.

Use this minimum portable `SKILL.md` format:

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
- `name` must be 1-64 characters, using lowercase letters, digits, and hyphens only.
- `name` must not start or end with a hyphen, and must not contain consecutive hyphens.
- `description` must be non-empty, should explain what the skill does and when to use it, and must stay under 1024 characters.
- Put trigger conditions in `description`.
- Keep `SKILL.md` under 500 lines; move detailed material into focused files under `references/`.
- Use `scripts/` for deterministic automation.
- Use `references/` for optional docs.
- Use `assets/` for files copied into outputs.

Optional frontmatter fields allowed by the spec include `license`, `compatibility`, `metadata`, and experimental `allowed-tools`. Prefer only `name` and `description` unless the optional field changes agent behavior or user expectations.

## Migration Policy

Default to model-led, reversible operations:

- Inventory and explain the migration plan before writes.
- Use deterministic scripts as helpers only; semantic merging belongs to the model.
- Produce spec-compliant skill packages; do not force incompatible vendor behavior into portable assets.
- Report every non-1:1 migration gap explicitly.
- Preserve source vendor files unless the user asks for cleanup.
- Copy vendor assets without rewriting their contents on the first pass.
- Prefer shims for instruction files.
- Prefer symlinks for skills when supported; otherwise copy with provenance markers.
- Never silently overwrite non-generated files.

## Claude Asset Review

Claude Code assets need explicit model review because not all of them are portable:

- `CLAUDE.md` and `.claude/CLAUDE.md`: merge durable guidance into `AGENTS.md`; keep Claude-only instructions in a shim.
- `.claude/skills/`: migrate spec-compatible skills to `.agents/skills/`, preserving skill-local `scripts/`, `references/`, and `assets/`.
- `.claude/commands/`: move reusable command prompts to `.agents/commands/`; leave Claude-only command syntax documented if it cannot be generalized.
- `.claude/agents/` and `.claude/subagents/`: move reusable subagent definitions to `.agents/subagents/`; flag model, tool, or permission assumptions.
- `.claude/hooks/`: move reusable hook scripts to `.agents/hooks/`; inspect `.claude/settings*.json` for hook registration and keep local/private settings out of canonical files.
- `.claude/templates/`: move reusable templates to `.agents/templates/`.
- `.claude/references/` and `.claude/resources/`: move durable reference material to `.agents/references/`.
- `.claude/settings.json`, `.claude/settings.local.json`, `.claude-plugin/`, and MCP config are adapter or integration configuration. Summarize durable requirements, but do not blindly move local paths, secrets, permissions, or plugin manifests into canonical assets.
