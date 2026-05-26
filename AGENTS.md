# AGENTS.md

## Project Overview

This repository packages the `migrate-agent-assets` Agent Skill for installation through `skills.sh` / `npx skills`.

## Build And Test

Python tooling follows the global rule: use `uv`, `ruff`, and `pytest`.

```powershell
uv run ruff check scripts\migrate_agent_assets.py
uv run python -m py_compile scripts\migrate_agent_assets.py
npx skills add . --list
```

## Agent Asset Layout

The root `SKILL.md` is the installable skill. Do not add a duplicate `.agents/skills/migrate-agent-assets/SKILL.md` inside this repo.

`scripts/` contains deterministic migration tooling. `references/` contains optional convention details loaded by the skill when migration policy needs to be changed.

## Release Notes

After publishing to GitHub, run `npx skills add schrmm/agent-asset-migrator --list` once so skills.sh sees the repository through CLI telemetry.

