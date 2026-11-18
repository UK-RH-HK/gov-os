"""Builder tests for W2-88 run 9, S27's folder mode (DEC-1183 (2)): each batch's texts written as numbered files to a
private folder outside the root, one ``gitleaks dir`` per batch and rule set, each finding on its own file.

Regression evidence only (DEC-136). Where a test judges a verdict, its oracle is the one-per-file form: ``_scan`` over
one text on standard input, as at 301708296. No secret stands whole in this file: each planted string is built from
parts, and no test prints or records a value.
"""
from __future__ import annotations

import base64
import hashlib
import json
import os
import shutil
import stat
import subprocess
import tempfile
import threading
import time
from pathlib import Path

import pytest

from gov import secrets
from gov.secrets import cache

REPO = Path(__file__).resolve().parents[3]
PLANTED = "_".join(["ARGUS", "TOKEN", "CAN" + "ARY", "4WM8"])
MAP = "namespaces:\n  everything: {paths: ['**'], memory_class: governance}\n"
PASSWORD = "".join(["Hx7", "q2Lm", "Pz9", "Rt4"])  # a basic-auth value, built from parts; never printed
WORD = "PRIVATE" + " KEY"

pytestmark = pytest.mark.skipif(shutil.which("gitleaks") is None, reason="gitleaks is not on PATH")


def _write(root: Path, rel: str, data) -> str:
    path = root / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(data if isinstance(data, bytes) else data.encode())
    return rel


def _setup(root: Path) -> Path:
    _write(root, "governance/project/path-map.yaml", MAP)
    _write(root, ".gitleaks.toml", (REPO / "template/.gitleaks.toml").read_text(encoding="utf-8"))
    return root


@pytest.fixture()
def project(tmp_path, monkeypatch):
    monkeypatch.setenv("GOV_HEAVY_THREAD_BUDGET", "1")  # one worker: a list is one batch unless a test says otherwise
    monkeypatch.delenv("GOV_SECRETS_CACHE", raising=False)
    return _setup(tmp_path / "project")


def _oracle(root: Path, rels: list[str]) -> list[str]:
    """The one-per-file form's verdict: each file's bytes judged alone by ``_scan`` on standard input."""
    rules = secrets._rules(root)
    return [rel for rel in dict.fromkeys(rels)
            if (root / rel).exists() and not secrets._scan(rules, secrets._forms((root / rel).read_bytes()), root)]


@pytest.fixture()
def calls(monkeypatch):
    """Each gitleaks run: its arguments, its folder's state while it runs, and stdin given (if any)."""
    seen = []
    real = secrets.subprocess.run

    def spy(command, **options):
        if command and command[0] == "gitleaks":
            entry = {"command": list(command), "cwd": options.get("cwd"), "input": options.get("input")}
            if options.get("cwd"):
                folder = Path(options["cwd"])
                entry["mode"] = stat.S_IMODE(folder.stat().st_mode)
                entry["names"] = sorted(os.listdir(folder))
                entry["file_modes"] = {stat.S_IMODE((folder / name).stat().st_mode) for name in entry["names"]}
                entry["bytes"] = {name: (folder / name).read_bytes() for name in entry["names"]}
            seen.append(entry)
        return real(command, **options)

    monkeypatch.setattr(secrets.subprocess, "run", spy)
    return seen


def _dir_runs(calls):
    return [entry for entry in calls if entry["command"][1] == "dir"]


# -- P1R-1's shapes (run 7's re-check): a match from one text never reaches the next ---------------------------------

CURL_A = "Check the service:\ncurl https://api.example.com/health\n"
CURL_B = (f"curl -u deploy:{PASSWORD} https://api.example.com/deploy\necho ok\n"
          "curl -u user:$PASSWORD https://api.example.com/other\n")


def _pem() -> str:
    body = base64.b64encode(os.urandom(1190)).decode()
    lines = "\n".join(body[at:at + 64] for at in range(0, len(body), 64))
    return f"-----BEGIN RSA {WORD}-----\n{lines}\n-----END RSA {WORD}-----\n"


KEY_A = f"Notes on keys.\n-----BEGIN RSA {WORD}-----\nthe value is false here\n"


