"""Builder tests for the secrets scan's size-aware limit, its pool and its reuse of clean results (W2-50, DEC-853).

Regression evidence only (DEC-136). They cover what the acceptance tests leave to the builder: the limit
of each gitleaks run grows with what it reads, the largest store is judged first, the record of clean
results is written whole and trusted only whole, its own file is scanned like any store without being
taken for a secret, and a run that does not finish records nothing.
No secret stands whole in this file: the planted string is built from parts.
"""
from __future__ import annotations

import hashlib
import json
import shutil
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO / "src"))

from gov import secrets  # noqa: E402

PLANTED = "_".join(["ARGUS", "TOKEN", "CAN" + "ARY", "4WM8"])

pytestmark = pytest.mark.skipif(shutil.which("gitleaks") is None, reason="gitleaks is not on PATH")


def _write(root, rel, data):
    path = root / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(data if isinstance(data, bytes) else data.encode())
    return rel


@pytest.fixture()
def project(tmp_path):
    _write(tmp_path, ".gitleaks.toml", (REPO / "template/.gitleaks.toml").read_text(encoding="utf-8"))
    return tmp_path


@pytest.fixture()
def scanned(monkeypatch):
    """The contents given to gitleaks, in the order they were judged: of a file that is no store, its bytes."""
    seen = []
    real = secrets._scan
    monkeypatch.setattr(secrets, "_scan", lambda rules, chunks: seen.append(chunks[0]) or real(rules, chunks))
    return seen


def _digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _reuse_lines(err, rel):
    return [line for line in err.splitlines() if "reused" in line and rel in line]


def test_the_limit_of_each_gitleaks_run_grows_with_what_it_reads(project, monkeypatch):
    limits = []
    run = secrets.subprocess.run
    monkeypatch.setattr(secrets.subprocess, "run", lambda command, **options: limits.append(
        (len(options["input"]), options["timeout"])) or run(command, **options))
    rules = secrets._rules(project)
    assert secrets._holds_secret(rules, b"x\n" * 3_000_000) is False
    assert secrets._holds_secret(rules, b"short\0text\n") is False  # UTF-16: the zero-free copy counts too
    assert [limit for _, limit in limits] == [60 + size / 1_000_000 for size, _ in limits]
    # in pieces, a blank line after each (DEC-897): the first input is longer than the content by the overlaps
    assert limits[0][0] == 1 + sum(len(piece) + 2 for piece in secrets._pieces(b"x\n" * 3_000_000)) > 6_000_001
    assert limits[-1][0] == len(b"\nshort\0text\n\n\nshorttext\n\n\n")


def test_an_unchanged_clean_store_is_reused_and_labelled_a_changed_one_scanned(project, scanned, capsys):
    store = _write(project, ".gov-runtime/index/rows.txt", "Ordinary rows.\n")
    other = _write(project, ".gov-runtime/codeintel/code.txt", "Ordinary code.\n")
    assert secrets.stores_with_secrets(project) == []
    assert capsys.readouterr().err == ""  # a scanned store carries no label
    record = project / secrets.RECORD_REL
    assert record.is_file() and len(scanned) == 2
    scanned.clear()
    _write(project, other, "Ordinary code, changed.\n")
    assert secrets.stores_with_secrets(project) == []
    err = capsys.readouterr().err
    assert _reuse_lines(err, store) == [f"secrets-indexing: clean result reused, not scanned again: {store} "
                                        f"sha256 {_digest(project / store)}"]
    assert not _reuse_lines(err, other)
    # the changed store and the record itself are scanned, by the real gitleaks, and the record is no secret
    assert len(scanned) == 2 and (project / other).read_bytes() in scanned
    assert any(each.startswith(b'{"form"') for each in scanned)


def test_a_finding_is_never_recorded_and_is_found_on_every_run(project, scanned):
    planted = _write(project, ".gov-runtime/index/planted.md", f"The value is {PLANTED} today.\n")
    for _ in range(3):
        assert secrets.stores_with_secrets(project) == [planted]
    assert sum(each == (project / planted).read_bytes() for each in scanned) == 3
    assert _digest(project / planted) not in json.loads((project / secrets.RECORD_REL).read_text())["clean"]


@pytest.mark.parametrize("damage", ["missing", "garbage", "truncated", "edited", "other-form", "other-rules"])
def test_a_record_that_is_not_whole_and_current_is_not_trusted(project, scanned, capsys, damage):
    store = _write(project, ".gov-runtime/index/rows.txt", "Ordinary rows.\n")
    secrets.stores_with_secrets(project)
    record = project / secrets.RECORD_REL
    text = record.read_text()
    body = json.loads(text)
    if damage == "missing":
        record.unlink()
    elif damage == "garbage":
        record.write_bytes(b"\x00\xff not a record")
    elif damage == "truncated":
        record.write_text(text[: len(text) // 2])
    elif damage == "edited":  # a digest changed to one of another store, the record's own check left as it was
        body["clean"].append(hashlib.sha256(b"another store").hexdigest())
        record.write_text(json.dumps(body))
    elif damage == "other-form":
        record.write_text(text.replace(f'"form": {secrets._FORM}', f'"form": {secrets._FORM - 1}'))
    else:
        config = project / ".gitleaks.toml"
        config.write_text(config.read_text() + "\n[[rules]]\nid = 'w2-50-unit'\nregex = '''never-in-a-store-zq'''\n")
    capsys.readouterr()
    scanned.clear()
    assert secrets.stores_with_secrets(project) == []
    assert not _reuse_lines(capsys.readouterr().err, store)
    assert (project / store).read_bytes() in scanned


def test_a_run_that_does_not_finish_records_nothing(project, monkeypatch):
    _write(project, ".gov-runtime/index/rows.txt", "Ordinary rows.\n")
    secrets.stores_with_secrets(project)
    record = project / secrets.RECORD_REL
    before = record.read_bytes()
    _write(project, ".gov-runtime/index/new.txt", "Ordinary new rows.\n")
    run = secrets.subprocess.run

    def timing_out(command, **options):
        raise secrets.subprocess.TimeoutExpired(command, options["timeout"])

    monkeypatch.setattr(secrets.subprocess, "run", timing_out)
    with pytest.raises(secrets.subprocess.TimeoutExpired):
        secrets.stores_with_secrets(project)
    assert record.read_bytes() == before
    assert sorted(path.name for path in record.parent.iterdir()) == ["index", "secrets-clean.json"]
    monkeypatch.setattr(secrets.subprocess, "run", run)


def test_no_gitleaks_on_path_raises_and_records_nothing(project, monkeypatch):
    _write(project, ".gov-runtime/index/rows.txt", "Ordinary rows.\n")
    monkeypatch.setenv("PATH", str(project / "no-such-folder"))
    with pytest.raises(OSError):
        secrets.stores_with_secrets(project)
    assert not (project / secrets.RECORD_REL).exists()


def test_the_largest_store_is_judged_first_and_the_result_keeps_the_path_order(project, scanned, monkeypatch):
    monkeypatch.setattr(secrets.os, "cpu_count", lambda: 1)
    small = _write(project, ".gov-runtime/a/small.md", f"The value is {PLANTED} today.\n")
    large = _write(project, ".gov-runtime/z/large.md", "Ordinary text.\n" * 1000 + f"The value is {PLANTED}.\n")
    middle = _write(project, ".gov-runtime/m/middle.md", "Ordinary text.\n" * 100)
    assert secrets.stores_with_secrets(project) == [small, large]
    assert scanned == [(project / rel).read_bytes() for rel in (large, middle, small)]
