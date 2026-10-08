"""Builder tests for ``gov ci checks`` (W1-40): regression evidence only. The hook cases are the acceptance suite's."""
from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

import pytest
import yaml

REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO / "src"))

from gov.ci import command  # noqa: E402
from gov.cli.checks import CHECKS_DIR  # noqa: E402
from gov.cli.errors import GovError  # noqa: E402


def _declare(root, tier, command_line, severity="hard-block"):
    path = root / CHECKS_DIR / f"check-{tier.lower()}.yaml"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(yaml.safe_dump({"id": f"check-{tier.lower()}", "family": "schema/invariants", "tier": tier,
                                    "severity": severity, "command": command_line}), encoding="utf-8")


def test_only_the_tiers_named_run(tmp_path):
    _declare(tmp_path, "G1", "true")
    _declare(tmp_path, "G2", "true")
    _declare(tmp_path, "G3", "touch ran-g3; false")
    assert command._checks(tmp_path, ["G1", "G2"])["checks"] == {"check-g1": "GREEN", "check-g2": "GREEN"}
    assert not (tmp_path / "ran-g3").exists()


def test_a_red_hard_block_check_refuses_with_exit_code_3(tmp_path):
    _declare(tmp_path, "G1", "true")
    _declare(tmp_path, "G2", "false")
    with pytest.raises(GovError) as refused:
        command._checks(tmp_path, ["G1", "G2"])
    assert (refused.value.code, refused.value.exit_code) == ("CHECK_FAILED", 3)


def test_a_named_tier_without_a_check_refuses_before_any_check_runs(tmp_path):
    _declare(tmp_path, "G1", "touch ran-g1")
    with pytest.raises(GovError) as refused:
        command._checks(tmp_path, ["G1", "G2"])
    assert refused.value.code == command.NOT_MEASURED and refused.value.details == {"tiers": ["G2"]}
    assert not (tmp_path / "ran-g1").exists()


@pytest.mark.parametrize("tiers", [["G1", "G22"], ["G1", "tier2"], ["g1"], []])
def test_a_name_that_is_no_tier_refuses(tmp_path, tiers):
    _declare(tmp_path, "G1", "true")
    with pytest.raises(GovError) as refused:
        command._checks(tmp_path, tiers)
    assert refused.value.code == "CI_TIER_UNKNOWN"


@pytest.fixture()
def openspec(tmp_path, monkeypatch):
    """A stand-in ``openspec`` on PATH that validates anything: with it the openspec check is measured."""
    folder = tmp_path / "stand-in-bin"
    folder.mkdir()
    (folder / "openspec").write_text("#!/bin/sh\nexit 0\n", encoding="utf-8")
    (folder / "openspec").chmod(0o755)
    monkeypatch.setenv("PATH", f"{folder}{os.pathsep}{os.environ['PATH']}")


def test_the_job_gate_names_a_check_whose_tool_is_absent_as_unmeasured_and_refuses(tmp_path, monkeypatch):
    _declare(tmp_path, "G1", "true")
    _declare(tmp_path, "G2", """echo '{"findings": [{"code": "RULESYNC_ABSENT", "message": "m"}]}'; exit 1""")
    monkeypatch.setenv("PATH", "/usr/bin:/bin")  # no openspec: the runner gives OPENSPEC_ABSENT, YELLOW
    with pytest.raises(GovError) as refused:
        command._checks(tmp_path, list(command.JOB_TIERS), job=True)
    assert refused.value.code == command.NOT_MEASURED and refused.value.exit_code != 0
    message = refused.value.message
    assert message.startswith("unmeasured: check-g2 (rulesync is not on the runner), openspec-validate (openspec ")
    assert "hard-block checks failed: check-g2" in message
    assert refused.value.details["checks"]["openspec-validate"] == "YELLOW"


def test_the_job_gate_refuses_a_declared_check_of_an_unknown_family_and_the_hook_gate_does_not(tmp_path, openspec):
    _declare(tmp_path, "G1", "true")
    _declare(tmp_path, "G2", "true")
    path = tmp_path / CHECKS_DIR / "check-g2.yaml"
    path.write_text(path.read_text(encoding="utf-8").replace("schema/invariants", "a family nobody knows"),
                    encoding="utf-8")
    assert command._checks(tmp_path, ["G1", "G2"])["checks"] == {"check-g1": "GREEN", "check-g2": "GREEN"}
    with pytest.raises(GovError) as refused:
        command._checks(tmp_path, list(command.JOB_TIERS), job=True)
    assert (refused.value.code, refused.value.exit_code) == ("CHECK_FAILED", 3)
    assert "a family nobody knows" in refused.value.message


def test_the_job_gate_runs_the_tier_less_checks_and_no_check_above_g2(tmp_path, openspec):
    _declare(tmp_path, "G0", "touch ran-g0")
    _declare(tmp_path, "G1", "true")
    _declare(tmp_path, "G2", "true")
    _declare(tmp_path, "G3", "touch ran-g3; false")
    statuses = command._checks(tmp_path, list(command.JOB_TIERS), job=True)["checks"]
    assert {"check-g0", "check-g1", "check-g2", "openspec-validate", "skill-version", "readiness"} <= set(statuses)
    assert "check-g3" not in statuses and statuses["readiness"] == "GREEN"
    assert (tmp_path / "ran-g0").exists() and not (tmp_path / "ran-g3").exists()


