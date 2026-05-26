# agent-asset-migrator

[![skills.sh](https://skills.sh/b/schrmm/agent-asset-migrator)](https://skills.sh/schrmm/agent-asset-migrator)

Migrate agent-specific instruction files, skills, commands, hooks, subagents, templates, and references into a canonical `AGENTS.md` and `.agents/` layout.

This is a portable Agent Skill for consolidating assets from `CLAUDE.md`, `.claude`, `.codex`, `.pi`, `.hermes`, Cursor, Gemini, and similar agent-specific layouts without deleting the original files.

## Install

```powershell
npx skills add schrmm/agent-asset-migrator -g
```

To inspect the skill before installing:

```powershell
npx skills add schrmm/agent-asset-migrator --list
```

## Usage

The skill runs migrations in two passes: report first, write only after review.

```powershell
python scripts\migrate_agent_assets.py --root C:\path\to\repo --scope repo --dry-run --report C:\tmp\agent-migration-report.md
python scripts\migrate_agent_assets.py --root C:\path\to\repo --scope repo --apply
```

For a parent directory containing many repositories:

```powershell
python scripts\migrate_agent_assets.py --root C:\path\to\repos --scope tree --dry-run
```

## Canonical Target

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

## Safety

- Dry-run reports are the default workflow.
- Existing vendor files are preserved.
- Existing canonical skills are skipped.
- Existing canonical commands, hooks, subagents, templates, and references are skipped.
- Generated adapter files are refreshed only when recognized as generated.
- Empty `.agents` subdirectories get `.gitkeep` placeholders so Git can track the canonical structure.
