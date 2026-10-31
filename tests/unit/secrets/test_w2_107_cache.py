"""Builder tests for W2-107: clean gitleaks verdicts remembered by content hash (DEC-966 item 4).

Regression evidence only (DEC-136). A stand-in gitleaks first on PATH counts its runs and hands each to the real one;
every test names its own record in its tmp_path by GOV_SECRETS_CACHE, so the machine's record is never touched. No
secret stands whole in this file: the planted strings are built from parts at run time.
"""
from __future__ import annotations

import os
import shutil
import sqlite3
import subprocess
from pathlib import Path

import pytest

from gov import secrets
from gov.secrets import cache

REPO = Path(__file__).resolve().parents[3]
PLANTED = "_".join(["ARGUS", "TOKEN", "CAN" + "ARY", "4WM8"])
KEYWORD = "".join(("source", "graph"))  # row W2-L423's rule, in parts
MAP = "namespaces:\n  everything: {paths: ['**'], memory_class: governance}\n"
REAL = shutil.which("gitleaks")

pytestmark = pytest.mark.skipif(REAL is None, reason="gitleaks is not on PATH")


def _write(root: Path, rel: str, data) -> str:
    path = root / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(data if isinstance(data, bytes) else data.encode())
    return rel


def _stand_in(folder: Path, note: str = "") -> Path:
    """A gitleaks that counts its runs in ``runs`` beside it and hands each to the real one."""
    folder.mkdir(parents=True, exist_ok=True)
    script = folder / "gitleaks"
    script.write_text(f"#!/bin/sh\n# {note}\necho run >> '{folder / 'runs'}'\nexec '{REAL}' \"$@\"\n")
    script.chmod(0o755)
    return script


def _runs(folder: Path) -> int:
    path = folder / "runs"
    return len(path.read_text().splitlines()) if path.exists() else 0


@pytest.fixture()
def bench(tmp_path, monkeypatch):
    project = tmp_path / "project"
    _write(project, "governance/project/path-map.yaml", MAP)
    _write(project, ".gitleaks.toml", (REPO / "template/.gitleaks.toml").read_text(encoding="utf-8"))
    tools = tmp_path / "bin"
    _stand_in(tools)
    monkeypatch.setenv("PATH", f"{tools}{os.pathsep}{os.environ['PATH']}")
    record = tmp_path / "home" / "cache" / "secrets-scan.sqlite"
    monkeypatch.setenv("GOV_SECRETS_CACHE", str(record))
    monkeypatch.delenv("GOV_SECRETS_FULL_SCAN", raising=False)
    return project, tools, record


def _delta(before: dict, after: dict) -> dict:
    return {kind: {what: after[kind][what] - before[kind][what] for what in after[kind]} for kind in after}


def test_a_second_judgement_of_unchanged_content_and_names_starts_no_gitleaks(bench):
    project, tools, record = bench
    rels = [_write(project, f"notes/{number}.md", f"Ordinary text {number}.\n") for number in range(3)]
    before = secrets.scan_counts()
    assert secrets.indexable(project, rels) == rels
    assert [secrets.path_holds_secret(project, rel) for rel in rels] == [False] * 3
    first, middle = _runs(tools), secrets.scan_counts()
    assert first > 0 and _delta(before, middle) == {"content": {"scanned": 3, "remembered": 0},
                                                    "path": {"scanned": 3, "remembered": 0}}
    assert secrets.indexable(project, rels) == rels
    assert [secrets.path_holds_secret(project, rel) for rel in rels] == [False] * 3
    assert _runs(tools) == first
    assert _delta(middle, secrets.scan_counts()) == {"content": {"scanned": 0, "remembered": 3},
                                                     "path": {"scanned": 0, "remembered": 3}}
    assert oct(record.parent.stat().st_mode & 0o777) == "0o700"
    # a changed file is scanned again; the unchanged ones are not
    (project / rels[0]).write_text("Ordinary text, changed.\n")
    middle = secrets.scan_counts()
    assert secrets.indexable(project, rels) == rels
    assert _delta(middle, secrets.scan_counts())["content"] == {"scanned": 1, "remembered": 2}