@pytest.mark.parametrize("shape", ["curl", "private-key"])
def test_p1r1_pairs_in_one_batch_in_both_orders_and_in_a_long_batch(project, shape, calls):
    a_text, b_text = (CURL_A, CURL_B) if shape == "curl" else (KEY_A, _pem())
    a = _write(project, "config/a-tail.md", a_text)
    b = _write(project, "config/b-head.sh", b_text)
    assert _oracle(project, [a, b]) == [a], "the plant: B alone holds a secret, A alone none"
    clean = [_write(project, f"notes/c{number:02d}.md", f"Plain note {number}.\n") for number in range(14)]
    for order in ([a, b], [b, a], [*clean[:6], a, b, *clean[6:]], [*clean[:6], b, a, *clean[6:]]):
        calls.clear()
        got = secrets.indexable(project, order)
        assert got == _oracle(project, order) and b not in got and a in got, (shape, order)
        assert len(_dir_runs(calls)) == len(secrets._rules(project)), "the pair and the rest are one batch"


def test_a_collision_pair_identical_bytes_and_numbered_repository_names(project):
    """Two files with the same bytes, and repository files named like the folder's numbers, in either order."""
    one = _write(project, "0", f"value {PLANTED} here\n")
    two = _write(project, "1", "Plain words.\n")
    same_a = _write(project, "dup/a.md", f"value {PLANTED} here\n")
    same_b = _write(project, "dup/b.md", f"value {PLANTED} here\n")
    clean_a = _write(project, "dup/c.md", "Plain words.\n")
    for order in ([one, two, same_a, same_b, clean_a], [clean_a, same_b, two, same_a, one]):
        assert secrets.indexable(project, order) == _oracle(project, order) == [rel for rel in order if rel in (two, clean_a)]


def test_names_with_a_space_and_a_newline_never_reach_gitleaks(project, calls):
    spaced = _write(project, "notes/a name with spaces.md", f"value {PLANTED}\n")
    clean = _write(project, "notes/clean name with spaces.md", "Plain words.\n")
    broken = _write(project, "notes/line\nbreak.md", "Plain words.\n")
    got = secrets.indexable(project, [spaced, clean, broken])
    assert got == _oracle(project, [spaced, clean]) == [clean]  # a newline matches no namespace, as at 301708296
    assert _dir_runs(calls)
    for entry in _dir_runs(calls):
        assert entry["command"][2] == "." and all(name.isdigit() for name in entry["names"])
        assert not any(part in arg for arg in entry["command"] for part in ("name with", "line\n", "notes"))


# -- the folder ------------------------------------------------------------------------------------------------------

def test_the_folder_is_private_outside_the_root_numbered_and_removed(project, calls):
    rels = [_write(project, f"notes/n{number}.md", f"Plain {number}.\n") for number in range(5)]
    assert secrets.indexable(project, rels) == rels
    runs = _dir_runs(calls)
    assert runs
    for entry in runs:
        folder = Path(entry["cwd"])
        assert entry["mode"] == 0o700 and entry["file_modes"] == {0o600}
        assert entry["names"] == [str(number) for number in range(len(entry["names"]))]
        assert project.resolve() not in folder.resolve().parents
        assert not folder.exists()


def test_each_file_holds_exactly_the_one_per_file_forms_standard_input(project, calls):
    texts = {"plain": b"Plain words.\n", "utf16": "Value here\n".encode("utf-16-le"),
             "large": ("filler line of a large file\n" * 4_000).encode() + b"-----BEGIN x-----\nk\n-----END x-----\n",
             "blank": b"a\n\n\nb\n", "empty": b""}
    rels = [_write(project, f"notes/{name}.md", data) for name, data in texts.items()]
    secrets.indexable(project, rels)
    files = _dir_runs(calls)[0]["bytes"]
    rules = secrets._rules(project)
    for number, data in enumerate(texts.values()):
        calls.clear()
        secrets._scan(rules[:1], secrets._forms(data))
        assert files[str(number)] == calls[0]["input"]


