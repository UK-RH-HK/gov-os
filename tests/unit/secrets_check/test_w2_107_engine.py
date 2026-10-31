"""Builder tests for W2-107, round 2: the engine a remembered verdict is judged under (DEC-966 item 4, DEC-967).

Regression evidence only (DEC-136): gitleaks' version and the filter's reading form are in the fingerprint, one engine
serves a judgement's lookup and write, and a record that cannot be written still answers its own engine's verdicts.
Each test names its own record in its tmp_path by GOV_SECRETS_CACHE, so the machine's record is never touched; the
stand-ins first on PATH hand every scan to the real gitleaks.
"""
from __future__ import annotations

import hashlib
import json
import os
import shutil
import sqlite3
import subprocess
import sys
from pathlib import Path

import pytest

from gov import secrets
from gov.secrets import cache

REPO = Path(__file__).resolve().parents[3]
SRC = Path(secrets.__file__).resolve().parents[2]  # the src/ whose gov is under test
MAP = "namespaces:\n  everything: {paths: ['**'], memory_class: governance}\n"
REAL = shutil.which("gitleaks")

pytestmark = pytest.mark.skipif(REAL is None, reason="gitleaks is not on PATH")


def _write(root: Path, rel: str, data: str) -> str:
    path = root / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(data)
    return rel


def _script(path: Path, body: str) -> Path:
    path.write_text(f"#!/bin/sh\n{body}")
    path.chmod(0o755)
    return path


def _release(path: Path, version: str) -> Path:
    """A gitleaks release that says ``version`` and hands every other run to the real one, logging each run."""
    return _script(path, f"echo \"$1\" >> '{path.parent / 'runs'}'\n"
                         f"if [ \"$1\" = version ]; then echo '{version}'; exit 0; fi\nexec '{REAL}' \"$@\"\n")


def _asked(folder: Path) -> list[str]:
    path = folder / "runs"
    return path.read_text().splitlines() if path.exists() else []


@pytest.fixture()
def bench(tmp_path, monkeypatch):
    project = tmp_path / "project"
    _write(project, "governance/project/path-map.yaml", MAP)
    _write(project, ".gitleaks.toml", (REPO / "template/.gitleaks.toml").read_text(encoding="utf-8"))
    tools = tmp_path / "bin"
    tools.mkdir()
    _release(tools / "gitleaks", "8.0.1")
    monkeypatch.setenv("PATH", f"{tools}{os.pathsep}{os.environ['PATH']}")
    record = tmp_path / "home" / "cache" / "secrets-scan.sqlite"
    monkeypatch.setenv("GOV_SECRETS_CACHE", str(record))
    monkeypatch.delenv("GOV_SECRETS_FULL_SCAN", raising=False)
    monkeypatch.setattr(cache, "_binaries", {})  # each test starts as a fresh process would
    monkeypatch.setattr(cache, "_ready", set())
    return project, tools, record


def _judged(project: Path, rels: list[str]) -> dict:
    """What one judgement of ``rels`` did in this process: how many contents were scanned and remembered."""
    before = secrets.scan_counts()["content"]
    assert secrets.indexable(project, rels) == rels
    after = secrets.scan_counts()["content"]
    return {what: after[what] - before[what] for what in after}


def _rows(record: Path) -> int:
    if not record.exists():
        return 0
    with sqlite3.connect(record) as connection:
        return connection.execute("SELECT count(*) FROM verdict").fetchone()[0]


def _process(project: Path, rels: list[str]) -> dict:
    """One judgement of ``rels`` in a process of its own, as a rebuild makes it."""
    code = ("import json, sys; from gov import secrets; "
            "assert secrets.indexable(sys.argv[1], sys.argv[2:]) == sys.argv[2:]; "
            "print(json.dumps(secrets.scan_counts()['content']))")
    env = os.environ | {"PYTHONPATH": str(SRC)}
    done = subprocess.run([sys.executable, "-c", code, str(project), *rels], capture_output=True, text=True,
                          env=env, check=True, timeout=300)
    return json.loads(done.stdout)


def test_a_release_changed_behind_a_shim_of_the_same_bytes_forgets_every_verdict(bench):
    project, tools, record = bench
    _release(tools / "r1", "8.0.1")
    _release(tools / "r2", "8.0.2")
    setting = tools / "release"
    setting.write_text(str(tools / "r1"))
    shim = _script(tools / "gitleaks", f"exec \"$(cat '{setting}')\" \"$@\"\n")
    seen = hashlib.sha256(shim.read_bytes()).hexdigest(), shim.stat().st_ino
    rels = [_write(project, "notes/clean.md", "Ordinary text.\n")]
    assert _process(project, rels) == {"scanned": 1, "remembered": 0}
    assert _process(project, rels) == {"scanned": 0, "remembered": 1}
    setting.write_text(str(tools / "r2"))  # the shim's bytes stay, the release it runs changes
    assert (hashlib.sha256(shim.read_bytes()).hexdigest(), shim.stat().st_ino) == seen
    assert _process(project, rels) == {"scanned": 1, "remembered": 0}
    assert _process(project, rels) == {"scanned": 0, "remembered": 1}
    with sqlite3.connect(record) as connection:
        assert len({row[0] for row in connection.execute("SELECT fingerprint FROM verdict")}) == 1


