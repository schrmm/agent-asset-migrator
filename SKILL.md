---
name: migrate-agent-assets
description: Consolidate repo or global AI-agent instructions, skills, commands, hooks, templates, and references into canonical AGENTS.md and .agents layouts while preserving vendor shims. Use when migrating from CLAUDE.md, .claude, .codex, .pi, .hermes, Gemini, Cursor, or other agent-specific assets; auditing multiple repositories for agent asset drift; generating compatibility symlinks/copies; or standardizing SKILL.md packages.
---

# Migrate Agent Assets

## Workflow

Use a two-pass migration: first inventory and report, then write changes only after reviewing the plan. Preserve original files unless the user explicitly asks to remove them.

1. Find scope: global home, one repo, or a parent directory containing many repos.
2. Run the migrator in dry-run mode:

```powershell
python <skill-dir>\scripts\migrate_agent_assets.py --root <path> --scope repo --dry-run --report <path>\agent-migration-report.md
```

3. Read the report. Identify duplicate or conflicting instructions that need human judgment.
4. Apply only when the plan is coherent:

```powershell
python <skill-dir>\scripts\migrate_agent_assets.py --root <path> --scope repo --apply --adapter-mode shim
```

For a directory of repos, use `--scope tree`. The script treats directories with `.git`, `AGENTS.md`, `CLAUDE.md`, `.agents`, `.claude`, `.codex`, `.pi`, or `.hermes` as candidate roots.

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

Do not dump every vendor instruction into AGENTS.md. Merge durable project guidance; move reusable workflows into `.agents/skills`; leave model/tool-specific quirks in vendor shims.

## Skill Package Shape

Each skill must be:

```text
.agents/skills/<lowercase-hyphen-name>/
  SKILL.md
  scripts/
  references/
  assets/
```

`SKILL.md` requires YAML frontmatter with only `name` and `description` for maximum portability. Put trigger conditions in `description`; keep operational details in the body. Use `scripts/` for deterministic repeatable operations, `references/` for optional documentation, and `assets/` for templates or files copied into outputs.

## Vendor Adapters

Prefer shims, symlinks, or generated copies:

- `CLAUDE.md`: point to `AGENTS.md`, plus Claude-only deltas if needed.
- `.claude/skills`: symlink or copy from `.agents/skills` for Claude Code.
- `.codex`: Codex-specific config only; keep durable repo guidance in `AGENTS.md`.
- `.pi`, `.hermes`, `.cursor`, `.gemini`: tool-specific config only unless the tool requires native assets.

If symlinks are risky on Windows or in a repo, use copy mode and mark generated files with a short header pointing back to `.agents`.

## References

Read `references/conventions.md` before changing migration policy or target layout.