def test_a_temporary_folder_inside_the_root_is_refused_and_nothing_written_there(project, monkeypatch):
    inside = project / "tmp-inside"
    inside.mkdir()
    rels = [_write(project, "notes/a.md", "Plain.\n")]
    monkeypatch.setattr(tempfile, "tempdir", str(inside))
    with pytest.raises(RuntimeError, match="tmp-inside"):
        secrets.indexable(project, rels)
    assert list(inside.iterdir()) == []


def test_a_temporary_folder_whose_path_meets_the_default_path_allowlist_still_finds_the_secret(project, tmp_path,
                                                                                               monkeypatch):
    """gitleaks' default allowlist drops every finding under a path holding node_modules/ or venv/lib (probe p1):
    gitleaks runs in the folder on ``.``, so the path it matches is the number alone."""
    for name in ("node_modules", "venv/lib", "gitleaks.toml.d"):
        where = tmp_path / "outside" / name
        where.mkdir(parents=True)
        monkeypatch.setattr(tempfile, "tempdir", str(where))
        rels = [_write(project, "notes/a.md", f"value {PLANTED}\n"), _write(project, "notes/b.md", "Plain.\n")]
        assert secrets.indexable(project, rels) == ["notes/b.md"], name


def test_any_other_entry_in_the_folder_refuses_the_batch(project, monkeypatch):
    """gitleaks dir reads a .gitleaksignore found in the folder even with --gitleaks-ignore-path /dev/null (probe p3)."""
    real = tempfile.mkdtemp

    def planted(*args, **named):
        made = real(*args, **named)
        Path(made, ".gitleaksignore").write_text("0:gov-canary:2\n")
        return made

    monkeypatch.setattr(secrets.tempfile, "mkdtemp", planted)
    with pytest.raises(RuntimeError):
        secrets.indexable(project, [_write(project, "notes/a.md", f"value {PLANTED}\n")])


# -- fail closed (interface item 7) ----------------------------------------------------------------------------------

def _stand_in(monkeypatch, answer, when=lambda folder: True):
    """gitleaks dir answered by ``answer(folder)`` (a CompletedProcess) where ``when(folder)``; else the real one."""
    real = secrets.subprocess.run
    folders = []

    def run(command, **options):
        if command and command[0] == "gitleaks" and command[1] == "dir":
            folders.append(Path(options["cwd"]))
            if when(Path(options["cwd"])):
                return answer(Path(options["cwd"]), command, options)
        return real(command, **options)

    monkeypatch.setattr(secrets.subprocess, "run", run)
    return folders


def _done(code, stdout):
    return lambda folder, command, options: subprocess.CompletedProcess(command, code, stdout, b"")


@pytest.fixture()
def record(monkeypatch, tmp_path):
    monkeypatch.setenv("GOV_SECRETS_CACHE", str(tmp_path / "cache.sqlite"))


def _remembered(root, rel):
    rules = secrets._rules(root)
    digest = hashlib.sha256((root / rel).read_bytes()).hexdigest()
    return cache.remembered("content", digest, cache.engine(rules, secrets._FORM))


def test_a_stand_in_failing_inside_one_batch_raises_and_that_batch_is_not_remembered(project, monkeypatch, record):
    monkeypatch.setattr(secrets, "_BATCH_TEXTS", 3)
    monkeypatch.setenv("GOV_HEAVY_THREAD_BUDGET", "1")
    rels = [_write(project, f"notes/n{number}.md", f"Plain {number}{' FAILHERE' if number == 4 else ''}.\n")
            for number in range(9)]
    folders = _stand_in(monkeypatch, _done(1, b""), when=lambda folder: any(
        b"FAILHERE" in path.read_bytes() for path in folder.iterdir()))
    with pytest.raises(RuntimeError):
        secrets.indexable(project, rels)
    assert not any(_remembered(project, rel) for rel in rels[3:6])
    assert folders and not any(folder.exists() for folder in folders)


@pytest.mark.parametrize("stdout", [b"not json", b"{}", json.dumps([{"File": "99", "RuleID": "x"}]).encode(),
                                    json.dumps([{"File": "../0", "RuleID": "x"}]).encode(), json.dumps(["x"]).encode()],
                         ids=["unreadable", "no-list", "a-file-not-in-the-folder", "another-spelling", "not-a-finding"])
