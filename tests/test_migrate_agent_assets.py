from __future__ import annotations

import importlib.util
import sys
from pathlib import Path


def load_migrator():
    script = Path(__file__).resolve().parents[1] / "scripts" / "migrate_agent_assets.py"
    spec = importlib.util.spec_from_file_location("migrate_agent_assets", script)
    assert spec is not None
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def test_agents_md_records_vendor_sources_without_raw_dump(tmp_path: Path) -> None:
    migrator = load_migrator()
    raw_guidance = "DO NOT INLINE THIS RAW VENDOR GUIDANCE"
    (tmp_path / "GEMINI.md").write_text(raw_guidance, encoding="utf-8")

    plan = migrator.collect_plan(tmp_path)
    migrator.apply_plan(plan, True, "none")

    agents = (tmp_path / "AGENTS.md").read_text(encoding="utf-8")
    assert "`GEMINI.md`" in agents
    assert raw_guidance not in agents


def test_dry_run_reports_actions_without_writing(tmp_path: Path) -> None:
    migrator = load_migrator()
    (tmp_path / ".claude" / "commands").mkdir(parents=True)
    (tmp_path / ".claude" / "commands" / "review.md").write_text("review", encoding="utf-8")

    plan = migrator.collect_plan(tmp_path)
    migrator.apply_plan(plan, False, "shim")

    assert "ensure .agents standard subdirectories exist" in plan.actions
    assert "copy .claude/commands/review.md -> .agents/commands/review.md" in plan.actions
    assert not (tmp_path / ".agents").exists()


def test_apply_executes_same_reported_asset_action(tmp_path: Path) -> None:
    migrator = load_migrator()
    (tmp_path / ".claude" / "commands").mkdir(parents=True)
    (tmp_path / ".claude" / "commands" / "review.md").write_text("review", encoding="utf-8")

    plan = migrator.collect_plan(tmp_path)
    migrator.apply_plan(plan, True, "shim")

    assert "copy .claude/commands/review.md -> .agents/commands/review.md" in plan.actions
    assert (tmp_path / ".agents" / "commands" / "review.md").read_text(encoding="utf-8") == "review"


def test_shim_mode_creates_missing_generated_claude_adapter(tmp_path: Path) -> None:
    migrator = load_migrator()
    (tmp_path / "AGENTS.md").write_text("# AGENTS.md\n", encoding="utf-8")

    plan = migrator.collect_plan(tmp_path)
    migrator.apply_plan(plan, True, "shim")

    claude = (tmp_path / "CLAUDE.md").read_text(encoding="utf-8")
    assert migrator.GENERATED in claude
    assert "Canonical agent instructions live in `AGENTS.md`." in claude


def test_main_rejects_missing_root(monkeypatch, capsys, tmp_path: Path) -> None:
    migrator = load_migrator()
    missing = tmp_path / "missing"
    monkeypatch.setattr(sys, "argv", ["migrate_agent_assets.py", "--root", str(missing)])

    assert migrator.main() == 2
    captured = capsys.readouterr()
    assert "--root must be an existing directory" in captured.err
