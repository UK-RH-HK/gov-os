"""Builder tests for the role table (MR-1 to MR-3; DEC-1246 (3)(b)): regression evidence, not acceptance."""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO / "src"))

from gov.cli.errors import GovError  # noqa: E402
from gov.launch import criticality, launcher, role_table  # noqa: E402

ROW = "  - {{role: {role}, model: {model}, effort: {effort}, decided: DEC-1242 R-4}}\n"


def text(*rows, version=1):
    return f"version: {version}\nrows:\n" + "".join(ROW.format(role=r, model=m, effort=e) for r, m, e in rows)


def planted(tmp_path, body):
    (tmp_path / "governance/project").mkdir(parents=True)
    (tmp_path / role_table.REL).write_text(body, encoding="utf-8")
    return tmp_path


def test_the_real_table_is_the_kit_s_and_holds_the_ten_rows():
    real = (REPO / role_table.REL).read_bytes()
    assert real == (REPO / role_table.KIT_REL).read_bytes()
    table = role_table.load(REPO)
    assert len(table) == 10 and table["lead"] == {"model": "claude-sonnet-5-5", "effort": "medium",
                                                  "decided": "DEC-1242 R-4, DEC-1236 (2)"}
    assert table["orchestrator"]["model"] == table["senior-engineer"]["model"] == table["audit-wide"]["model"] == \
        "claude-opus-5-5"
    assert role_table.check_roles(REPO) == []


@pytest.mark.parametrize("body", (
    "version: 1\nrows: [\n",
    "version: 2\nrows: []\n",
    "rows: []\n",
    "version: 1\nrows: {}\n",
    text(("engineer", "claude-sonnet-5-5", "high"), ("engineer", "claude-sonnet-5-5", "low")),
    text(("engineer", "claude-fable-5", "high")),
    text(("engineer", "gpt-5", "high")),
    text(("engineer", "claude-sonnet-5-5", "ultra")),
    "version: 1\nrows:\n  - {role: engineer, model: claude-sonnet-5-5, effort: high}\n",
    "version: 1\nrows:\n  - {role: engineer, model: claude-sonnet-5-5, effort: high, decided: x, extra: 1}\n",
))
def test_a_table_that_cannot_be_read_or_is_wrong_refuses(tmp_path, body):
    root = planted(tmp_path, body)
    with pytest.raises(GovError) as raised:
        role_table.load(root)
    assert raised.value.code == "LAUNCH_REFUSED" and role_table.REL in raised.value.message
    with pytest.raises(GovError):
        role_table.row_for(root, "engineer")


def test_row_for_gives_a_lead_the_lead_row_and_none_without_a_file_or_a_row(tmp_path):
    assert role_table.row_for(tmp_path, "engineer") is None
    root = planted(tmp_path, text(("lead", "claude-sonnet-5-5", "low"), ("orchestrator", "claude-opus-5-5", "high")))
    assert role_table.row_for(root, "lead")["effort"] == "low"
    assert role_table.row_for(root, "ticket-lead")["effort"] == "low"
    assert role_table.row_for(root, "engineer") is None


def test_the_launcher_s_lead_setting_follows_the_table_and_falls_back_to_its_own(tmp_path):
    assert launcher._lead_setting(tmp_path) == (launcher.LEAD_MODEL, launcher.LEAD_EFFORT)
    root = planted(tmp_path, text(("lead", "claude-sonnet-5-5", "low")))
    assert launcher._lead_setting(root) == ("claude-sonnet-5-5", "low")
    assert launcher._lead_effort_args(["-p"], root) == ["--effort", "low"]
    assert launcher._lead_effort_args(["--effort", "high"], root) == []
    (root / role_table.REL).write_text("version: 1\nrows: [\n")
    with pytest.raises(GovError):
        launcher._lead_setting(root)


def test_a_role_file_that_differs_from_its_row_is_found(tmp_path):
    root = planted(tmp_path, text(("engineer", "claude-sonnet-5-5", "high"), ("lead", "claude-sonnet-5-5", "medium")))
    folder = root / "template/governance/kernel/roles"
    folder.mkdir(parents=True)
    (folder / "engineer.md").write_text("- **Launch default:** model claude-sonnet-5-5, effort medium\n")
    (folder / "ticket-lead.md").write_text("- **Launch default:** model claude-sonnet-5-5, effort medium\n")
    found = role_table.check_roles(root)
    assert [(f["role"], f["found"], f["table"]["effort"]) for f in found] == [
        ("engineer", {"model": "claude-sonnet-5-5", "effort": "medium"}, "high")]


def test_a_role_file_with_no_line_of_the_form_is_found(tmp_path):
    root = planted(tmp_path, text(("engineer", "claude-sonnet-5-5", "high")))
    folder = root / "template/governance/kernel/roles"
    folder.mkdir(parents=True)
    (folder / "engineer.md").write_text("no line here\n")
    assert [f["role"] for f in role_table.check_roles(root)] == ["engineer"]