def test_the_filter_threads_at_once_lose_no_verdict(bench):
    project, tools, record = bench
    rels = [_write(project, f"many/{number}.md", f"Ordinary text {number}.\n") for number in range(24)]
    assert secrets.indexable(project, rels) == rels
    before = secrets.scan_counts()["content"]
    assert secrets.indexable(project, rels) == rels
    assert secrets.scan_counts()["content"] == {"scanned": before["scanned"], "remembered": before["remembered"] + 24}


def test_a_finding_is_never_remembered_and_the_record_holds_no_text(bench):
    project, tools, record = bench
    clean = _write(project, "notes/clean.md", "Ordinary text.\n")
    planted = _write(project, "notes/planted.md", f"The value is {PLANTED} today.\n")
    named = f"notes/{PLANTED}.md"
    for _ in range(2):
        before = _runs(tools)
        assert secrets.indexable(project, [planted, clean]) == [clean]
        assert secrets.path_holds_secret(project, named) is True
        assert _runs(tools) > before  # the planted content and name are scanned every time
    with sqlite3.connect(record) as connection:
        rows = connection.execute("SELECT digest, kind, verdict FROM verdict").fetchall()
        columns = [row[1] for row in connection.execute("PRAGMA table_info(verdict)")]
    assert columns == ["digest", "kind", "fingerprint", "verdict"]
    assert [(kind, verdict) for _, kind, verdict in rows] == [("content", "clean")]  # the clean file's alone
    stored = b"".join(path.read_bytes() for path in record.parent.iterdir())
    for text in (PLANTED, "clean.md", "planted.md", "Ordinary", "notes"):
        assert text.encode() not in stored


def test_an_exempt_commit_hash_is_judged_afresh_every_time(tmp_path, monkeypatch):
    root = tmp_path / "project"
    root.mkdir()
    shutil.copyfile(REPO / ".gitleaks.toml", root / ".gitleaks.toml")
    git = ["git", "-C", str(root), "-c", "user.name=t", "-c", "user.email=t@example.invalid"]
    subprocess.run(["git", "init", "-q", str(root)], check=True)
    subprocess.run([*git, "commit", "-q", "--allow-empty", "-m", "one"], check=True)
    commit = subprocess.run([*git, "rev-parse", "HEAD"], capture_output=True, text=True, check=True).stdout.strip()
    monkeypatch.setenv("GOV_SECRETS_CACHE", str(tmp_path / "record.sqlite"))
    rules, text = secrets._rules(root), f"The review names {KEYWORD} at {commit} today.\n".encode()
    for _ in range(2):
        before = secrets.scan_counts()["content"]
        assert secrets._holds_secret(rules, text, root, "content") is False
        assert secrets.scan_counts()["content"]["scanned"] == before["scanned"] + 1


def test_another_gitleaks_or_other_rules_forget_every_verdict(bench):
    project, tools, record = bench
    rel = _write(project, "notes/clean.md", "Ordinary text.\n")
    assert secrets.indexable(project, [rel]) == [rel]

    def scanned() -> int:
        before = secrets.scan_counts()["content"]["scanned"]
        assert secrets.indexable(project, [rel]) == [rel]
        return secrets.scan_counts()["content"]["scanned"] - before

    assert scanned() == 0
    _stand_in(tools, note="another build")  # the same place, new bytes
    assert scanned() == 1 and scanned() == 0
    with sqlite3.connect(record) as connection:
        assert len({row[0] for row in connection.execute("SELECT fingerprint FROM verdict")}) == 1
    config = project / ".gitleaks.toml"
    config.write_text(config.read_text(encoding="utf-8") + "\n[[rules]]\nid = 'extra'\nregex = '''zz-never-zz'''\n")
    assert scanned() == 1 and scanned() == 0


