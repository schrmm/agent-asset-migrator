#!/usr/bin/env python3
"""Consolidate agent assets into AGENTS.md and .agents.

This script is deliberately conservative:
- dry-run is the default operating mode
- source vendor files are preserved
- existing canonical files are appended to only when content is not already present
- adapter files are written only when missing or recognized as generated
"""

from __future__ import annotations

import argparse
import datetime as dt
import os
import re
import shutil
import sys
from collections.abc import Iterable
from dataclasses import dataclass, field
from pathlib import Path

GENERATED = "<!-- generated-by: migrate-agent-assets -->"

INSTRUCTION_FILES = [
    "CLAUDE.md",
    "AGENT.md",
    "GEMINI.md",
    ".cursorrules",
    ".windsurfrules",
    ".github/copilot-instructions.md",
    ".codex/AGENTS.md",
    ".claude/CLAUDE.md",
    ".pi/AGENTS.md",
    ".hermes/AGENTS.md",
]

SKILL_DIRS = [
    ".claude/skills",
    ".codex/skills",
    ".pi/skills",
    ".pi/agent/skills",
    ".hermes/skills",
    ".cursor/skills",
    ".gemini/skills",
]

ASSET_DIRS = {
    "commands": [
        ".claude/commands",
        ".codex/commands",
        ".pi/commands",
        ".hermes/commands",
        ".cursor/commands",
        ".gemini/commands",
    ],
    "subagents": [
        ".claude/agents",
        ".claude/subagents",
        ".codex/agents",
        ".codex/subagents",
        ".pi/agents",
        ".pi/subagents",
        ".hermes/agents",
        ".hermes/subagents",
        ".cursor/agents",
        ".cursor/subagents",
        ".gemini/agents",
        ".gemini/subagents",
    ],
    "hooks": [
        ".claude/hooks",
        ".codex/hooks",
        ".pi/hooks",
        ".hermes/hooks",
        ".cursor/hooks",
        ".gemini/hooks",
    ],
    "templates": [
        ".claude/templates",
        ".codex/templates",
        ".pi/templates",
        ".hermes/templates",
        ".cursor/templates",
        ".gemini/templates",
    ],
    "references": [
        ".claude/references",
        ".claude/resources",
        ".codex/references",
        ".codex/resources",
        ".pi/references",
        ".pi/resources",
        ".hermes/references",
        ".hermes/resources",
        ".cursor/references",
        ".cursor/resources",
        ".gemini/references",
        ".gemini/resources",
    ],
}

CANONICAL_SUBDIRS = [
    "skills",
    "commands",
    "subagents",
    "hooks",
    "templates",
    "references",
]


@dataclass
class RepoPlan:
    root: Path
    instruction_sources: list[Path] = field(default_factory=list)
    skill_sources: list[Path] = field(default_factory=list)
    asset_sources: dict[str, list[Path]] = field(default_factory=dict)
    actions: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)


def rel(path: Path, root: Path) -> str:
    try:
        return path.relative_to(root).as_posix()
    except ValueError:
        return path.as_posix()


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="replace")


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8", newline="\n")


def is_generated(path: Path) -> bool:
    return path.exists() and GENERATED in read_text(path)[:500]


def slugify(name: str) -> str:
    stem = Path(name).stem.lower()
    stem = re.sub(r"[^a-z0-9]+", "-", stem).strip("-")
    return stem or "unnamed-skill"


def parse_skill_frontmatter(skill_md: Path) -> dict[str, str]:
    text = read_text(skill_md)
    if not text.startswith("---\n"):
        return {}
    end = text.find("\n---", 4)
    if end == -1:
        return {}
    result: dict[str, str] = {}
    for line in text[4:end].splitlines():
        if ":" not in line:
            continue
        key, value = line.split(":", 1)
        result[key.strip()] = value.strip().strip('"\'')
    return result


def validate_skill(source: Path) -> list[str]:
    warnings: list[str] = []
    skill_md = source / "SKILL.md"
    frontmatter = parse_skill_frontmatter(skill_md)
    expected_name = slugify(source.name)
    actual_name = frontmatter.get("name", "")
    description = frontmatter.get("description", "")

    if not frontmatter:
        warnings.append(f"{source}: SKILL.md has missing or malformed YAML frontmatter")
        return warnings
    if not actual_name:
        warnings.append(f"{source}: SKILL.md frontmatter is missing name")
    elif slugify(actual_name) != expected_name:
        warnings.append(f"{source}: skill name '{actual_name}' does not match directory '{source.name}'")
    if not description:
        warnings.append(f"{source}: SKILL.md frontmatter is missing description")
    elif "use when" not in description.lower():
        warnings.append(f"{source}: description should include trigger wording such as 'Use when ...'")
    return warnings


