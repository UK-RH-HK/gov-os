"""W2-115 S1 (the switch), S2 (the scoped selection) and S3 (``gov close --select``)."""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest

from gov.cli.errors import GovError
from gov.close import command, select

from .test_w2_115_support import OWN_SUITE, OWN_TEST, TICKET, change, green_night, project

REPO_ROOT = Path(__file__).resolve().parents[3]


def _cli(root: Path, *args: str) -> subprocess.CompletedProcess:
    import os
    env = {"PATH": "/usr/bin:/bin", "PYTHONPATH": str(REPO_ROOT / "src"), "HOME": str(root.parent)}
    env.update({k: v for k, v in os.environ.items() if k == "PYTHONUSERBASE"})  # the same interpreter's packages
    return subprocess.run([sys.executable, "-m", "gov.cli.main", "close", *args, "--root", str(root)],
                          capture_output=True, text=True, env=env, cwd=str(root))


# --- S1: the switch -----------------------------------------------------------

def test_s1_no_file_is_strict(tmp_path):
    repo = project(tmp_path, mode=None)
    assert command.close_mode(repo.root) == command.STRICT


def test_s1_file_chooses(tmp_path):
    for mode in ("scoped", "strict"):  # no parametrize: the tree's opt-in list keeps only a first row
        assert command.close_mode(project(tmp_path / mode, mode=mode).root) == mode


def test_s1_other_value_or_unreadable_refuses(tmp_path):
    repo = project(tmp_path)
    for text in ("close: fast\n", "close: [scoped\n", "- scoped\n", "other: 1\n", "close: Scoped\n"):
        (repo.root / command.CLOSE_MODE_REL).write_text(text, encoding="utf-8")
        with pytest.raises(GovError) as raised:
            command.close_mode(repo.root)
        assert raised.value.code == "CLOSE_MODE_INVALID", text


def test_s1_template_and_this_repository_read_scoped(tmp_path):
    import shutil
    for rel in ("template/governance/project/close.yaml", "governance/project/close.yaml"):
        planted = tmp_path / rel.replace("/", "_") / command.CLOSE_MODE_REL
        planted.parent.mkdir(parents=True)
        shutil.copy2(REPO_ROOT / rel, planted)
        assert command.close_mode(planted.parents[2]) == command.SCOPED, rel


def test_s1_strict_mode_takes_the_strict_path(tmp_path, monkeypatch):
    """A strict project never enters the scoped close; a scoped one never enters the strict gates."""
    seen = []
    monkeypatch.setattr(command, "_run_scoped", lambda *a, **k: seen.append("scoped") or {"ok": 1})
    monkeypatch.setattr(command, "_read_count", lambda *a, **k: seen.append("strict") or (_ for _ in ()).throw(
        RuntimeError("strict")))
    args = type("A", (), {"ticket": TICKET, "select": False, "verify": False, "disposition": None,
                          "owner_decision": None, "timeout": None})()
    strict = project(tmp_path / "a", mode="strict")
    with pytest.raises(RuntimeError):
        command.run(strict.root, args, {})
    assert seen == ["strict"]
    scoped = project(tmp_path / "b", mode="scoped")
    assert command.run(scoped.root, args, {}) == {"ok": 1}
    assert seen == ["strict", "scoped"]


# --- S2: the scoped selection ---------------------------------------------------

def test_s2_own_file_selects_own_suite_and_reachable(tmp_path):
    repo = project(tmp_path)
    change(repo, {"src/pkg/feature.py": "from pkg.core import add\n\n\ndef twice(x):\n    return add(x, x)  # c\n"})
    chosen = select.scoped(repo.root, TICKET)
    assert chosen["suites"] == [OWN_SUITE]  # the own test imports feature: inside the own suite
    assert "tests" not in chosen["suites"]


def test_s2_shared_core_selects_its_mapped_suites_never_the_full(tmp_path):
    repo = project(tmp_path)
    change(repo, {"src/pkg/core.py": "def add(a, b):\n    return b + a\n"})
    chosen = select.scoped(repo.root, TICKET)
    assert chosen["suites"] == sorted([OWN_SUITE, "tests/unit/test_core.py", "tests/unit/test_core_contract.py"])
    assert "tests/unit/test_other.py" not in chosen["suites"]
    assert all(s not in ("tests", "tests/", "tests/unit", "tests/unit/") for s in chosen["suites"])


def test_s2_records_alone_select_record_reading_only(tmp_path):
    repo = project(tmp_path)
    change(repo, {"docs/notes.md": "# notes, more\n"})
    chosen = select.scoped(repo.root, TICKET)
    assert chosen["suites"] == ["tests/unit/test_records.py"]  # "and nothing else": not even the own suite
    assert chosen["records_only"] is True


def test_s2_records_alone_without_an_own_suite(tmp_path):
    repo = project(tmp_path, extra={OWN_TEST: "# no tests yet\n"})
    (repo.root / OWN_TEST).unlink()
    repo.commit("no own suite")
    change(repo, {"docs/notes.md": "# notes, more\n"})
    assert select.scoped(repo.root, TICKET)["suites"] == ["tests/unit/test_records.py"]


def test_s2_governance_alone_selects_nothing_by_itself(tmp_path):
    repo = project(tmp_path)
    change(repo, {"governance/project/briefs/a.md": "a brief\n"})
    assert select.scoped(repo.root, TICKET)["suites"] == []


def test_s2_records_and_code_together_run_the_own_suite_and_record_reading(tmp_path):
    repo = project(tmp_path)
    change(repo, {"docs/notes.md": "# more\n", "src/pkg/other.py": "def other():\n    return 1  # c\n"})
    assert select.scoped(repo.root, TICKET)["suites"] == sorted(
        [OWN_SUITE, "tests/unit/test_other.py", "tests/unit/test_records.py"])