def test_exit_3_with_a_report_that_cannot_be_placed_holds_every_text_of_the_batch(project, monkeypatch, record, stdout):
    rels = [_write(project, f"notes/n{number}.md", f"Plain {number}.\n") for number in range(4)]
    folders = _stand_in(monkeypatch, _done(3, stdout))
    assert secrets.indexable(project, rels) == []
    assert not any(_remembered(project, rel) for rel in rels)
    assert folders and not any(folder.exists() for folder in folders)


@pytest.mark.parametrize("code, stdout", [(0, json.dumps([{"File": "0", "RuleID": "x"}]).encode()), (0, b"junk"),
                                          (3, b"[]\n"), (1, b"[]\n"), (2, b"")],
                         ids=["exit-0-with-a-finding", "exit-0-unreadable", "exit-3-no-finding", "exit-1", "exit-2"])
def test_a_run_that_does_not_decide_raises_and_nothing_is_remembered(project, monkeypatch, record, code, stdout):
    rels = [_write(project, f"notes/n{number}.md", f"Plain {number}.\n") for number in range(3)]
    folders = _stand_in(monkeypatch, _done(code, stdout))
    with pytest.raises(RuntimeError):
        secrets.indexable(project, rels)
    assert not any(_remembered(project, rel) for rel in rels)
    assert folders and not any(folder.exists() for folder in folders)


def test_a_time_out_raises_and_removes_the_folder(project, monkeypatch, record):
    def late(folder, command, options):
        raise subprocess.TimeoutExpired(command, options["timeout"])

    folders = _stand_in(monkeypatch, late)
    with pytest.raises(RuntimeError):
        secrets.indexable(project, [_write(project, "notes/a.md", "Plain.\n")])
    assert folders and not any(folder.exists() for folder in folders)
    assert not _remembered(project, "notes/a.md")


def test_no_gitleaks_on_path_raises(project, monkeypatch):
    monkeypatch.setenv("PATH", str(project / "no-such-folder"))
    with pytest.raises(RuntimeError):
        secrets.indexable(project, [_write(project, "notes/a.md", "Plain.\n")])


def test_a_finding_on_one_file_holds_that_text_alone(project, monkeypatch):
    rels = [_write(project, f"notes/n{number}.md", f"Plain {number}.\n") for number in range(4)]
    _stand_in(monkeypatch, _done(3, json.dumps([{"File": "2", "RuleID": "x", "Secret": "y"}]).encode()))
    assert secrets.indexable(project, rels) == [rels[0], rels[1], rels[3]]


# -- batches, width, record ------------------------------------------------------------------------------------------

def test_one_gitleaks_dir_per_batch_and_rule_set_and_no_stdin(project, monkeypatch, calls):
    monkeypatch.setattr(secrets, "_BATCH_TEXTS", 4)
    monkeypatch.setenv("GOV_HEAVY_THREAD_BUDGET", "1")
    rels = [_write(project, f"notes/n{number:02d}.md", f"Plain {number}.\n") for number in range(10)]
    assert secrets.indexable(project, rels) == rels
    runs = _dir_runs(calls)
    assert len(runs) == 3 * len(secrets._rules(project)) and all(entry["input"] is None for entry in calls)
    assert sorted(len(entry["names"]) for entry in runs[::len(secrets._rules(project))]) == [2, 4, 4]


def test_one_text_over_the_byte_cap_is_a_batch_of_its_own(project, monkeypatch, calls):
    monkeypatch.setattr(secrets, "_BATCH_BYTES", 1_000)
    monkeypatch.setenv("GOV_HEAVY_THREAD_BUDGET", "1")
    rels = [_write(project, "notes/a.md", "Plain.\n"), _write(project, "notes/big.md", "word " * 400),
            _write(project, "notes/b.md", "Plain.\n")]
    assert secrets.indexable(project, rels) == rels
    sizes = [len(entry["names"]) for entry in _dir_runs(calls)[::len(secrets._rules(project))]]
    assert sizes == [1, 1, 1]


