# AGENTS.md

## Project Overview

This repository packages the `migrate-agent-assets` Agent Skill for installation through `skills.sh` / `npx skills`.

## Build And Test

Python tooling follows the global rule: use `uv`, `ruff`, and `pytest`.

```powershell
uv run ruff check scripts\migrate_agent_assets.py
uv run pytest
uv run python -m py_compile scripts\migrate_agent_assets.py
npx skills@latest add . --list
```

## Agent skills

### Issue tracker

Issues and PRDs live in this repo's GitHub Issues. See `docs/agents/issue-tracker.md`.

### Triage labels

Use the default Matt Pocock skill triage label vocabulary. See `docs/agents/triage-labels.md`.

### Domain docs

This is a single-context repo; read root context docs and ADRs if they exist. See `docs/agents/domain.md`.

## Agent Asset Layout

The root `SKILL.md` is the installable skill. Do not add a duplicate `.agents/skills/migrate-agent-assets/SKILL.md` inside this repo.

`scripts/` contains deterministic migration tooling. `references/` contains optional convention details loaded by the skill when migration policy needs to be changed.

## Release Notes

After publishing to GitHub, run `npx skills@latest add schrmm/agent-asset-migrator --list` once so skills.sh sees the repository through CLI telemetry.
