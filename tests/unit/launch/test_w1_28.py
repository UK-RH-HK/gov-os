"""Builder tests for the launcher changes of W1-28 (DEC-386).

Regression evidence only (DEC-136). No CLI is started: ``subprocess.Popen`` is
replaced, and the project is a temporary directory. They cover an exit the
acceptance tests reach only through a real process: a CLI that cannot be
started. The interrupt is in ``test_w1_32.py`` (DEC-392).
"""
from __future__ import annotations

import os
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO / "src"))

from gov.cli.errors import GovError  # noqa: E402
from gov.launch import launcher  # noqa: E402


@pytest.fixture
def session(tmp_path, monkeypatch):
    """``session(end)`` launches with ``end(folder)`` in place of the CLI; the folders made are in ``session.made``."""
    home, temp, project = tmp_path / "home", tmp_path / "temp", tmp_path / "project"
    for folder in (home / ".local" / "bin", temp, project):
        folder.mkdir(parents=True)
    (home / launcher.CLI_REL).write_text("", encoding="utf-8")
    monkeypatch.setenv("HOME", str(home))
    monkeypatch.setattr(launcher.tempfile, "tempdir", str(temp))
    monkeypatch.setattr(launcher, "_check_ticket", lambda *args: None)
    monkeypatch.setattr(launcher, "_check_repository_settings", lambda *args: None)

    def _session(end):
        class Session:  # in place of ``subprocess.Popen`` (W1-32): ``end`` runs where the session is started
            def __init__(self, argv, cwd, env):
                _session.made.append(Path(env["TMPDIR"]))
                assert _session.made[-1].is_dir()
                self.returncode = end(_session.made[-1]).returncode

            def wait(self):
                return self.returncode

            def poll(self):
                return self.returncode

        monkeypatch.setattr(launcher.subprocess, "Popen", Session)
        return launcher.launch(project, "engineer", "TST-a001", [])

    _session.made, _session.temp = [], temp
    return _session


def test_the_product_spec_settings_are_strict_with_no_host_and_the_workers_deny_rules(tmp_path):
    built = launcher.build_settings(tmp_path, "product-spec", "TST-a001")
    assert launcher.sandbox_faults(built) == [] and built["sandbox"]["network"]["allowedDomains"] == []
    assert built["permissions"]["deny"] == launcher.build_settings(tmp_path, "engineer", "TST-a001")["permissions"]["deny"]


@pytest.mark.parametrize("ticket_role, refused", (("product-spec", False), ("engineer", True), (None, True)))
def test_product_spec_is_held_to_a_ticket_of_its_own(monkeypatch, tmp_path, ticket_role, refused):
    monkeypatch.setattr(launcher, "_load_ticket", lambda root, tid: {"status": "in_progress", "role": ticket_role})
    if refused:
        with pytest.raises(GovError):
            launcher._check_ticket(tmp_path, "product-spec", "TST-a001")
    else:
        launcher._check_ticket(tmp_path, "product-spec", "TST-a001")


def _not_started(folder):
    raise PermissionError(13, "Permission denied")


def test_the_folder_is_removed_when_the_session_cannot_be_started(session):
    """The interrupt, which W1-28 let through as ``KeyboardInterrupt``, is in ``test_w1_32.py`` (DEC-392)."""
    with pytest.raises(GovError):
        session(_not_started)
    assert len(session.made) == 1 and os.listdir(session.temp) == []


def test_a_link_goes_and_its_target_stays_and_the_exit_code_is_the_sessions(session, tmp_path):
    kept = tmp_path / "kept"
    kept.mkdir()
    (kept / "file.txt").write_text("kept\n", encoding="utf-8")

    def end(folder):
        (folder / "link").symlink_to(kept)
        return type("Done", (), {"returncode": 7})()

    assert session(end) == 7
    assert os.listdir(session.temp) == [] and (kept / "file.txt").read_text(encoding="utf-8") == "kept\n"