@pytest.mark.parametrize("damage", ["garbage", "other-form", "folder", "unmakeable"])
def test_a_record_that_cannot_be_used_is_a_miss_and_left_as_it_is(bench, monkeypatch, damage):
    project, tools, record = bench
    record.parent.mkdir(parents=True)
    if damage == "garbage":
        record.write_bytes(b"not a database at all " * 100)
    elif damage == "other-form":
        with sqlite3.connect(record) as connection:
            connection.execute("CREATE TABLE verdict (digest TEXT)")
    elif damage == "folder":
        record.mkdir()
    else:
        (record.parent / "file").write_text("x")
        monkeypatch.setenv("GOV_SECRETS_CACHE", str(record.parent / "file" / "record.sqlite"))
    kept = record.read_bytes() if record.is_file() else None
    clean = _write(project, "notes/clean.md", "Ordinary text.\n")
    planted = _write(project, "notes/planted.md", f"The value is {PLANTED} today.\n")
    for _ in range(2):
        before = secrets.scan_counts()["content"]
        assert secrets.indexable(project, [planted, clean]) == [clean]
        assert secrets.scan_counts()["content"] == {**before, "scanned": before["scanned"] + 2}
    assert (record.read_bytes() if record.is_file() else None) == kept


def test_a_locked_record_is_a_miss_and_does_not_stop_the_scan(bench, monkeypatch):
    project, tools, record = bench
    monkeypatch.setattr(cache, "_WAIT_S", 0.2)
    rel = _write(project, "notes/clean.md", "Ordinary text.\n")
    assert secrets.indexable(project, [rel]) == [rel]
    holder = sqlite3.connect(record, isolation_level=None)
    try:
        holder.execute("PRAGMA locking_mode=EXCLUSIVE")
        holder.execute("BEGIN EXCLUSIVE")
        holder.execute("DELETE FROM verdict WHERE kind = 'none'")
        before = secrets.scan_counts()["content"]["scanned"]
        assert secrets.indexable(project, [rel]) == [rel]
        assert secrets.scan_counts()["content"]["scanned"] == before + 1
    finally:
        holder.close()


def test_a_full_scan_reads_nothing_and_writes_fresh(bench, monkeypatch):
    project, tools, record = bench
    rel = _write(project, "notes/clean.md", "Ordinary text.\n")
    assert secrets.indexable(project, [rel]) == [rel]
    with sqlite3.connect(record) as connection:
        connection.execute("DELETE FROM verdict")
    for value, scanned in (("1", 1), ("yes", 1), ("0", 0), ("", 0)):
        monkeypatch.setenv("GOV_SECRETS_FULL_SCAN", value)
        before = secrets.scan_counts()["content"]["scanned"]
        assert secrets.indexable(project, [rel]) == [rel]
        assert secrets.scan_counts()["content"]["scanned"] - before == scanned


def test_no_record_without_a_name_under_pytest_or_an_empty_name(bench, monkeypatch):
    project, tools, record = bench
    monkeypatch.delenv("GOV_SECRETS_CACHE")
    assert "PYTEST_CURRENT_TEST" in os.environ and cache.location() is None
    monkeypatch.setenv("GOV_SECRETS_CACHE", "")
    assert cache.location() is None
    rel = _write(project, "notes/clean.md", "Ordinary text.\n")
    for _ in range(2):
        before = secrets.scan_counts()["content"]["scanned"]
        assert secrets.indexable(project, [rel]) == [rel]
        assert secrets.scan_counts()["content"]["scanned"] == before + 1
    monkeypatch.delenv("PYTEST_CURRENT_TEST")
    monkeypatch.delenv("GOV_SECRETS_CACHE")
    monkeypatch.setenv("HOME", str(record.parent))
    assert cache.location() == record.parent / ".cache" / "gov-os" / "secrets-scan.sqlite"


def test_a_scan_that_cannot_decide_raises_and_keeps_nothing(bench):
    project, tools, record = bench
    (tools / "gitleaks").write_text("#!/bin/sh\nexit 2\n")
    rel = _write(project, "notes/clean.md", "Ordinary text.\n")
    with pytest.raises(RuntimeError):
        secrets.indexable(project, [rel])
    with pytest.raises(RuntimeError):
        secrets.path_holds_secret(project, rel)
    if record.exists():
        with sqlite3.connect(record) as connection:
            assert connection.execute("SELECT count(*) FROM verdict").fetchone()[0] == 0
