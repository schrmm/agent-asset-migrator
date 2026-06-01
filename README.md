# agent-asset-migrator

[![skills.sh](https://skills.sh/b/schrmm/agent-asset-migrator)](https://skills.sh/schrmm/agent-asset-migrator)

Migrate agent-specific instruction files, skills, commands, hooks, subagents, templates, and references into Agent Skills specification-compliant assets and a canonical `AGENTS.md` / `.agents/` layout.

This is a portable Agent Skill for model-led consolidation of assets from `CLAUDE.md`, `.claude`, `.codex`, `.pi`, `.hermes`, Cursor, Gemini, and similar agent-specific layouts without deleting the original files. The model should produce assets compatible with https://agentskills.io/specification and highlight anything that cannot migrate 1:1. The bundled script is an optional inventory and safe-copy helper; the skill expects the model to make the semantic migration decisions.

## Standards

- Agent Skills specification: https://agentskills.io/specification defines the portable `SKILL.md` format, optional `scripts/`, `references/`, and `assets/` directories, and progressive disclosure model.
- skills.sh docs: https://skills.sh/docs define installer behavior, discovery, supported source formats, and distribution conventions.
- This repository publishes one single-skill package through the root `SKILL.md`, a layout supported by `skills.sh`.

## Install

```powershell
npx skills@latest add schrmm/agent-asset-migrator --global
```

To inspect the skill before installing:

```powershell
npx skills@latest add schrmm/agent-asset-migrator --list
```

## Usage

The skill runs migrations in two passes: inventory and migration plan first, write only after review. A capable model should inspect source assets directly, decide what can become Agent Skills specification-compliant output, identify what is durable versus vendor-specific, and then write the canonical files. The plan should include a non-1:1 migration section for vendor-specific behavior that must remain adapter-only or requires manual follow-up. The script can help inventory and copy known asset classes, but it should not replace semantic review.

When installed through `skills.sh`, optional script paths are:

```text
.agents/skills/migrate-agent-assets/scripts/migrate_agent_assets.py
~/.codex/skills/migrate-agent-assets/scripts/migrate_agent_assets.py
~/.agents/skills/migrate-agent-assets/scripts/migrate_agent_assets.py
```

From a local checkout, optional script usage is:

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
- `AGENTS.md` records source references and durable merged guidance; raw vendor instructions should be inspected by the model before merging.
- Existing canonical skills are skipped.
- Existing canonical commands, hooks, subagents, templates, and references are skipped.
- Generated adapter files are created or refreshed only when safe; non-generated adapters are preserved.
- Empty `.agents` subdirectories get `.gitkeep` placeholders so Git can track the canonical structure.

## skills.sh Surface

- This repository publishes one root-level skill via `SKILL.md`.
- `scripts/` and `references/` are bundled runtime assets for that skill.
- `.agents/skills/` is intentionally absent from the source repo because it is an install target.
- Verify discovery with `npx skills@latest add . --list` before publishing.
