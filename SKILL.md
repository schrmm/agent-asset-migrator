---
name: migrate-agent-assets
description: Migrate vendor-specific AI-agent assets into Agent Skills specification-compliant SKILL.md packages and canonical AGENTS.md/.agents layouts, while flagging anything that cannot migrate 1:1. Use when migrating from CLAUDE.md, .claude, .codex, .pi, .hermes, Gemini, Cursor, or similar agent-specific assets; auditing agent asset drift; or standardizing skills for agentskills.io-compatible clients.
---

# Migrate Agent Assets

Goal: produce assets that follow the Agent Skills specification at https://agentskills.io/specification, and explicitly highlight vendor-specific behavior that cannot be migrated 1:1. Do not force incompatible settings, permissions, plugin manifests, local paths, or tool-specific syntax into a portable skill package.

## Workflow

Use a model-led two-pass migration: first inventory and explain the migration plan, then write changes only after the plan is coherent. Preserve original files unless the user explicitly asks to remove them.

1. Find scope: global home, one repo, or a parent directory containing many repos.
2. Inventory all agent assets in scope. Use direct file reads/searches first; optionally use the bundled script as a mechanical inventory helper.
3. Classify each asset as durable cross-agent guidance, reusable workflow, executable helper, reference material, static asset, or vendor-only adapter detail.
4. Propose the target canonical layout and call out conflicts, duplicates, semantic merges, and non-1:1 migration gaps that need judgment.
5. Apply only when the plan is coherent. Prefer small, reviewable writes and preserve vendor files.

The bundled script is optional support, not the authority. Use it when a deterministic inventory helps, but rely on model judgment for merging instructions, naming skills, and deciding what belongs in AGENTS.md versus `.agents/`.

Resolve the bundled script from the installed skill with these paths:

- Project install: `.agents/skills/migrate-agent-assets/scripts/migrate_agent_assets.py`
- Codex global install: `~/.codex/skills/migrate-agent-assets/scripts/migrate_agent_assets.py`
- Agent Skills global install: `~/.agents/skills/migrate-agent-assets/scripts/migrate_agent_assets.py`
- Local checkout: `<repo>/scripts/migrate_agent_assets.py`

Optional dry-run inventory:

```powershell
python <migrator-script> --root <path> --scope repo --dry-run --report <path>\agent-migration-report.md
```

Optional mechanical apply after review:

```powershell
python <migrator-script> --root <path> --scope repo --apply --adapter-mode shim
```

For a directory of repos, use `--scope tree`. The script treats Git repositories and directories with agent instruction files as candidate roots.

## Canonical Layout

Use this as the target:

```text
AGENTS.md
.agents/
  skills/<skill-name>/SKILL.md
  commands/
  subagents/
  hooks/
  templates/
  references/
```

Only `AGENTS.md` and `.agents/skills/<name>/SKILL.md` are broadly standardized. Treat the other `.agents` subfolders as a house convention for portable source-of-truth assets, with vendor adapters generated as needed.

The migrator copies these vendor asset classes into the canonical tree without rewriting their contents:

- commands -> `.agents/commands`
- hooks -> `.agents/hooks`
- agents/subagents -> `.agents/subagents`
- templates -> `.agents/templates`
- references/resources -> `.agents/references`

## Claude Asset Checklist

When migrating Claude-specific assets, inspect all of these before writing:

- `CLAUDE.md` and `.claude/CLAUDE.md`: merge durable repo guidance into `AGENTS.md`; leave Claude-only deltas in a shim only if needed.
- `.claude/skills/<name>/SKILL.md`: migrate portable skills to `.agents/skills/<name>/SKILL.md`; preserve skill-local `scripts/`, `references/`, and `assets/`.
- `.claude/commands/`: migrate reusable command prompts to `.agents/commands/` unless they are truly Claude-only.
- `.claude/agents/` and `.claude/subagents/`: migrate reusable subagent definitions to `.agents/subagents/`; flag tool/model-specific assumptions for review.
- `.claude/hooks/`: migrate hook scripts to `.agents/hooks/`; inspect `.claude/settings*.json` for hook wiring before claiming the hook is portable.
- `.claude/templates/`: migrate reusable templates to `.agents/templates/`.
- `.claude/references/` and `.claude/resources/`: migrate durable reference material to `.agents/references/`.
- `.claude/settings.json` and `.claude/settings.local.json`: do not blindly canonicalize. Extract durable policy into `AGENTS.md` or `.agents/references/`; keep local permissions, paths, and secrets out of canonical assets.
- `.claude-plugin/` and Claude plugin manifests: treat as vendor adapters. Do not convert them unless the user asks for plugin packaging.
- `.mcp.json` or MCP server config: treat as integration config. Document requirements, but do not move secrets or local machine paths into shared canonical files.

