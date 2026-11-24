"""Builder tests for W2-184's R1-R3 (DEC-1180 (4); the interface's section 10).

Regression evidence only (DEC-136): the lead's three options refused by the CLI (exit 2) and by the launcher; the
launch record written to a hidden temporary file and linked to its name; no probe record is read (MR-2).
"""
from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO / "src"))

from gov.cli.errors import GovError  # noqa: E402
from gov.launch import command, launcher, record  # noqa: E402

SID = "5b8f0c1e-2d3a-4f5b-9c6d-7e8f9a0b1c2d"
TK = "DAEO-rr01"


class Killed(BaseException):
    """A stand-in for the process being killed inside the write (not an OSError: nothing cleans up)."""


# R1: a lead takes none of --reason, --trial and --owner-named


def _args(role: str, **options) -> argparse.Namespace:
    base = {"worker_role": role, "ticket": TK, "plan": False, "passthrough": None, "gate_override": None,
            "gpu_need_mib": None, "reason": None, "trial": None, "owner_named": None}
    base.update(options)
    return argparse.Namespace(**base)


@pytest.mark.parametrize("role", ["orchestrator", "lead"])
@pytest.mark.parametrize("options, named", [
    ({"reason": "x"}, ["--reason"]),
    ({"reason": ""}, ["--reason"]),
    ({"trial": "t1"}, ["--trial"]),
    ({"owner_named": "DEC-1"}, ["--owner-named"]),
    ({"reason": "x", "trial": "t1", "owner_named": "DEC-1"}, ["--reason", "--trial", "--owner-named"]),
])
def test_the_cli_refuses_a_lead_given_an_option_with_exit_2_before_the_launcher(monkeypatch, capsys, role, options,
                                                                                 named):
    monkeypatch.setattr(launcher, "launch", lambda *a, **k: pytest.fail("the launcher was called"))
    assert command.run(Path("/nowhere"), _args(role, **options), {}) == 2
    err = capsys.readouterr().err
    assert "a lead" in err and all(option in err for option in named)
    assert all(option in err for option in ("--reason", "--trial", "--owner-named"))


def test_the_cli_passes_a_lead_launch_without_the_options_to_the_launcher(monkeypatch):
    seen = {}
    monkeypatch.setattr(launcher, "launch", lambda *a, **k: seen.update(args=a, kwargs=k) or 0)
    assert command.run(Path("/nowhere"), _args("lead", passthrough=["--reason", "x"]), {}) == 0
    assert seen["args"][3] == ["--reason", "x"] and seen["kwargs"] == {"gate_override": None, "gpu_need_mib": None}


def test_the_cli_passes_a_worker_s_options_to_the_launcher(monkeypatch):
    seen = {}
    monkeypatch.setattr(launcher, "launch", lambda *a, **k: seen.update(kwargs=k) or 0)
    assert command.run(Path("/nowhere"), _args("engineer", reason="x", trial="t1"), {}) == 0
    assert seen["kwargs"]["reason"] == "x" and seen["kwargs"]["trial"] == "t1" and "owner_named" not in seen["kwargs"]


@pytest.mark.parametrize("role", ["orchestrator", "lead"])
@pytest.mark.parametrize("option", ["reason", "trial", "owner_named"])
def test_the_launcher_refuses_a_lead_given_an_option_before_anything(monkeypatch, tmp_path, role, option):
    monkeypatch.setattr(launcher, "_admit_lead", lambda *a: pytest.fail("the lead was admitted"))
    with pytest.raises(GovError) as raised:
        launcher.launch(tmp_path, role, TK, [], **{option: "DEC-1" if option == "owner_named" else "x"})
    assert raised.value.code == "LAUNCH_REFUSED" and "a lead" in raised.value.message
    assert "--" + option.replace("_", "-") in raised.value.message


# R2: the record written atomically


def _leftovers(folder: Path) -> list[str]:
    return sorted(name for name in os.listdir(folder))


def test_the_record_is_whole_under_its_name_and_no_temporary_file_is_left(tmp_path):
    path = record.write(tmp_path, {"session_id": SID, "role": "engineer"})
    assert path == tmp_path / f"{SID}.json"
    assert json.loads(path.read_text(encoding="utf-8")) == {"session_id": SID, "role": "engineer"}
    assert _leftovers(tmp_path) == [f"{SID}.json"]


@pytest.mark.parametrize("where", ["write", "fsync"])
def test_a_write_killed_midway_leaves_no_final_name_and_only_a_hidden_tmp(monkeypatch, tmp_path, where):
    def kill(*a, **k):
        raise Killed

    monkeypatch.setattr(record.os, where, kill)
    with pytest.raises(Killed):
        record.write(tmp_path, {"session_id": SID})
    monkeypatch.undo()
    names = _leftovers(tmp_path)
    assert f"{SID}.json" not in names
    assert all(name.startswith(f".{SID}.") and name.endswith(".tmp") for name in names)


@pytest.mark.parametrize("where", ["write", "fsync", "link"])
def test_an_oserror_refuses_and_leaves_neither_file(monkeypatch, tmp_path, where):
    def fail(*a, **k):
        raise OSError(5, "I/O error")

    monkeypatch.setattr(record.os, where, fail)
    with pytest.raises(GovError) as raised:
        record.write(tmp_path, {"session_id": SID})
    monkeypatch.undo()
    assert "cannot be written" in raised.value.message
    assert _leftovers(tmp_path) == []


def test_an_existing_record_refuses_as_already_there_and_the_tmp_is_removed(tmp_path):
    (tmp_path / f"{SID}.json").write_text('{"whole": true}\n', encoding="utf-8")
    with pytest.raises(GovError) as raised:
        record.write(tmp_path, {"session_id": SID, "role": "research"})
    assert "already there" in raised.value.message
    assert _leftovers(tmp_path) == [f"{SID}.json"]
    assert json.loads((tmp_path / f"{SID}.json").read_text(encoding="utf-8")) == {"whole": True}


def test_a_leftover_tmp_is_not_read_as_a_record(monkeypatch, tmp_path):
    monkeypatch.setattr(record, "folder", lambda root: tmp_path)
    (tmp_path / f".{SID}.abc.tmp").write_text("{not json", encoding="utf-8")
    assert launcher._launch_records(tmp_path) == []


# R3: no root's copy of a probe record is read

# Rewrite-Reason: DEC-1246 (3)(b): MR-2: the promotion read every root's copy of the ticket's probe records; it is
# retired with criticality's `opus` key, and the launcher keeps no function that reads one.
def test_the_launcher_reads_no_probe_record():
    for name in ("_promotion", "_probe_roots", "_probe_files", "_read_probe", "_probe_record", "_fails_open"):
        assert not hasattr(launcher, name), name
    assert not hasattr(launcher, "PROBES_REL")
