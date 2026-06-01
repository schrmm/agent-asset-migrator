---
audience: agent
covers: ["scripts/migrate_agent_assets.py"]
synced: c273ea0a890723985f4719bf827da63129fd7c74
reviewed: 2026-05-27
review_interval: 30d
---

# Agent Asset Migrator Script

## Purpose

`scripts/migrate_agent_assets.py` is the deterministic migration tool behind the
`migrate-agent-assets` skill. It consolidates vendor-specific agent instruction
files and reusable assets into the canonical `AGENTS.md` and `.agents/` layout
without deleting the original vendor files.

The script is intentionally conservative:

- dry-run/report mode is the default unless `--apply` is passed
- existing canonical files win over vendor sources
- vendor files are preserved
- raw vendor instruction contents stay in the migration report rather than being
  dumped into `AGENTS.md`
- adapter files are created or refreshed only when safe; non-generated adapters
  are preserved

## CLI

Run the script with an explicit root:

```powershell
python scripts\migrate_agent_assets.py --root C:\path\to\repo --scope repo --dry-run --report C:\tmp\agent-migration-report.md
python scripts\migrate_agent_assets.py --root C:\path\to\repo --scope repo --apply --adapter-mode shim
```

Arguments:

- `--root`: repository, parent tree, or global directory to inspect
- `--scope`: `repo`, `tree`, or `global`; `tree` discovers nested repositories
  and marker directories
- `--apply`: write filesystem changes
- `--dry-run`: force report-only mode even if `--apply` is also present
- `--adapter-mode`: `shim` or `none`; `shim` manages generated adapter files
- `--report`: write the markdown migration report to a file instead of stdout

## Discovery

`collect_plan()` scans a root for known vendor instruction files, skill
directories, and asset directories.

Instruction sources include common files such as `CLAUDE.md`, `GEMINI.md`,
`.cursorrules`, `.github/copilot-instructions.md`, and vendor-specific nested
adapter files.

Skill sources are directories under known vendor skill roots that contain a
`SKILL.md`. Each discovered skill is validated for portable frontmatter:

- `name` must exist and match the skill directory after slugification
- `description` must exist
- `description` should include trigger wording such as `Use when ...`

Reusable assets are copied by category into `.agents/commands`,
`.agents/subagents`, `.agents/hooks`, `.agents/templates`, and
`.agents/references`.

## Write Behavior

`apply_plan()` is the only path that mutates the repository. It first decides
whether the root has anything relevant to migrate, then:

1. Ensures the canonical `.agents` subdirectories exist.
2. Creates or appends missing vendor instruction source references in
   `AGENTS.md`.
3. Copies vendor skills into `.agents/skills/<slug>` only when the target is
   missing.
4. Copies vendor asset files into the matching `.agents/<category>` directory
   only when the target file is missing.
5. Creates or refreshes generated adapter shims when `--adapter-mode shim` is
   active and preserves non-generated adapters.

`--apply` must be present and `--dry-run` absent for writes to occur. Otherwise
the script only prints or writes the migration report.

## Generated Adapters

Generated adapter files are identified by the marker:

```md
<!-- generated-by: migrate-agent-assets -->
```

Currently, `write_shims()` manages a generated `CLAUDE.md` adapter. If an
existing `CLAUDE.md` lacks the generated marker, the script preserves it and
reports `preserve existing CLAUDE.md`. If no `CLAUDE.md` exists and shim mode is
active, the script creates a generated adapter.

## Reports

`render_report()` produces a markdown report for every planned root. Each root
section includes:

- instruction sources
- skill sources
- asset sources
- planned or applied actions, generated from the same planning path
- validation warnings

Reports are useful both for dry-run review and for recording applied migration
work through `--report`.

## Extension Notes

When changing migration policy or target layout, update
`references/conventions.md` and keep `SKILL.md` aligned with the script. New
vendor ecosystems should be added to the discovery constants near the top of the
script so collection, reporting, and application behavior stay deterministic.