def test_the_job_gate_refuses_a_red_readiness_check_and_the_hook_gate_does_not_run_it(tmp_path, openspec):
    _declare(tmp_path, "G1", "true")
    _declare(tmp_path, "G2", "true")
    proposal = tmp_path / "openspec" / "changes" / "unjudged" / "proposal.md"
    proposal.parent.mkdir(parents=True)
    proposal.write_text("# A change with no specification record\n", encoding="utf-8")
    assert set(command._checks(tmp_path, ["G1", "G2"])["checks"]) == {"check-g1", "check-g2"}
    with pytest.raises(GovError) as refused:
        command._checks(tmp_path, list(command.JOB_TIERS), job=True)
    assert (refused.value.code, refused.value.exit_code) == ("CHECK_FAILED", 3)
    assert refused.value.details["checks"]["readiness"] == "RED"


def test_the_job_gate_refuses_where_no_g2_check_is_declared(tmp_path):
    _declare(tmp_path, "G1", "true")
    with pytest.raises(GovError) as refused:
        command._checks(tmp_path, list(command.JOB_TIERS), job=True)
    assert refused.value.code == command.NOT_MEASURED and refused.value.details == {"tiers": ["G2"]}


def _git(cwd, *args):
    return subprocess.run(["git", *args], cwd=str(cwd), capture_output=True, text=True, check=True).stdout.strip()


@pytest.fixture()
def pushed_to(tmp_path, monkeypatch):
    """A repository built from scratch with one commit, and a bare repository beside it as ``origin``."""
    for key, value in {"GIT_CONFIG_GLOBAL": os.devnull, "GIT_CONFIG_NOSYSTEM": "1", "GIT_AUTHOR_NAME": "t",
                       "GIT_AUTHOR_EMAIL": "t@example.invalid", "GIT_COMMITTER_NAME": "t",
                       "GIT_COMMITTER_EMAIL": "t@example.invalid"}.items():
        monkeypatch.setenv(key, value)
    root, remote = tmp_path / "project", tmp_path / "origin.git"
    root.mkdir()
    _git(tmp_path, "init", "-q", "--bare", str(remote))
    _git(root, "init", "-q", "-b", "main")
    (root / "README.md").write_text("# A project\n", encoding="utf-8")
    _git(root, "add", "README.md")
    _git(root, "commit", "-q", "-m", "initial")
    _git(root, "remote", "add", "origin", str(remote))
    return root, remote


def test_the_push_gate_leaves_the_record_on_the_remote_and_the_record_gate_accepts_it(pushed_to):
    root, remote = pushed_to
    _declare(root, "G3", "true")
    head = _git(root, "rev-parse", "HEAD")
    assert command._push(root, ["origin"]) == {"commit": head, "result": "passed", "checks": {"check-g3": "GREEN"}}
    assert json.loads(_git(remote, "notes", "--ref", command.EVIDENCE_REF, "show", head))["commit"] == head
    assert command._record(root)["result"] == "passed"
    assert _git(root, "status", "--porcelain", "--untracked-files=no") == ""


def test_a_failing_g3_check_refuses_and_its_record_is_neither_pushed_nor_accepted(pushed_to):
    root, remote = pushed_to
    _declare(root, "G3", "false")
    with pytest.raises(GovError) as refused:
        command._push(root, ["origin"])
    assert (refused.value.code, refused.value.exit_code) == ("CHECK_FAILED", 3)
    assert _git(remote, "for-each-ref", "refs/notes/") == ""
    with pytest.raises(GovError) as refused:
        command._record(root)
    assert refused.value.code == "EVIDENCE_REFUSED" and "failed" in refused.value.message


def test_no_g3_check_is_recorded_in_those_words_and_the_record_gate_reports_them(pushed_to):
    root, _ = pushed_to
    assert command._push(root, ["origin"])["result"] == "no G3 check declared"
    assert command._record(root)["result"] == "no G3 check declared"  # DEC-497: printed, not refused, no "passed"


def test_the_record_gate_refuses_no_record_and_the_record_of_another_commit(pushed_to):
    root, _ = pushed_to
    with pytest.raises(GovError) as refused:
        command._record(root)
    assert refused.value.code == command.NOT_MEASURED
    _declare(root, "G3", "true")
    command._push(root, ["origin"])
    first = _git(root, "rev-parse", "HEAD")
    _git(root, "commit", "-q", "--allow-empty", "-m", "second")
    _git(root, "notes", "--ref", command.EVIDENCE_REF, "copy", first, "HEAD")
    with pytest.raises(GovError) as refused:
        command._record(root)
    assert refused.value.code == command.NOT_MEASURED and "another commit" in refused.value.message


def test_no_check_of_the_tiers_is_not_a_pass(tmp_path):
    _declare(tmp_path, "G3", "true")
    with pytest.raises(GovError) as refused:
        command._checks(tmp_path, ["G1", "G2"])
    assert refused.value.code == command.NOT_MEASURED
