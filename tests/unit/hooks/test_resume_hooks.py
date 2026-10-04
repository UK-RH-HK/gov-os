"""Builder tests for the W1-49 hooks (regression evidence only; the acceptance tests are in tests/acceptance/W1-49)."""

from __future__ import annotations

import json
import os
import subprocess
import sys
import time
from pathlib import Path

HOOKS = Path(__file__).resolve().parents[3] / "template/governance/kernel/hooks"
ORCH = ".gov-runtime/scratch/orchestrator/CHECKPOINT.md"

sys.path.insert(0, str(HOOKS))
import precompact  # noqa: E402
import sessionstart  # noqa: E402


def _run(name, root, stdin, role):
    env = {"PATH": os.environ["PATH"], "CLAUDE_PROJECT_DIR": str(root), "PYTHONDONTWRITEBYTECODE": "1"}
    if role is not None:
        env["GOV_ROLE"] = role
    return subprocess.run([sys.executable, str(HOOKS / name)], input=json.dumps(stdin), capture_output=True,
                          text=True, cwd=str(root), env=env, timeout=30, check=False)


def _checkpoint(root, age_s):
    path = root / ORCH
    path.parent.mkdir(parents=True)
    path.write_text("# C\n\n## RESUME HERE\n\n- SECRET-71\n", encoding="utf-8")
    stamp = time.time() - age_s
    os.utime(path, (stamp, stamp))


def test_resume_section_ends_at_a_heading_of_the_same_or_a_higher_level():
    text = "# Top\n\n## Before\nx\n## RESUME HERE now\na\n### Sub\nb\n## After\nc\n"
    assert sessionstart.resume_section(text) == "## RESUME HERE now\na\n### Sub\nb"
    assert sessionstart.resume_section("# Top\n\nRESUME HERE in prose\n") == ""


def test_current_is_at_most_thirty_minutes_old(tmp_path):
    _checkpoint(tmp_path, age_s=29 * 60)
    assert precompact.is_current(str(tmp_path), ORCH)
    stamp = time.time() - 31 * 60
    os.utime(tmp_path / ORCH, (stamp, stamp))
    assert not precompact.is_current(str(tmp_path), ORCH)


def test_an_unset_role_is_not_the_orchestrator(tmp_path):
    """DEC-259: PreCompact does not block and SessionStart injects nothing."""
    _checkpoint(tmp_path, age_s=3 * 24 * 3600)
    before = _run("precompact.py", tmp_path, {"trigger": "manual"}, role=None)
    after = _run("sessionstart.py", tmp_path, {"source": "compact"}, role=None)
    assert (before.returncode, before.stdout, before.stderr) == (0, "", "")
    assert (after.returncode, after.stdout) == (0, "")


def test_precompact_blocks_only_the_orchestrators_manual_compaction(tmp_path):
    _checkpoint(tmp_path, age_s=3 * 24 * 3600)
    assert _run("precompact.py", tmp_path, {"trigger": "manual"}, role="orchestrator").returncode == 2
    assert _run("precompact.py", tmp_path, {"trigger": "auto"}, role="orchestrator").returncode == 0
    assert _run("precompact.py", tmp_path, ["not an object"], role="orchestrator").returncode == 0
