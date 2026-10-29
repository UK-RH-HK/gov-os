"""Builder tests for one option reader in the read rule (W2-50, DEC-778).

The read rule reads ``mv`` and ``cp -l`` with the reader the write rule uses
for ``cp``, ``install`` and ``mv`` (DEC-765): an option's value is a value,
and nothing after ``--`` is an option.

Regression evidence only (DEC-136).  The stand-in for the protected pair is
a temporary project's own settings file; no other file of the pair is made
or named.
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO / "src"))
from gov.guard.heldout import SETTINGS_REL  # noqa: E402
from gov.guard.protected import SECOND_NAME_REFUSAL, _second_names, read_refusal  # noqa: E402


@pytest.fixture()
def box(tmp_path, monkeypatch):
    project, temp = tmp_path / "project", tmp_path / "temp"
    (project / SETTINGS_REL).parent.mkdir(parents=True)
    (project / SETTINGS_REL).write_text("{}\n", encoding="utf-8")
    (project / "src" / "d").mkdir(parents=True)
    (project / "src" / "data.json").write_text("{}\n", encoding="utf-8")
    temp.mkdir()
    monkeypatch.setenv("HOME", str(tmp_path / "home"))
    return project, temp


@pytest.mark.parametrize("name, args, second", (
    ("mv", ["-S.t", "F", "N"], ["F"]), ("mv", ["-St", "F", "N"], ["F"]), ("mv", ["-S", "-t", "F", "N"], ["F"]),
    ("mv", ["--suffix", "-t", "F", "N"], ["F"]), ("mv", ["F", "N", "-S.t"], ["F", "N"]),
    ("mv", ["-t", "T", "-S.t", "F"], ["F"]), ("mv", ["--", "F", "-t"], ["F"]), ("mv", ["F", "--", "-t"], ["F"]),
    ("mv", ["F", "N", "--"], ["F"]), ("mv", ["-t", "T", "--", "F"], ["F"]), ("mv", ["-T", "F", "N"], ["F"]),
    ("cp", ["-lS.t", "F", "N"], ["F"]), ("cp", ["-l", "-S", "-t", "F", "N"], ["F"]),
    ("cp", ["--link", "--sparse", "always", "F", "N"], ["F"]), ("cp", ["-l", "--", "F", "-t"], ["F"]),
    ("cp", ["-lt", "T", "F"], ["F"]), ("cp", ["-rlS.t", "D", "DD"], ["D"]),
    ("cp", ["-S.l", "F", "N"], []), ("cp", ["--sparse=auto", "F", "N"], []), ("cp", ["-a", "F", "N"], []),
    ("mv", ["--no-such", "F", "N"], ["--no-such", "F", "N"]), ("cp", ["-q", "F", "N"], ["-q", "F", "N"])))
def test_the_second_names_are_read_as_the_write_rule_reads_the_call(name, args, second):
    """DEC-778: a t inside an option's value is no -t, an l inside one no -l, and a word after -- an operand;
    a call whose options cannot be read gives every word."""
    assert _second_names(name, args) == second


@pytest.mark.parametrize("command, cwd", (
    ("mv -S.t {F} {N}", "project"), ("mv -S -t {F} {N}", "project"), ("mv {F} {N} -S.t", "project"),
    ("mv -t {T} -S.t {F}", "project"), ("mv -- {F} -t", "temp"), ("mv -S.t {D} {N}", "project"),
    ("mv -S.t .claude/settings.json {N}", "project"), ("cp -lS.t {F} {N}", "project"),
    ("cp -l {F} -- -t", "temp"), ("cp -rlS.t {D} {N}", "project"), ("cp -l --reflink=auto {F} -- -t", "temp")))
@pytest.mark.parametrize("role", ("orchestrator", "engineer"))
def test_a_second_name_however_the_options_are_written_is_refused(box, command, cwd, role):
    """W2-58: refused for its own reason now, the write side (DEC-821 item 4)."""
    project, temp = box
    paths = {"F": project / SETTINGS_REL, "D": (project / SETTINGS_REL).parent, "N": temp / "new",
             "T": temp}
    folder = project if cwd == "project" else temp
    assert read_refusal("Bash", {"command": command.format(**paths)}, str(project),
                        str(folder)) == SECOND_NAME_REFUSAL


@pytest.mark.parametrize("command, cwd", (
    ("mv -S.t {U} {N}", "project"), ("mv -S -t {U} {N}", "project"), ("mv -- {U} -t", "d"),
    ("cp -lS.t {U} {N}", "project"), ("cp -l -- {U} -t", "d"), ("cp -S.l {U} {N}", "project"),
    ("mv {N} {F}", "project")))
def test_the_same_forms_of_an_unprotected_file_are_no_read(box, command, cwd):
    """And a move onto the file, not a second name for it, stays with the allow-list."""
    project, temp = box
    paths = {"U": project / "src" / "data.json", "N": project / "src" / "d" / "new.json",
             "F": project / SETTINGS_REL}
    folder = project / "src" / "d" if cwd == "d" else project
    assert read_refusal("Bash", {"command": command.format(**paths)}, str(project), str(folder)) == ""