def test_the_version_is_asked_once_per_binary_and_only_with_a_record(bench, monkeypatch):
    project, tools, record = bench
    rels = [_write(project, f"notes/{number}.md", f"Ordinary text {number}.\n") for number in range(4)]
    for named in ("", None):  # an empty name, and none under pytest: no record, no version asked
        if named is None:
            monkeypatch.delenv("GOV_SECRETS_CACHE")
        else:
            monkeypatch.setenv("GOV_SECRETS_CACHE", named)
        assert _judged(project, rels) == {"scanned": 4, "remembered": 0}
        assert "version" not in _asked(tools)
    monkeypatch.setenv("GOV_SECRETS_CACHE", str(record))
    assert _judged(project, rels) == {"scanned": 4, "remembered": 0}
    assert _judged(project, rels) == {"scanned": 0, "remembered": 4}
    assert [secrets.path_holds_secret(project, rel) for rel in rels] == [False] * 4
    assert _asked(tools).count("version") == 1


@pytest.mark.parametrize("answer", ["fails", "empty", "silent"])
def test_a_version_that_cannot_be_read_means_no_record(bench, monkeypatch, answer):
    project, tools, record = bench
    monkeypatch.setattr(cache, "_VERSION_S", 0.5)
    said = {"fails": "echo 8.0.1; exit 1", "empty": "echo '  '; exit 0", "silent": "exec sleep 5"}[answer]
    _script(tools / "gitleaks", f"if [ \"$1\" = version ]; then {said}; fi\nexec '{REAL}' \"$@\"\n")
    rels = [_write(project, "notes/clean.md", "Ordinary text.\n")]
    for _ in range(2):
        assert _judged(project, rels) == {"scanned": 1, "remembered": 0}
    assert _rows(record) == 0


def test_the_reading_form_raised_forgets_every_verdict(bench, monkeypatch):
    project, tools, record = bench
    rels = [_write(project, "notes/clean.md", "Ordinary text.\n")]
    assert _judged(project, rels) == {"scanned": 1, "remembered": 0}
    assert _judged(project, rels) == {"scanned": 0, "remembered": 1}
    monkeypatch.setattr(secrets, "_FORM", secrets._FORM + 1)
    assert _judged(project, rels) == {"scanned": 1, "remembered": 0}
    assert _judged(project, rels) == {"scanned": 0, "remembered": 1}


def test_a_gitleaks_replaced_during_its_scan_is_credited_with_nothing(bench):
    project, tools, record = bench
    _release(tools / "next", "8.0.2")
    mark, self = tools / "replaced", tools / "gitleaks"
    _script(self, f"if [ \"$1\" = version ]; then echo 8.0.1; exit 0; fi\n"
                  f"if [ ! -e '{mark}' ]; then : > '{mark}'; mv '{tools / 'next'}' '{self}'; fi\n"
                  f"exec '{REAL}' \"$@\"\n")
    rels = [_write(project, "notes/clean.md", "Ordinary text.\n")]
    assert _judged(project, rels) == {"scanned": 1, "remembered": 0}
    assert mark.exists() and _rows(record) == 0  # judged by the old gitleaks, the new one is credited with nothing
    assert _judged(project, rels) == {"scanned": 1, "remembered": 0}
    assert _rows(record) == 1
    assert _judged(project, rels) == {"scanned": 0, "remembered": 1}


def _snapshot(folder: Path) -> dict:
    return {path.name: path.read_bytes() for path in sorted(folder.iterdir())}


@pytest.mark.parametrize("read_only", ["file", "folder"])
def test_a_record_that_cannot_be_written_answers_its_own_engine_alone(bench, monkeypatch, read_only):
    project, tools, record = bench
    clean = _write(project, "notes/clean.md", "Ordinary text.\n")
    other = _write(project, "notes/other.md", "Other ordinary text.\n")
    assert _judged(project, [clean]) == {"scanned": 1, "remembered": 0}
    assert secrets.path_holds_secret(project, clean) is False
    record.chmod(0o444)
    if read_only == "folder":
        record.parent.chmod(0o555)
    kept = _snapshot(record.parent)
    try:
        monkeypatch.setattr(cache, "_ready", set())  # as a fresh process finds it
        before = secrets.scan_counts()
        assert _judged(project, [clean]) == {"scanned": 0, "remembered": 1}
        assert secrets.path_holds_secret(project, clean) is False
        assert secrets.scan_counts()["path"]["remembered"] == before["path"]["remembered"] + 1
        assert _judged(project, [other]) == {"scanned": 1, "remembered": 0}  # judged, not written
        assert _judged(project, [other]) == {"scanned": 1, "remembered": 0}
        _release(tools / "gitleaks", "8.0.2")  # another engine: never answered from the first one's rows
        for _ in range(2):
            assert _judged(project, [clean]) == {"scanned": 1, "remembered": 0}
        assert {name: data for name, data in _snapshot(record.parent).items() if name in kept} == kept
        assert set(_snapshot(record.parent)) <= set(kept) | {f"{record.name}-shm", f"{record.name}-wal"}
    finally:
        record.parent.chmod(0o700)
        record.chmod(0o644)
    assert _rows(record) == 2  # nothing written, nothing cleared


def test_a_write_lock_that_cannot_be_had_still_answers(bench, monkeypatch):
    project, tools, record = bench
    monkeypatch.setattr(cache, "_WAIT_S", 0.2)
    clean = _write(project, "notes/clean.md", "Ordinary text.\n")
    other = _write(project, "notes/other.md", "Other ordinary text.\n")
    assert _judged(project, [clean]) == {"scanned": 1, "remembered": 0}
    holder = sqlite3.connect(record, isolation_level=None)
    try:
        holder.execute("BEGIN IMMEDIATE")
        monkeypatch.setattr(cache, "_ready", set())
        assert _judged(project, [clean]) == {"scanned": 0, "remembered": 1}
        assert _judged(project, [other]) == {"scanned": 1, "remembered": 0}
    finally:
        holder.close()
    assert _rows(record) == 1