def find_repos(root: Path, scope: str) -> list[Path]:
    root = root.resolve()
    if scope in {"repo", "global"}:
        return [root]

    repos: list[Path] = []
    marker_roots: list[Path] = []
    for current, dirs, files in os.walk(root):
        path = Path(current)
        names = set(dirs) | set(files)
        if ".git" in dirs:
            repos.append(path)
            dirs[:] = []
            continue
        if names & {"AGENTS.md", "CLAUDE.md", "GEMINI.md", "AGENT.md"}:
            marker_roots.append(path)
        dirs[:] = [d for d in dirs if d not in {".git", "node_modules", ".venv", "venv", "dist", "build", ".next"}]

    repo_set = set(repos)
    for marker in marker_roots:
        if not any(marker == repo or repo in marker.parents for repo in repo_set):
            repo_set.add(marker)
    return sorted(repo_set)


def collect_plan(root: Path) -> RepoPlan:
    plan = RepoPlan(root=root)

    for item in INSTRUCTION_FILES:
        path = root / item
        if path.exists() and path.is_file():
            plan.instruction_sources.append(path)

    for item in SKILL_DIRS:
        base = root / item
        if not base.is_dir():
            continue
        for child in sorted(base.iterdir()):
            if child.is_dir() and (child / "SKILL.md").is_file():
                plan.skill_sources.append(child)
                plan.warnings.extend(validate_skill(child))

    for target_name, source_dirs in ASSET_DIRS.items():
        for item in source_dirs:
            base = root / item
            if base.is_dir():
                plan.asset_sources.setdefault(target_name, []).append(base)

    has_canonical = (root / "AGENTS.md").exists() or (root / ".agents").exists()

    if has_canonical or plan.instruction_sources or plan.skill_sources or plan.asset_sources:
        plan.actions = planned_actions(plan, "shim")
    return plan


def default_agents_md(root: Path, sources: list[Path]) -> str:
    now = dt.date.today().isoformat()
    chunks = [
        "# AGENTS.md",
        "",
        "## Project Overview",
        "",
        "Add a short description of this project and the main ownership boundaries.",
        "",
        "## Build And Test",
        "",
        "Document the common setup, lint, typecheck, test, and dev-server commands.",
        "",
        "## Architecture Notes",
        "",
        "Document the important module boundaries and domain terms agents should preserve.",
        "",
        "## Code Style",
        "",
        "Document language, framework, formatting, and naming conventions.",
        "",
        "## Testing Policy",
        "",
        "Document when to add tests and which commands verify the relevant behavior.",
        "",
        "## Security And Safety",
        "",
        "Document secrets, credentials, destructive commands, data handling, and approval expectations.",
        "",
        "## Agent Asset Layout",
        "",
        "Canonical agent assets live in `AGENTS.md` and `.agents/`. Vendor folders are compatibility adapters.",
        "",
    ]

    if sources:
        chunks += ["## Migrated Vendor Instruction Sources", ""]
        chunks += ["Review the migration report, then fold durable guidance into the sections above.", ""]
        for source in sources:
            chunks.append(f"- `{rel(source, root)}` discovered on {now}")
        chunks.append("")

    return "\n".join(chunks).rstrip() + "\n"


def append_missing_agents_sections(root: Path, sources: list[Path]) -> None:
    target = root / "AGENTS.md"
    existing = read_text(target) if target.exists() else ""
    if not existing:
        write_text(target, default_agents_md(root, sources))
        return

    additions: list[str] = []
    for source in sources:
        marker = f"`{rel(source, root)}`"
        if marker in existing:
            continue
        additions.append(f"- {marker}")

    if additions:
        heading = (
            "\n## Migrated Vendor Instruction Sources\n\n"
            "Review the migration report, then fold durable guidance into the main AGENTS.md sections.\n"
        )
        if "## Migrated Vendor Instruction Sources" not in existing:
            existing = existing.rstrip() + heading
        existing = existing.rstrip() + "\n" + "\n".join(additions).rstrip() + "\n"
        write_text(target, existing)


def ensure_agent_dirs(root: Path) -> None:
    for name in CANONICAL_SUBDIRS:
        path = root / ".agents" / name
        path.mkdir(parents=True, exist_ok=True)
        keep = path / ".gitkeep"
        if not keep.exists():
            keep.write_text("", encoding="utf-8")


def copy_skill(source: Path, root: Path) -> None:
    target_root = root / ".agents" / "skills"
    target = target_root / slugify(source.name)
    if target.exists():
        return
    target_root.mkdir(parents=True, exist_ok=True)
    shutil.copytree(source, target)


def copy_asset_dir(source: Path, root: Path, target_name: str) -> None:
    target_root = root / ".agents" / target_name
    for item in sorted(source.rglob("*")):
        if item.is_dir():
            continue
        relative = item.relative_to(source)
        target = target_root / relative
        if target.exists():
            continue
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(item, target)


def shim_text() -> str:
    return (
        f"{GENERATED}\n"
        "# Claude Adapter\n\n"
        "Canonical agent instructions live in `AGENTS.md`.\n"
        "Canonical reusable assets live in `.agents/`.\n"
        "Keep Claude-only deltas here only when they should not apply to other agents.\n"
    )