def git(cwd, *args, **kw):
    return subprocess.run(["git", "-c", "user.name=t", "-c", "user.email=t@t", *args], cwd=cwd, check=True,
                          capture_output=True, text=True, **kw)


def commit(root, body, message):
    (root / role_table.REL).write_text(body, encoding="utf-8")
    git(root, "add", "-A")
    git(root, "commit", "-q", "-m", message)


def test_a_row_changed_without_the_owner_trailer_is_reported_by_field(tmp_path):
    root = planted(tmp_path, text(("engineer", "claude-sonnet-5-5", "high")))
    git(root, "init", "-q")
    commit(root, text(("engineer", "claude-sonnet-5-5", "high")), "first")
    commit(root, text(("engineer", "claude-sonnet-5-5", "xhigh")), "no trailer")
    commit(root, text(("engineer", "claude-sonnet-5-5", "max")), "owner\n\nDecided-by: owner")
    commit(root, text(("engineer", "claude-sonnet-5-5", "max"), ("research", "claude-sonnet-5-5", "low")), "added")
    found = role_table.check_range(root, "HEAD~3..HEAD")
    assert [(f["role"], f["field"], f["old"], f["new"]) for f in found] == [
        ("engineer", "effort", "high", "xhigh"), ("research", "row", None, "model claude-sonnet-5-5, effort low")]
    assert role_table.check_range(root, "HEAD~2..HEAD~1") == []
    git(root, "commit", "-q", "--allow-empty", "-m", "elsewhere")
    assert role_table.check_range(root, "HEAD~1..HEAD") == []
    with pytest.raises(GovError):
        role_table.check_range(root, "nonsense..HEAD")


def scripts(folder, lead="--effort \"${EFFORT:-medium}\"", cto="--effort high", audit="--effort high", extra=""):
    folder.mkdir(parents=True, exist_ok=True)
    (folder / "start_lead.sh").write_text(f"EFFORT=${{EFFORT:-medium}}\nclaude -p --model claude-sonnet-5-5 {lead} --x\n")
    (folder / "start_cto.sh").write_text(f"model=claude-opus-5-5\nclaude --model $model {cto} \\\n  --y\n{extra}")
    (folder / "start_audit.sh").write_text(f"claude -p --model claude-opus-5-5 {audit}\n")
    return folder


def test_scripts_that_agree_with_the_table_pass_and_are_printed(tmp_path):
    root = planted(tmp_path / "root", (REPO / role_table.REL).read_text())
    lines, ok = role_table.check_scripts(scripts(tmp_path / "s"), root)
    assert ok and len(lines) == 3 and "start_cto.sh: --model claude-opus-5-5 --effort high" in lines[1]


@pytest.mark.parametrize("change, word", (
    (dict(cto="--effort medium"), "start_cto.sh"),
    (dict(lead="--effort high"), "start_lead.sh"),
    (dict(lead="--effort \"${EFFORT:-high}\""), "start_lead.sh"),
    (dict(audit=""), "names no --effort"),
    (dict(cto="--effort high", extra="read_fable_substitution\n"), "substitution"),
))
def test_scripts_that_disagree_are_reported(tmp_path, change, word):
    root = planted(tmp_path / "root", (REPO / role_table.REL).read_text())
    lines, ok = role_table.check_scripts(scripts(tmp_path / "s", **change), root)
    assert not ok and any(word in line for line in lines[3:]), lines


def test_a_missing_script_is_reported_not_skipped(tmp_path):
    root = planted(tmp_path / "root", (REPO / role_table.REL).read_text())
    folder = scripts(tmp_path / "s")
    (folder / "start_audit.sh").unlink()
    lines, ok = role_table.check_scripts(folder, root)
    assert not ok and any("start_audit.sh" in line and "cannot be read" in line for line in lines[3:])


def test_the_module_runs_as_a_command(tmp_path):
    root = planted(tmp_path / "root", (REPO / role_table.REL).read_text())
    run = lambda *a: subprocess.run([sys.executable, "-m", "gov.launch.role_table", *a], cwd=root,  # noqa: E731
                                    capture_output=True, text=True, env={"PYTHONPATH": str(REPO / "src"), "PATH": "/usr/bin:/bin"})
    assert run("--roles").returncode == 0
    assert run("--scripts", str(scripts(tmp_path / "s"))).returncode == 0
    assert run("--scripts", str(scripts(tmp_path / "bad", cto="--effort medium"))).returncode == 1


def test_criticality_load_refuses_the_retired_opus_key(tmp_path):
    (tmp_path / "governance/project").mkdir(parents=True)
    path = tmp_path / criticality.REL
    path.write_text("version: 1\ndefault: C2\nopus: claude-opus-5-5\nrules: []\n")
    with pytest.raises(GovError) as raised:
        criticality.load(tmp_path)
    assert "opus" in raised.value.message
    path.write_text("version: 1\ndefault: C2\nrules: []\n")
    assert criticality.load(tmp_path)["default"] == "C2"
    assert not hasattr(criticality, "opus_model")