def test_at_most_the_workers_run_at_once(project, monkeypatch):
    monkeypatch.setattr(secrets, "_BATCH_TEXTS", 2)
    monkeypatch.setenv("GOV_HEAVY_THREAD_BUDGET", "2")
    rels = [_write(project, f"notes/n{number:02d}.md", f"Plain {number}.\n") for number in range(16)]
    real, lock, state = secrets.subprocess.run, threading.Lock(), {"now": 0, "most": 0}

    def run(command, **options):
        if command[0] == "gitleaks":
            with lock:
                state["now"] += 1
                state["most"] = max(state["most"], state["now"])
            try:
                time.sleep(0.05)
                return real(command, **options)
            finally:
                with lock:
                    state["now"] -= 1
        return real(command, **options)

    monkeypatch.setattr(secrets.subprocess, "run", run)
    assert secrets.indexable(project, rels) == rels
    assert 1 < state["most"] <= min(2, secrets._workers())


def test_counts_and_the_record_of_clean_results(project, record, calls):
    rels = [_write(project, f"notes/n{number}.md", f"Plain {number}.\n") for number in range(6)]
    rels.append(_write(project, "notes/held.md", f"value {PLANTED}\n"))
    before = secrets.scan_counts()["content"]
    assert secrets.indexable(project, rels) == rels[:6]
    middle = secrets.scan_counts()["content"]
    assert middle["scanned"] - before["scanned"] == 7 and middle["remembered"] == before["remembered"]
    calls.clear()
    assert secrets.indexable(project, rels) == rels[:6]
    after = secrets.scan_counts()["content"]
    assert after["remembered"] - middle["remembered"] == 6 and after["scanned"] - middle["scanned"] == 1
    assert all(entry["names"] == ["0"] for entry in _dir_runs(calls))  # the finding's file alone, scanned again


def test_form_7_and_a_form_6_record_is_not_reused(project, record):
    rel = _write(project, "notes/held.md", f"value {PLANTED}\n")
    rules = secrets._rules(project)
    digest = hashlib.sha256((project / rel).read_bytes()).hexdigest()
    cache.remember("content", digest, cache.engine(rules, 6))
    assert secrets._FORM == 7 and secrets.indexable(project, [rel]) == []


def test_a_large_file_with_secrets_across_read_edges_is_judged_as_one_per_file(project):
    """Planted across 100,000-byte multiples of the folder's file and near the pieces' edges (probe p2 ran 523)."""
    filler = "filler line of a large file\n"
    rels = []
    for number, at in enumerate((99_990, 199_985, secrets._PIECE - 9, 3 * secrets._PIECE + 3, 300_000)):
        head = (filler * (at // len(filler) + 1))[:at]
        rels.append(_write(project, f"big/b{number}.txt", head + f"value {PLANTED} end\n" + filler * 4_000))
    rels.append(_write(project, "big/clean.txt", filler * 15_000))
    rels.append(_write(project, "big/blob.txt", ("Aq" * 37 + "/") * 5_000 + PLANTED + "/" + ("Aq" * 37 + "/") * 3_000))
    got = secrets.indexable(project, rels)
    assert got == _oracle(project, rels) == ["big/clean.txt"]


def test_order_asked_repeats_missing_and_links(project):
    rels = [_write(project, f"notes/n{number}.md", f"Plain {number}{' ' + PLANTED if number == 2 else ''}.\n")
            for number in range(5)]
    (project / "notes" / "to-secret.md").symlink_to("n2.md")
    (project / "notes" / "to-clean.md").symlink_to("n1.md")
    asked = [*reversed(rels), rels[0], "notes/missing.md", "notes/to-secret.md", "notes/to-clean.md", "/etc/hostname"]
    got = secrets.indexable(project, asked)
    assert got == ["notes/n4.md", "notes/n3.md", "notes/n1.md", "notes/n0.md", "notes/to-clean.md"]


def test_no_code_path_joins_two_texts_into_one_gitleaks_input():
    source = (REPO / "src/gov/secrets/__init__.py").read_text(encoding="utf-8")
    assess = (REPO / "src/gov/adopt/assess.py").read_text(encoding="utf-8")
    scan_class = assess.split("class _Scan", 1)[1].split("\ndef ", 1)[0]
    assert '"stdin"' not in assess and "subprocess" not in scan_class and "_Folder" in scan_class
    indexable = source.split("def indexable", 1)[1].split("\ndef ", 1)[0]
    assert "_scan(" not in indexable and "_holds_secret(" not in indexable