For each Claude asset, decide whether to copy, merge, summarize, leave as adapter-only, or ignore as local/private. Do not rewrite Claude-specific syntax into a generic format unless the target format is clear.

## Non-1:1 Migration Report

Every migration plan must include a section for assets that cannot become Agent Skills specification-compliant output without loss or interpretation. For each item, state:

- source path
- why it is not portable 1:1
- what was migrated, if anything
- what remains as a vendor adapter or manual follow-up
- whether the blocker is semantics, permissions, local paths, secrets, unsupported lifecycle hooks, plugin packaging, MCP integration, or agent-specific tool syntax

Common examples:

- permissions in `.claude/settings*.json`
- hook registration that depends on Claude settings
- plugin manifests under `.claude-plugin/`
- MCP server definitions with local paths, credentials, or machine-specific commands
- slash-command syntax that assumes Claude-only runtime behavior
- subagent fields that name model/tool capabilities unavailable in other clients

## AGENTS.md Shape

AGENTS.md is plain Markdown with no required frontmatter. Prefer short, durable sections:

- Project Overview
- Build And Test
- Architecture Notes
- Code Style
- Testing Policy
- Security And Safety
- Agent Asset Layout
- PR Or Commit Guidance

Do not dump every vendor instruction into AGENTS.md. Record vendor source references and merge only durable project guidance. Move reusable workflows into `.agents/skills`; leave model/tool-specific quirks in vendor shims.

## Skill Package Shape

Use the Agent Skills specification as the foundation: https://agentskills.io/specification. Use `skills.sh` conventions only for discovery, installation, and repository packaging.

For publishable `skills.sh` packages, a repository may expose either a root-level `SKILL.md` for a single skill or top-level `skills/<skill-name>/SKILL.md` directories for a skill family. Do not put publishable skills under `.agents/skills/` in the source repository; that path is an install target.

Each skill must be:

```text
.agents/skills/<lowercase-hyphen-name>/
  SKILL.md
  scripts/
  references/
  assets/
```

`SKILL.md` requires YAML frontmatter with `name` and `description`. Put trigger conditions in `description`; keep operational details in the body. Use `scripts/` for deterministic repeatable operations, `references/` for optional documentation, and `assets/` for templates or files copied into outputs.

Spec constraints worth preserving during migration:

- `name` must match the skill directory, stay under 64 characters, and use lowercase letters, digits, and hyphens only.
- `description` must describe what the skill does and when to use it, and stay under 1024 characters.
- Keep `SKILL.md` concise; move detailed material into `references/` so agents load it only when needed.
- Use optional spec fields such as `license`, `compatibility`, or `metadata` only when they clarify portability boundaries.

## Vendor Adapters

Prefer shims, symlinks, or generated copies:

- `CLAUDE.md`: point to `AGENTS.md`, plus Claude-only deltas if needed.
- `.claude/skills`: symlink or copy from `.agents/skills` for Claude Code.
- `.codex`: Codex-specific config only; keep durable repo guidance in `AGENTS.md`.
- `.pi`, `.hermes`, `.cursor`, `.gemini`: tool-specific config only unless the tool requires native assets.

If symlinks are risky on Windows or in a repo, use copy mode and mark generated files with a short header pointing back to `.agents`.

## Conflict Policy

Existing canonical files win. The migrator skips a target when the destination already exists and reports the skip. Review those conflicts manually before deleting or overwriting any vendor asset.

## References

Read `references/conventions.md` before changing migration policy or target layout.