def write_shims(root: Path, mode: str) -> None:
    if mode == "none":
        return

    claude = root / "CLAUDE.md"
    if is_generated(claude) or not claude.exists():
        write_text(claude, shim_text())


def should_touch(plan: RepoPlan) -> bool:
    return bool(
        plan.instruction_sources
        or plan.skill_sources
        or plan.asset_sources
        or (plan.root / "AGENTS.md").exists()
        or (plan.root / ".agents").exists()
    )


def planned_actions(plan: RepoPlan, adapter_mode: str) -> list[str]:
    if not should_touch(plan):
        return []

    actions = ["ensure .agents standard subdirectories exist"]
    agents = plan.root / "AGENTS.md"
    if not agents.exists() and plan.instruction_sources:
        actions.append("create AGENTS.md with vendor instruction source references")
    elif plan.instruction_sources:
        actions.append("append missing vendor instruction source references to AGENTS.md")

    for source in plan.skill_sources:
        target = plan.root / ".agents" / "skills" / slugify(source.name)
        if target.exists():
            actions.append(f"skip existing skill {rel(target, plan.root)}")
        else:
            actions.append(f"copy {rel(source, plan.root)} -> {rel(target, plan.root)}")

    for target_name, sources in sorted(plan.asset_sources.items()):
        for source in sources:
            target_root = plan.root / ".agents" / target_name
            for item in sorted(source.rglob("*")):
                if item.is_dir():
                    continue
                target = target_root / item.relative_to(source)
                if target.exists():
                    actions.append(f"skip existing {rel(target, plan.root)}")
                else:
                    actions.append(f"copy {rel(item, plan.root)} -> {rel(target, plan.root)}")

    if adapter_mode != "none" and (agents.exists() or plan.instruction_sources or plan.skill_sources):
        claude = plan.root / "CLAUDE.md"
        if is_generated(claude):
            actions.append("refresh generated CLAUDE.md adapter")
        elif claude.exists():
            actions.append("preserve existing CLAUDE.md")
        else:
            actions.append("create generated CLAUDE.md adapter")

    return actions


def apply_plan(plan: RepoPlan, apply: bool, adapter_mode: str) -> None:
    plan.actions = planned_actions(plan, adapter_mode)
    if not apply or not should_touch(plan):
        return

    ensure_agent_dirs(plan.root)
    append_missing_agents_sections(plan.root, plan.instruction_sources)
    for source in plan.skill_sources:
        copy_skill(source, plan.root)
    for target_name, sources in sorted(plan.asset_sources.items()):
        for source in sources:
            copy_asset_dir(source, plan.root, target_name)
    if (plan.root / "AGENTS.md").exists() or plan.instruction_sources or plan.skill_sources:
        write_shims(plan.root, adapter_mode)


def render_report(plans: Iterable[RepoPlan], applied: bool) -> str:
    lines = [
        "# Agent Asset Migration Report",
        "",
        f"Mode: {'apply' if applied else 'dry-run'}",
        f"Generated: {dt.datetime.now().isoformat(timespec='seconds')}",
        "",
    ]
    for plan in plans:
        lines += [f"## {plan.root}", ""]
        lines += ["Instruction sources:"]
        lines += [f"- {rel(p, plan.root)}" for p in plan.instruction_sources] or ["- none"]
        lines += ["", "Skill sources:"]
        lines += [f"- {rel(p, plan.root)}" for p in plan.skill_sources] or ["- none"]
        lines += ["", "Asset sources:"]
        if plan.asset_sources:
            for target_name, sources in sorted(plan.asset_sources.items()):
                for source in sources:
                    lines.append(f"- {rel(source, plan.root)} -> .agents/{target_name}")
        else:
            lines.append("- none")
        lines += ["", "Actions:"]
        lines += [f"- {item}" for item in plan.actions] or ["- none"]
        if plan.warnings:
            lines += ["", "Warnings:"]
            lines += [f"- {item}" for item in plan.warnings]
        lines.append("")
    return "\n".join(lines)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", required=True, type=Path, help="Repo root, parent directory, or home directory.")
    parser.add_argument("--scope", choices=["repo", "tree", "global"], default="repo")
    parser.add_argument("--apply", action="store_true", help="Write changes. Without this, only report.")
    parser.add_argument("--dry-run", action="store_true", help="Force report-only mode.")
    parser.add_argument("--adapter-mode", choices=["shim", "none"], default="shim")
    parser.add_argument("--report", type=Path, help="Write markdown report to this path.")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if not args.root.exists() or not args.root.is_dir():
        print(f"error: --root must be an existing directory: {args.root}", file=sys.stderr)
        return 2
    applied = bool(args.apply and not args.dry_run)
    roots = find_repos(args.root, args.scope)
    plans = [collect_plan(root) for root in roots]
    for plan in plans:
        apply_plan(plan, applied, args.adapter_mode)

    report = render_report(plans, applied)
    if args.report:
        write_text(args.report, report)
    else:
        print(report)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
