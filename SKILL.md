---
name: migrate-agent-assets
description: Consolidate repo or global AI-agent instructions, skills, commands, hooks, templates, and references into canonical AGENTS.md and .agents layouts while preserving vendor shims. Use when migrating from CLAUDE.md, .claude, .codex, .pi, .hermes, Gemini, Cursor, or other agent-specific assets; auditing multiple repositories for agent asset drift; generating compatibility symlinks/copies; or standardizing SKILL.md packages.
---

# Migrate Agent Assets

## Workflow

Use a two-pass migration: first inventory and report, then write changes only after reviewing the plan. Preserve original files unless the user explicitly asks to remove them.

1. Find scope: global home, one repo, or a parent directory containing many repos.
2. Resolve the bundled migrator script from the installed skill. Try these paths in order:

- Project install: `.agents/skills/migrate-agent-assets/scripts/migrate_agent_assets.py`
- Codex global install: `~/.codex/skills/migrate-agent-assets/scripts/migrate_agent_assets.py`
- Agent Skills global install: `~/.agents/skills/migrate-agent-assets/scripts/migrate_agent_assets.py`
- Local checkout: `<repo>/scripts/migrate_agent_assets.py`

3. Run the migrator in dry-run mode:

```powershell
python <migrator-script> --root <path> --scope repo --dry-run --report <path>\agent-migration-report.md
```

4. Read the report. Identify duplicate or conflicting instructions that need human judgment.
5. Apply only when the plan is coherent:

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

Do not dump every vendor instruction into AGENTS.md. The migrator records vendor source references in AGENTS.md and leaves raw contents in the migration report for review. Merge durable project guidance; move reusable workflows into `.agents/skills`; leave model/tool-specific quirks in vendor shims.

## Skill Package Shape

For publishable `skills.sh` packages, a repository may expose either a root-level `SKILL.md` for a single skill or top-level `skills/<skill-name>/SKILL.md` directories for a skill family. Do not put publishable skills under `.agents/skills/` in the source repository; that path is an install target.

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

## Conflict Policy

Existing canonical files win. The migrator skips a target when the destination already exists and reports the skip. Review those conflicts manually before deleting or overwriting any vendor asset.

## References

Read `references/conventions.md` before changing migration policy or target layout.