def test_s2_unmapped_change_refuses_never_widened(tmp_path):
    repo = project(tmp_path)
    change(repo, {"src/pkg/lonely.py": "VALUE = 2\n"})
    with pytest.raises(select.SelectionRefused) as raised:
        select.scoped(repo.root, TICKET)
    assert "src/pkg/lonely.py" in raised.value.reason


def test_s2_records_committed_since_the_green_base_select_record_reading_only(tmp_path):
    """The change is everything since the last green record, not only the ticket's own commits: a record commit
    without the ticket's trailer is still the change, and records alone select record_reading only."""
    repo = project(tmp_path)
    green_night(repo)
    repo.commit("a decision", "Role: orchestrator", files={"docs/notes.md": "# notes, one decision\n"})
    chosen = select.scoped(repo.root, TICKET)
    assert chosen["suites"] == ["tests/unit/test_records.py"]
    assert chosen["records_only"] is True


def test_s2_an_unmapped_path_merged_since_the_green_base_refuses(tmp_path):
    repo = project(tmp_path)
    green_night(repo)
    repo.commit("merged", "Task: T-0009", files={"odd/unplaced.txt": "odd\n"})
    change(repo, {"src/pkg/feature.py": "from pkg.core import add\n\n\ndef twice(x):\n    return add(x, x)  # c\n"})
    with pytest.raises(select.SelectionRefused) as raised:
        select.scoped(repo.root, TICKET)
    assert "odd/unplaced.txt" in raised.value.reason
    done = _cli(repo.root, "--select", TICKET)
    assert done.returncode == 2 and select.SELECTION_REFUSED in done.stderr and done.stdout.strip() == ""


def test_s2_the_close_records_outputs_only_the_tickets_own_paths(tmp_path):
    repo = project(tmp_path)
    green_night(repo)
    repo.commit("a decision", "Role: orchestrator", files={"docs/notes.md": "# notes, one decision\n"})
    change(repo, {"src/pkg/feature.py": "from pkg.core import add\n\n\ndef twice(x):\n    return add(x, x)  # c\n"})
    chosen = select.scoped(repo.root, TICKET)
    assert "docs/notes.md" in chosen["changed"] and chosen["own"] == ["src/pkg/feature.py"]


def test_s3_pytest_options_do_not_depend_on_the_environment(monkeypatch):
    import importlib.util

    with_plugin = select.pytest_options(None)
    monkeypatch.setattr(importlib.util, "find_spec", lambda name, *a, **k: None)
    assert select.pytest_options(None) == with_plugin
    assert any(o.startswith("--timeout=") for o in with_plugin)


def test_s2_unreadable_map_refuses(tmp_path):
    repo = project(tmp_path)
    change(repo, {"governance/project/test-map.yaml": "version: [\n"})
    with pytest.raises(select.SelectionRefused):
        select.scoped(repo.root, TICKET)


def test_s2_a_root_conftest_change_refuses_rather_than_run_everything(tmp_path):
    repo = project(tmp_path)
    change(repo, {"tests/conftest.py": "X = 1\n"})
    with pytest.raises(select.SelectionRefused):
        select.scoped(repo.root, TICKET)


def test_s2_a_changed_test_file_selects_itself(tmp_path):
    repo = project(tmp_path)
    change(repo, {"tests/unit/test_other.py": "def test_other():\n    assert 1\n"})
    assert select.scoped(repo.root, TICKET)["suites"] == sorted([OWN_SUITE, "tests/unit/test_other.py"])


def test_s2_another_tickets_paths_select_its_suite(tmp_path):
    from .test_w2_115_support import ticket_text
    repo = project(tmp_path, extra={
        ".tickets/T-2.md": ticket_text("T-2", "W-2", paths=["src/pkg/lonely.py"]),
        "tests/acceptance/W-2/test_w_2.py": "def test_two():\n    assert True\n"})
    change(repo, {"src/pkg/lonely.py": "VALUE = 3\n"})
    assert select.scoped(repo.root, TICKET)["suites"] == sorted([OWN_SUITE, "tests/acceptance/W-2/"])


def test_s2_module_named_by_text_is_reached(tmp_path):
    repo = project(tmp_path, extra={"tests/unit/test_cli.py": (
        "import subprocess, sys\n\n\ndef test_cli():\n    assert 'pkg.lonely'\n")})
    change(repo, {"src/pkg/lonely.py": "VALUE = 4\n"})
    assert "tests/unit/test_cli.py" in select.scoped(repo.root, TICKET)["suites"]


# --- S3: one selection command ---------------------------------------------------

def test_s3_select_prints_the_set_and_options(tmp_path):
    repo = project(tmp_path)
    change(repo, {"src/pkg/core.py": "def add(a, b):\n    return b + a\n"})
    done = _cli(repo.root, "--select", TICKET)
    assert done.returncode == 0, done.stderr
    printed = json.loads(done.stdout)
    chosen = select.scoped(repo.root, TICKET)
    assert printed == {"ticket": TICKET, "suites": chosen["suites"], "pytest_options": chosen["pytest_options"]}
    assert "-p" in printed["pytest_options"]


def test_s3_refused_selection_prints_no_set_exit_2(tmp_path):
    repo = project(tmp_path)
    change(repo, {"src/pkg/lonely.py": "VALUE = 5\n"})
    done = _cli(repo.root, "--select", TICKET)
    assert done.returncode == 2
    assert done.stdout == ""
    assert done.stderr.startswith("SELECTION_REFUSED: ")
