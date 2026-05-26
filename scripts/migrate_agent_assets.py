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
    actions: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)


def rel(path: Path, root: Path) -> str:
    try:
        return path.relative_to(root).as_posix()
    except ValueError:
        return path.as_posix()


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="replace")


def write_text(path: Path, text: str, apply: bool) -> None:
    if apply:
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

    has_canonical = (root / "AGENTS.md").exists() or (root / ".agents").exists()

    if not (root / "AGENTS.md").exists() and plan.instruction_sources:
        plan.actions.append("create AGENTS.md from vendor instruction sources")
    elif plan.instruction_sources:
        plan.actions.append("append missing vendor instruction sections to AGENTS.md")

    if plan.skill_sources:
        plan.actions.append("copy vendor skills into .agents/skills when missing")

    if has_canonical or plan.instruction_sources or plan.skill_sources:
        plan.actions.append("ensure .agents standard subdirectories exist")
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
        chunks += ["## Migrated Vendor Instructions", ""]
        for source in sources:
            chunks += [
                f"### {rel(source, root)}",
                "",
                f"Migrated on {now}. Review and fold durable guidance into the sections above.",
                "",
                "```md",
                read_text(source).strip(),
                "```",
                "",
            ]

    return "\n".join(chunks).rstrip() + "\n"


def append_missing_agents_sections(root: Path, sources: list[Path], apply: bool) -> None:
    target = root / "AGENTS.md"
    existing = read_text(target) if target.exists() else ""
    if not existing:
        write_text(target, default_agents_md(root, sources), apply)
        return

    additions: list[str] = []
    for source in sources:
        marker = f"### {rel(source, root)}"
        if marker in existing:
            continue
        additions += [
            "",
            marker,
            "",
            "Review and fold durable guidance into the main AGENTS.md sections.",
            "",
            "```md",
            read_text(source).strip(),
            "```",
            "",
        ]

    if additions:
        heading = "\n## Migrated Vendor Instructions\n"
        if "## Migrated Vendor Instructions" not in existing:
            existing = existing.rstrip() + heading
        existing = existing.rstrip() + "\n" + "\n".join(additions).rstrip() + "\n"
        write_text(target, existing, apply)


def ensure_agent_dirs(root: Path, apply: bool) -> None:
    for name in CANONICAL_SUBDIRS:
        path = root / ".agents" / name
        if apply:
            path.mkdir(parents=True, exist_ok=True)
            keep = path / ".gitkeep"
            if not keep.exists():
                keep.write_text("", encoding="utf-8")


def copy_skill(source: Path, root: Path, apply: bool) -> str:
    target_root = root / ".agents" / "skills"
    target = target_root / slugify(source.name)
    if target.exists():
        return f"skip existing skill {rel(target, root)}"
    if apply:
        target_root.mkdir(parents=True, exist_ok=True)
        shutil.copytree(source, target)
    return f"copy {rel(source, root)} -> {rel(target, root)}"


def write_shims(root: Path, mode: str, apply: bool) -> list[str]:
    actions: list[str] = []
    if mode == "none":
        return actions

    claude = root / "CLAUDE.md"
    if is_generated(claude):
        text = (
            f"{GENERATED}\n"
            "# Claude Adapter\n\n"
            "Canonical agent instructions live in `AGENTS.md`.\n"
            "Canonical reusable assets live in `.agents/`.\n"
            "Keep Claude-only deltas here only when they should not apply to other agents.\n"
        )
        write_text(claude, text, apply)
        actions.append("refresh generated CLAUDE.md adapter")
    elif claude.exists():
        actions.append("preserve existing CLAUDE.md")

    return actions


def apply_plan(plan: RepoPlan, apply: bool, adapter_mode: str) -> None:
    should_touch = bool(
        plan.instruction_sources
        or plan.skill_sources
        or (plan.root / "AGENTS.md").exists()
        or (plan.root / ".agents").exists()
    )
    if not should_touch:
        return

    ensure_agent_dirs(plan.root, apply)
    append_missing_agents_sections(plan.root, plan.instruction_sources, apply)
    for source in plan.skill_sources:
        plan.actions.append(copy_skill(source, plan.root, apply))
    if (plan.root / "AGENTS.md").exists() or plan.instruction_sources or plan.skill_sources:
        plan.actions.extend(write_shims(plan.root, adapter_mode, apply))


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
    applied = bool(args.apply and not args.dry_run)
    roots = find_repos(args.root, args.scope)
    plans = [collect_plan(root) for root in roots]
    for plan in plans:
        apply_plan(plan, applied, args.adapter_mode)

    report = render_report(plans, applied)
    if args.report:
        write_text(args.report, report, True)
    else:
        print(report)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
