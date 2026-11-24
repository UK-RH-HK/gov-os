"""Fix F1 (c) (owner W2-201, the doctor's part kept with W2-22's drift cases): ``gov doctor`` reports a repository whose
``.claude/settings.json`` lacks ``"disableClaudeAiConnectors": true`` as a drift line (the key named in the output) and
still exits 0 (a drift line, not a failure). A repository whose settings carry the key has no such line.

Each case builds a small committed repository (as ``support.doctor`` does), writes the settings file, and runs ``gov
doctor`` with a stand-in ``claude`` first on the ``PATH``. Public interface: the command's output and exit code.
"""

from __future__ import annotations

import json
import os

import pytest

import w2_22_support as support
from w1_27_support import git, run_gov_with_code, write_path_map, minimal_valid_path_map

KEY = "disableClaudeAiConnectors"


def _doctor(tmp_path, sandbox, monkeypatch, settings, *args):
    project = tmp_path / "repo"
    project.mkdir()
    git(project, "init", "-q", "-b", "main")
    write_path_map(project, minimal_valid_path_map())
    if settings is not None:
        path = project / ".claude" / "settings.json"
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(settings, indent=2) + "\n", encoding="utf-8")
    support.write_cli(sandbox, "2.1.329")
    monkeypatch.setenv("PATH", f"{sandbox.bin}{os.pathsep}{os.environ.get('PATH', '/usr/bin:/bin')}")
    return run_gov_with_code(support.REPO_ROOT, project, sandbox, "doctor", *args)


LACKING = {"permissions": {"deny": ["Bash(git push *)"]}}


def test_settings_without_the_key_are_a_drift_line_and_doctor_exits_0(sandbox, tmp_path, monkeypatch):
    """Red on the base: doctor says nothing of the key."""
    run = _doctor(tmp_path, sandbox, monkeypatch, LACKING, "--json")
    assert run.returncode == 0, f"a missing key is drift, not a failure: exit {run.returncode}\n{run.describe()}"
    assert KEY in run.stdout, f"doctor's JSON does not name {KEY}\n{run.describe()}"


def test_the_drift_line_is_in_the_plain_output_too(sandbox, tmp_path, monkeypatch):
    run = _doctor(tmp_path, sandbox, monkeypatch, LACKING)
    assert run.returncode == 0, f"exit {run.returncode}\n{run.describe()}"
    assert KEY in run.stdout + run.stderr, f"the plain output does not name {KEY}\n{run.describe()}"


def test_settings_with_the_key_have_no_drift_line(sandbox, tmp_path, monkeypatch):
    """Guard (green on the base): nothing to report when the key is there."""
    run = _doctor(tmp_path, sandbox, monkeypatch, {**LACKING, KEY: True}, "--json")
    assert run.returncode == 0, f"exit {run.returncode}\n{run.describe()}"
    assert KEY not in run.stdout, f"doctor names {KEY} though the settings carry it\n{run.describe()}"
